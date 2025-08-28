# Copyright 2018 The Abseil Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Unittests for cpp_flags library."""

import copy
import os
import subprocess
import sys

from absl import flags
from absl.flags import _cpp_flags
from absl.flags import _exceptions
from absl.flags.tests.python import cpp_flags_test_helper
from absl.testing import _bazelize_command
from absl.testing import absltest
from absl.testing import parameterized

from google3.base.python.clif import cpp_flag

FLAGS = flags.FLAGS

# Define a dummy python flag
flags.DEFINE_integer('dummy', None, 'Dummy flag.')

PYFLAG_DEFAULT_OVERRIDES_CPP = flags.DEFINE_integer(
    'pyflag_default_overrides_cpp', 1, 'Pre C++ flag.', allow_override_cpp=True)

# We need assert here (before absltest.main and InitGoogle) to ensure the test
# (not the code) correctness.
assert int(cpp_flag.Get('pyflag_default_overrides_cpp')) == 0, (
    'Ensure C++ default != Python default')

flags.DEFINE_integer(
    'pyflag_value_overrides_cpp', 2, 'Pre C++ flag.', allow_override_cpp=True)
# We pull the C++ default for the future ref.
pyflag_value_overrides_cpp_default = int(
    cpp_flag.Get('pyflag_value_overrides_cpp'))
assert pyflag_value_overrides_cpp_default == 0, (
    'Ensure C++ default != Python default')
FLAGS['pyflag_value_overrides_cpp'].value = 1

# we pull the C++ default and replace it with a different python args value.
# we will later check that the value makes it through flag parsing to both
# the Python and C++ layers.
new_pure_cpp_flag_value = int(cpp_flag.Get('pure_cpp_flag')) + 2
assert new_pure_cpp_flag_value == 2, new_pure_cpp_flag_value

undefined_cpp_flag_exception = None
invalid_cpp_flag_exception = None

# Used by test_main_module_key_flag_with_allow_override_cpp.
flags.declare_key_flag('log_dir')


class CppFlagsUnitTest(parameterized.TestCase):
  """Unit tests for the cpp_flags module."""

  @parameterized.parameters(
      ('true', True),
      ('True', True),
      ('TRUE', True),
      ('t', True),
      ('T', True),
      ('1', True),
      ('false', False),
      ('False', False),
      ('FALSE', False),
      ('f', False),
      ('F', False),
      ('0', False),
  )
  def test_cpp_flag_parse_bool(self, text, expected_value):
    self.assertIsInstance(FLAGS.cpp_bool_default_false, bool)
    self.assertFalse(FLAGS.cpp_bool_default_false)
    try:
      FLAGS(['', f'--cpp_bool_default_false={text}'])
      self.assertEqual(FLAGS.cpp_bool_default_false, expected_value)
    finally:
      FLAGS.cpp_bool_default_false = False

  # Some of the values are valid in C++ flags library, but not Python.
  @parameterized.parameters('yes', 'n', 'haha')
  def test_cpp_flag_parse_invalid_bool(self, text):
    with self.assertRaises(flags.IllegalFlagValueError):
      FLAGS(['', f'--cpp_bool_default_false={text}'])

  @parameterized.parameters(
      ('10', 10),
      ('0o10', 8),
      ('0x10', 16),
  )
  def test_cpp_flag_parse_int(self, text, expected_value):
    flags_to_test = [
        'cpp_int32',
        'cpp_int64',
        'cpp_uint64',
        'cpp_new_int32',
        'cpp_new_int64',
        'cpp_new_uint64',
    ]
    for flagname in flags_to_test:
      old_value = getattr(FLAGS, flagname)
      try:
        FLAGS(['', f'--{flagname}={text}'])
        self.assertEqual(getattr(FLAGS, flagname), expected_value)
      finally:
        setattr(FLAGS, flagname, old_value)

  @parameterized.parameters(
      ('cpp_int32', '2147483647', 2**31 - 1),
      ('cpp_new_int32', '2147483647', 2**31 - 1),
      ('cpp_int32', '-2147483648', -2**31),
      ('cpp_new_int32', '-2147483648', -2**31),
      ('cpp_int64', '9223372036854775807', 2**63 - 1),
      ('cpp_new_int64', '9223372036854775807', 2**63 - 1),
      ('cpp_int64', '-9223372036854775808', -2**63),
      ('cpp_new_int64', '-9223372036854775808', -2**63),
      ('cpp_uint64', '18446744073709551615', 2**64 - 1),
      ('cpp_new_uint64', '18446744073709551615', 2**64 - 1),
  )
  def test_cpp_flag_parse_int_max(self, flagname, text, expected_value):
    old_value = getattr(FLAGS, flagname)
    try:
      FLAGS(['', f'--{flagname}={text}'])
      self.assertEqual(getattr(FLAGS, flagname), expected_value)
    finally:
      setattr(FLAGS, flagname, old_value)

  @parameterized.parameters(
      ('cpp_int32', '2147483648'),
      ('cpp_new_int32', '2147483648'),
      ('cpp_int32', '-2147483649'),
      ('cpp_new_int32', '-2147483649'),
      ('cpp_int64', '9223372036854775808'),
      ('cpp_new_int64', '9223372036854775808'),
      ('cpp_int64', '-9223372036854775809'),
      ('cpp_new_int64', '-9223372036854775809'),
      ('cpp_int64', '18446744073709551616'),
      ('cpp_new_int64', '18446744073709551616'),
      ('cpp_uint64', '-1'),
      ('cpp_new_uint64', '-1'),
  )
  def test_cpp_flag_integer_overflows(self, flagname, text):
    with self.assertRaises(ValueError):
      FLAGS(['', f'--{flagname}={text}'])

  def test_cpp_flag_bool(self):
    self.assertIsInstance(FLAGS.cpp_bool_default_false, bool)
    self.assertFalse(FLAGS.cpp_bool_default_false)
    try:
      FLAGS.cpp_bool_default_false = True
      self.assertIsInstance(FLAGS.cpp_bool_default_false, bool)
      self.assertTrue(FLAGS.cpp_bool_default_false)
      self.assertEqual(cpp_flag.Get('cpp_bool_default_false'), 'true')

      cpp_flags_test_helper.update_cpp_bool_default_false(False)
      self.assertFalse(FLAGS.cpp_bool_default_false)
      self.assertEqual(cpp_flag.Get('cpp_bool_default_false'), 'false')

      with self.assertRaises(ValueError):
        FLAGS.cpp_bool_default_false = None
    finally:
      FLAGS.cpp_bool_default_false = False

    self.assertIsInstance(FLAGS.cpp_bool_default_true, bool)
    self.assertTrue(FLAGS.cpp_bool_default_true)
    try:
      FLAGS.cpp_bool_default_true = False
      self.assertIsInstance(FLAGS.cpp_bool_default_true, bool)
      self.assertFalse(FLAGS.cpp_bool_default_true)
      self.assertEqual(cpp_flag.Get('cpp_bool_default_true'), 'false')

      cpp_flags_test_helper.update_cpp_bool_default_true(True)
      self.assertTrue(FLAGS.cpp_bool_default_true)
      self.assertEqual(cpp_flag.Get('cpp_bool_default_true'), 'true')

      with self.assertRaises(ValueError):
        FLAGS.cpp_bool_default_true = None
    finally:
      FLAGS.cpp_bool_default_true = True

  def test_cpp_flag_int32(self):
    self.assertEqual(FLAGS.cpp_int32, 32)
    try:
      FLAGS.cpp_int32 = 64
      self.assertEqual(FLAGS.cpp_int32, 64)
      self.assertEqual(cpp_flag.Get('cpp_int32'), '64')

      cpp_flags_test_helper.update_cpp_int32(128)
      self.assertEqual(FLAGS.cpp_int32, 128)
      self.assertEqual(cpp_flag.Get('cpp_int32'), '128')

      with self.assertRaises(ValueError):
        FLAGS.cpp_int32 = None
    finally:
      FLAGS.cpp_int32 = 32

  def test_cpp_flag_int64(self):
    self.assertEqual(FLAGS.cpp_int64, 64)
    try:
      FLAGS.cpp_int64 = 128
      self.assertEqual(FLAGS.cpp_int64, 128)
      self.assertEqual(cpp_flag.Get('cpp_int64'), '128')

      cpp_flags_test_helper.update_cpp_int64(256)
      self.assertEqual(FLAGS.cpp_int64, 256)
      self.assertEqual(cpp_flag.Get('cpp_int64'), '256')

      with self.assertRaises(ValueError):
        FLAGS.cpp_int64 = None
    finally:
      FLAGS.cpp_int64 = 128

  def test_cpp_flag_uint64(self):
    self.assertEqual(FLAGS.cpp_uint64, 128)
    try:
      FLAGS.cpp_uint64 = 256
      self.assertEqual(FLAGS.cpp_uint64, 256)
      self.assertEqual(cpp_flag.Get('cpp_uint64'), '256')

      cpp_flags_test_helper.update_cpp_uint64(512)
      self.assertEqual(FLAGS.cpp_uint64, 512)
      self.assertEqual(cpp_flag.Get('cpp_uint64'), '512')

      with self.assertRaises(ValueError):
        FLAGS.cpp_uint64 = None
    finally:
      FLAGS.cpp_uint64 = 256

  def test_cpp_flag_double(self):
    self.assertEqual(FLAGS.cpp_double, 1.5)
    try:
      FLAGS.cpp_double = 2.5
      self.assertEqual(FLAGS.cpp_double, 2.5)
      self.assertEqual(cpp_flag.Get('cpp_double'), '2.5')

      FLAGS.cpp_double = 3
      self.assertEqual(FLAGS.cpp_double, 3)
      self.assertEqual(cpp_flag.Get('cpp_double'), '3')

      cpp_flags_test_helper.update_cpp_double(3.5)
      self.assertEqual(FLAGS.cpp_double, 3.5)
      self.assertEqual(cpp_flag.Get('cpp_double'), '3.5')

      with self.assertRaises(ValueError):
        FLAGS.cpp_double = None
    finally:
      FLAGS.cpp_double = 1.5

  def test_cpp_flag_parse_double(self):
    self.assertEqual(FLAGS.cpp_double, 1.5)
    try:
      FLAGS['cpp_double'].parse('2.5')
      self.assertEqual(FLAGS.cpp_double, 2.5)
      self.assertEqual(cpp_flag.Get('cpp_double'), '2.5')
    finally:
      FLAGS.cpp_double = 1.5

  def test_cpp_flag_string(self):
    self.assertEqual(FLAGS.cpp_string, 'string')
    try:
      FLAGS.cpp_string = 'else'
      self.assertEqual(FLAGS.cpp_string, 'else')
      self.assertEqual(cpp_flag.Get('cpp_string'), 'else')

      cpp_flags_test_helper.update_cpp_string('different')
      self.assertEqual(FLAGS.cpp_string, 'different')
      self.assertEqual(cpp_flag.Get('cpp_string'), 'different')

      with self.assertRaises(ValueError):
        FLAGS.cpp_string = None
    finally:
      FLAGS.cpp_string = 'string'

  def test_cpp_flag_string_unicode(self):
    self.assertEqual(FLAGS.cpp_string, 'string')
    try:
      FLAGS.cpp_string = 'Ещё'
      self.assertEqual(FLAGS.cpp_string, 'Ещё')
      self.assertEqual(cpp_flag.Get('cpp_string'), 'Ещё')
    finally:
      FLAGS.cpp_string = 'string'

  def test_cpp_flag_string_parse_unicode(self):
    self.assertEqual(FLAGS.cpp_string, 'string')
    try:
      FLAGS['cpp_string'].parse('Ещё')
      self.assertEqual(FLAGS.cpp_string, 'Ещё')
      self.assertEqual(cpp_flag.Get('cpp_string'), 'Ещё')
    finally:
      FLAGS.cpp_string = 'string'

  def test_cpp_flag_new_bool_parse_pytrue(self):
    self.assertEqual('bool', cpp_flag.GetFlagTypeName('cpp_new_bool'))
    self.assertEqual(FLAGS.cpp_new_bool, False)
    try:
      FLAGS(['', '--cpp_new_bool=True'])
      self.assertEqual(FLAGS.cpp_new_bool, True)
    finally:
      FLAGS.cpp_new_bool = False

  def test_cpp_flag_new_bool(self):
    self.assertEqual('bool', cpp_flag.GetFlagTypeName('cpp_new_bool'))
    self.assertEqual(FLAGS.cpp_new_bool, False)
    try:
      FLAGS.cpp_new_bool = True
      self.assertIsInstance(FLAGS.cpp_new_bool, bool)
      self.assertEqual(FLAGS.cpp_new_bool, True)
      self.assertEqual(cpp_flag.Get('cpp_new_bool'), 'true')

      FLAGS.cpp_new_bool = 'false'
      self.assertIsInstance(FLAGS.cpp_new_bool, bool)
      self.assertEqual(FLAGS.cpp_new_bool, False)
      self.assertEqual(cpp_flag.Get('cpp_new_bool'), 'false')

      cpp_flags_test_helper.update_cpp_new_bool(True)
      self.assertIsInstance(FLAGS.cpp_new_bool, bool)
      self.assertEqual(FLAGS.cpp_new_bool, True)
      self.assertEqual(cpp_flag.Get('cpp_new_bool'), 'true')

      with self.assertRaises(ValueError):
        FLAGS.cpp_new_bool = None
    finally:
      FLAGS.cpp_new_bool = False

  def test_cpp_flag_new_int32(self):
    self.assertEqual('int32', cpp_flag.GetFlagTypeName('cpp_new_int32'))
    self.assertEqual(FLAGS.cpp_new_int32, 32)
    try:
      FLAGS.cpp_new_int32 = 64
      self.assertEqual(FLAGS.cpp_new_int32, 64)
      self.assertEqual(cpp_flag.Get('cpp_new_int32'), '64')

      FLAGS.cpp_new_int32 = '128'
      self.assertEqual(FLAGS.cpp_new_int32, 128)
      self.assertEqual(cpp_flag.Get('cpp_new_int32'), '128')

      cpp_flags_test_helper.update_cpp_new_int32(-2**24)
      self.assertEqual(FLAGS.cpp_new_int32, -16777216)
      self.assertEqual(cpp_flag.Get('cpp_new_int32'), '-16777216')

      with self.assertRaises(ValueError):
        FLAGS.cpp_new_int32 = None
    finally:
      FLAGS.cpp_new_int32 = 32

  def test_cpp_flag_new_int64(self):
    self.assertEqual('int64', cpp_flag.GetFlagTypeName('cpp_new_int64'))
    self.assertEqual(FLAGS.cpp_new_int64, 64)
    try:
      FLAGS.cpp_new_int64 = 128
      self.assertEqual(FLAGS.cpp_new_int64, 128)
      self.assertEqual(cpp_flag.Get('cpp_new_int64'), '128')

      FLAGS.cpp_new_int64 = '256'
      self.assertEqual(FLAGS.cpp_new_int64, 256)
      self.assertEqual(cpp_flag.Get('cpp_new_int64'), '256')

      cpp_flags_test_helper.update_cpp_new_int64(-2**36)
      self.assertEqual(FLAGS.cpp_new_int64, -68719476736)
      self.assertEqual(cpp_flag.Get('cpp_new_int64'), '-68719476736')

      with self.assertRaises(ValueError):
        FLAGS.cpp_new_int64 = None
    finally:
      FLAGS.cpp_new_int64 = 64

  def test_cpp_flag_new_uint64(self):
    self.assertEqual('uint64', cpp_flag.GetFlagTypeName('cpp_new_uint64'))
    self.assertEqual(FLAGS.cpp_new_uint64, 128)
    try:
      FLAGS.cpp_new_uint64 = 256
      self.assertEqual(FLAGS.cpp_new_uint64, 256)
      self.assertEqual(cpp_flag.Get('cpp_new_uint64'), '256')

      FLAGS.cpp_new_uint64 = '512'
      self.assertEqual(FLAGS.cpp_new_uint64, 512)
      self.assertEqual(cpp_flag.Get('cpp_new_uint64'), '512')

      cpp_flags_test_helper.update_cpp_new_uint64(2**36)
      self.assertEqual(FLAGS.cpp_new_uint64, 68719476736)
      self.assertEqual(cpp_flag.Get('cpp_new_uint64'), '68719476736')

      with self.assertRaises(ValueError):
        FLAGS.cpp_new_uint64 = None
    finally:
      FLAGS.cpp_new_uint64 = 128

  def test_cpp_flag_new_double(self):
    self.assertEqual('double', cpp_flag.GetFlagTypeName('cpp_new_double'))
    self.assertEqual(FLAGS.cpp_new_double, 1.5)
    try:
      FLAGS.cpp_new_double = 2.5
      self.assertEqual(FLAGS.cpp_new_double, 2.5)
      self.assertEqual(cpp_flag.Get('cpp_new_double'), '2.5')

      FLAGS.cpp_new_double = 3
      self.assertEqual(FLAGS.cpp_new_double, 3)
      self.assertEqual(cpp_flag.Get('cpp_new_double'), '3')

      FLAGS.cpp_new_double = '3.5'
      self.assertEqual(FLAGS.cpp_new_double, 3.5)
      self.assertEqual(cpp_flag.Get('cpp_new_double'), '3.5')

      cpp_flags_test_helper.update_cpp_new_double(4.5)
      self.assertEqual(FLAGS.cpp_new_double, 4.5)
      self.assertEqual(cpp_flag.Get('cpp_new_double'), '4.5')

      with self.assertRaises(ValueError):
        FLAGS.cpp_new_double = None
    finally:
      FLAGS.cpp_new_double = 128

  def test_cpp_flag_new_string(self):
    self.assertEqual(FLAGS.cpp_new_string, 'string')
    try:
      FLAGS.cpp_new_string = 'else'
      self.assertEqual(FLAGS.cpp_new_string, 'else')
      self.assertEqual(cpp_flag.Get('cpp_new_string'), 'else')

      cpp_flags_test_helper.update_cpp_new_string('different')
      self.assertEqual(FLAGS.cpp_new_string, 'different')
      self.assertEqual(cpp_flag.Get('cpp_new_string'), 'different')

      with self.assertRaises(ValueError):
        FLAGS.cpp_new_string = None
    finally:
      FLAGS.cpp_new_string = 'string'

  def test_cpp_flag(self):
    # Check that the dummy flag is defined.
    self.assertEqual(FLAGS.dummy, None)

    # Check our overridden C++ flag has the right (default) value.
    self.assertEqual(FLAGS.pure_cpp_flag, new_pure_cpp_flag_value)
    # Check that C++ actually knows we changed the value, too.
    value = cpp_flag.Get('pure_cpp_flag')
    self.assertEqual(int(value), new_pure_cpp_flag_value)

    try:
      FLAGS.pure_cpp_flag = new_pure_cpp_flag_value + 2
      # Check our overridden C++ flag has the right (default) value.
      self.assertEqual(FLAGS.pure_cpp_flag, new_pure_cpp_flag_value + 2)
      # Check that C++ actually knows we changed the value, too.
      value = cpp_flag.Get('pure_cpp_flag')
      self.assertEqual(int(value), new_pure_cpp_flag_value + 2)

      # Check that updating Flag object's value directly also updates C++ value.
      FLAGS['pure_cpp_flag'].value = new_pure_cpp_flag_value + 4
      self.assertEqual(FLAGS.pure_cpp_flag, new_pure_cpp_flag_value + 4)
      value = cpp_flag.Get('pure_cpp_flag')
      self.assertEqual(int(value), new_pure_cpp_flag_value + 4)
    finally:
      FLAGS.pure_cpp_flag = new_pure_cpp_flag_value

    old_value = FLAGS.pyflag_default_overrides_cpp
    try:
      assert old_value != 3, 'Make sure old_value is not 3'
      assert PYFLAG_DEFAULT_OVERRIDES_CPP.value != 3, ('Make sure old_value is '
                                                       'not 3')
      FLAGS.pyflag_default_overrides_cpp = 3
      value = cpp_flag.Get('pyflag_default_overrides_cpp')
      self.assertEqual('3', value)
      self.assertEqual(3, PYFLAG_DEFAULT_OVERRIDES_CPP.value)

      FLAGS['pyflag_default_overrides_cpp'].value = 6
      value = cpp_flag.Get('pyflag_default_overrides_cpp')
      self.assertEqual('6', value)
    finally:
      FLAGS.pyflag_default_overrides_cpp = old_value

  def test_deepcopy_cpp_flags(self):
    self.assertEqual(FLAGS.pure_cpp_flag, new_pure_cpp_flag_value)

    copied_flags = copy.deepcopy(FLAGS)
    copied_flags.pure_cpp_flag = 13
    self.assertEqual(copied_flags.pure_cpp_flag, 13)

    # Check that neither global Python FLAGS nor C++ flag values changed
    self.assertEqual(FLAGS.pure_cpp_flag, new_pure_cpp_flag_value)
    value = cpp_flag.Get('pure_cpp_flag')
    self.assertEqual(int(value), new_pure_cpp_flag_value)

  def test_undefined_cpp_flag(self):
    self.assertIsInstance(undefined_cpp_flag_exception,
                          flags.UnrecognizedFlagError)

  def test_invalid_cpp_flag_value(self):
    self.assertIsInstance(invalid_cpp_flag_exception,
                          flags.IllegalFlagValueError)

  def test_cpp_flag_unicode_value(self):
    unicode_value = 'Да!'
    self.assertIn('mlock_style', FLAGS)
    try:
      FLAGS.mlock_style = unicode_value
      self.assertEqual(unicode_value, FLAGS.mlock_style)
      actual = cpp_flag.Get('mlock_style')
      self.assertEqual(unicode_value, actual)
    finally:
      FLAGS.mlock_style = FLAGS['mlock_style'].default

  def test_redefined_py_flag_default_overrides_cpp(self):
    self.assertEqual(FLAGS['pyflag_default_overrides_cpp'].flag_type(), '[C++]')
    self.assertEqual(FLAGS.pyflag_default_overrides_cpp, 1)

  def test_redefined_py_flag_value_overrides_cpp(self):
    self.assertEqual(FLAGS['pyflag_value_overrides_cpp'].flag_type(), '[C++]')
    self.assertNotEqual(FLAGS.pyflag_value_overrides_cpp,
                        pyflag_value_overrides_cpp_default)
    self.assertEqual(FLAGS.pyflag_value_overrides_cpp, 1)

  def test_cpp_flag_override_and_hide_raises(self):
    with self.assertRaises(flags.Error):
      flags.DEFINE_bool(
          'unused', 'default', '...', allow_hide_cpp=True,
          allow_override_cpp=True)

  def test_cpp_flag_override_cpp_raises_on_redefine(self):
    with self.assertRaises(flags.DuplicateFlagError):
      flags.DEFINE_bool(
          'pyflag_default_overrides_cpp', False, '...',
          allow_override_cpp=True)

  def test_cpp_flag_override_with_default_none(self):
    with self.assertRaises(_exceptions.NoneCannotPropagateToCppFlagsError):
      flags.DEFINE_bool(
          'unused', None, '...', allow_override_cpp=True)

  def test_set_default_to_pure_cpp_flag(self):
    # It was set default to 18 before flags are parsed.
    self.assertEqual(FLAGS.pure_cpp_flag_set_default_in_py, 18)

  def test_main_module_key_flag_with_allow_override_cpp(self):
    log_dir_flag = FLAGS['log_dir']
    self.assertIsInstance(log_dir_flag, _cpp_flags._CppFlag)
    self.assertIn(log_dir_flag, FLAGS.get_key_flags_for_module(sys.argv[0]))


class CppFlagsFunctionalTest(parameterized.TestCase):

  def _check_helper(self, env=None):
    helper = _bazelize_command.get_executable_path(
        'absl/flags/tests/cpp_flags_test_helper_app')
    if env is not None:
      # If env is specified, merge them with the current process.
      env = dict(os.environ, **env)
    proc = subprocess.Popen([helper],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            env=env)
    stdout, stderr = proc.communicate()
    self.assertEqual(
        # Helper will exit with non-zero return code on failures.
        proc.returncode,
        0,
        f'Helper failed with stdout:\n{stdout}\nstderr:\n{stderr}',
    )
    return stdout, stderr

  def test_init_and_load(self):
    self._check_helper()

  @parameterized.named_parameters(
      ('bool_match', 'cpp_bool_default_false', 'boolean', True),
      ('bool_nomatch', 'cpp_bool_default_false', 'integer', False),
      ('int32_match', 'cpp_int32', 'integer', True),
      ('int32_nomatch', 'cpp_int32', 'string', False),
      ('int64_match', 'cpp_int64', 'integer', True),
      ('int64_nomatch', 'cpp_int64', 'string', False),
      ('uint64_match', 'cpp_uint64', 'integer', True),
      ('uint64_nomatch', 'cpp_uint64', 'string', False),
      ('double_match', 'cpp_double', 'float', True),
      ('double_nomatch', 'cpp_double', 'integer', False),
      ('string_match', 'cpp_string', 'string', True),
      ('string_nomatch', 'cpp_string', 'boolean', False),
      ('new_bool_match', 'cpp_new_bool', 'boolean', True),
      ('new_bool_nomatch', 'cpp_new_bool', 'integer', False),
      ('new_int32_match', 'cpp_new_int32', 'integer', True),
      ('new_int32_nomatch', 'cpp_new_int32', 'string', False),
      ('new_int64_match', 'cpp_new_int64', 'integer', True),
      ('new_int64_nomatch', 'cpp_new_int64', 'string', False),
      ('new_uint64_match', 'cpp_new_uint64', 'integer', True),
      ('new_uint64_nomatch', 'cpp_new_uint64', 'string', False),
      ('new_double_match', 'cpp_new_double', 'float', True),
      ('new_double_nomatch', 'cpp_new_double', 'integer', False),
      ('new_string_match', 'cpp_new_string', 'string', True),
      ('new_string_nomatch', 'cpp_new_string', 'boolean', False),
  )
  def test_flag_types_match(self, flag_name, py_type, success):
    stdout, stderr = self._check_helper(
        env={
            'OVERRIDDEN_PY_FLAG_NAME': flag_name,
            'OVERRIDDEN_PY_FLAG_TYPE': py_type,
            'CATCH_ERROR_IN_LOAD': '1',
        })
    if success:
      self.assertEqual(
          b'', stdout,
          'Defining --{} as "{}" failed, stdout:\n{}\nstderr:\n{}'.format(
              flag_name, py_type, stdout, stderr))
    else:
      self.assertEqual(
          b'_cpp_flags.load() did throw flags.Error', stdout,
          'Defining --{} as "{}" should not succeed, '
          'stdout:\n{}\nstderr:\n{}'.format(flag_name, py_type, stdout, stderr))

  @parameterized.named_parameters(
      ('bool', '--cpp_bool_default_false=true',
       '--cpp_bool_default_false=True'),
      ('int32', '--cpp_int32=9', '--cpp_int32=9'),
      ('int64', '--cpp_int64=18', '--cpp_int64=18'),
      ('uint64', '--cpp_uint64=36', '--cpp_uint64=36'),
      ('double', '--cpp_double=1.5', '--cpp_double=1.5'),
      ('string', '--cpp_string=string', '--cpp_string=string'),
      ('new_bool', '--nocpp_new_bool', '--cpp_new_bool=False'),
      ('new_int32', '--cpp_new_int32=9', '--cpp_new_int32=9'),
      ('new_int64', '--cpp_new_int64=18', '--cpp_new_int64=18'),
      ('new_uint64', '--cpp_new_uint64=36', '--cpp_new_uint64=36'),
      ('new_double', '--cpp_new_double=2.5', '--cpp_new_double=2.5'),
      ('new_string', '--cpp_new_string=string', '--cpp_new_string=string'),
  )
  def test_get_cpp_args(self, arg, expected):
    self._check_helper(env={
        'ADDITIONAL_ARGV': arg,
        'EXPECTED_CPP_ARGS': expected,
    })

  @parameterized.named_parameters(
      ('bool', 'cpp_bool_default_false', bool),
      ('int32', 'cpp_int32', int),
      ('int64', 'cpp_int64', int),
      ('uint64', 'cpp_uint64', int),
      ('double', 'cpp_double', float),
      ('string', 'cpp_string', str),
      ('new_bool', 'cpp_new_bool', bool),
      ('new_int32', 'cpp_new_int32', int),
      ('new_int64', 'cpp_new_int64', int),
      ('new_uint64', 'cpp_new_uint64', int),
      ('new_double', 'cpp_new_double', float),
      ('new_string', 'cpp_new_string', str),
  )
  def test_set_default_after_flags_are_parsed(self, flag_name, py_type):
    old_value = getattr(FLAGS, flag_name)
    if py_type == bool:
      new_value = not old_value
    elif py_type == int or py_type == float:
      new_value = old_value + 1
    elif py_type == str:
      new_value = old_value + ', flags are parsed.'
    try:
      FLAGS.set_default(flag_name, new_value)
      self.assertEqual(new_value, getattr(FLAGS, flag_name))
    finally:
      setattr(FLAGS, flag_name, old_value)


if __name__ == '__main__':
  FLAGS.pure_cpp_flag = new_pure_cpp_flag_value
  FLAGS.set_default('pure_cpp_flag_set_default_in_py', 18)
  # pylint: disable=broad-except
  try:
    FLAGS.undefined_cpp_flag = 0
  except Exception as e:
    undefined_cpp_flag_exception = e
  try:
    FLAGS.pure_cpp_flag = "don't"
  except Exception as e:
    invalid_cpp_flag_exception = e
  absltest.main()
