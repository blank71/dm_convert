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

"""Helper script to test cpp_flags."""

import os
import sys
import traceback

from absl import flags
from absl.flags import _cpp_flags

from google3.base.python.clif import cpp_flag
from google3.base.python.clif import googleinit

FLAGS = flags.FLAGS

flags.DEFINE_integer('pyflag_default_overrides_cpp', 1, 'Pre C++ flag.',
                     allow_override_cpp=True)


def main():
  # Use a custom main function to test _cpp_flags.load.
  argv = [sys.argv[0],
          '--pyflag_default_overrides_cpp=2', 'cmd', '--cpp_int64', '18',
          '--pure_cpp_flag=1', '--cpp_retired', 'any',
          '--cpp_new_retired', 'any']
  additional_argv = os.getenv('ADDITIONAL_ARGV')
  if additional_argv:
    argv += additional_argv.split(' ')
  # Test arguments after a bare --.
  argv += ['--', '--ignored', 'positional']
  FLAGS.set_gnu_getopt()

  v = FLAGS['pyflag_default_overrides_cpp'].value
  assert v == 1, f'Wrong pyflag value before flag parsing: {v}.'
  assert 'pure_cpp_flag' not in FLAGS, (
      'pure_cpp_flag should not exit before load.')
  v = cpp_flag.Get('pyflag_default_overrides_cpp')
  assert v == '0', f'Wrong default C++ flag value before _cpp_flags.load: {v}.'

  old_flag = FLAGS['pyflag_default_overrides_cpp']

  try:
    cpp_flag_objects = _cpp_flags.load()
  except flags.Error:
    if os.getenv('CATCH_ERROR_IN_LOAD'):
      sys.stdout.write('_cpp_flags.load() did throw flags.Error')
      sys.stderr.write(traceback.format_exc())
      return
    else:
      raise

  new_flag = FLAGS['pyflag_default_overrides_cpp']
  assert old_flag != new_flag, 'New C++ flag is not defined.'

  # A flag redefined with allow_override_cpp is updated in _cpp_flags.load.
  v = cpp_flag.Get('pyflag_default_overrides_cpp')
  assert v == '1', f'Wrong C++ flag value after _cpp_flags.load: {v}.'
  # A flag not redefined with allow_override_cpp is NOT updated in
  # _cpp_flags.load.
  v = cpp_flag.Get('pure_cpp_flag')
  assert v == '0', f'Wrong C++ flag value after _cpp_flags.load: {v}.'

  argv = FLAGS(argv)

  assert len(argv) == 4, (
      'argv should have exactly four args after flag parsing, '
      'got "{}"'.format(argv))
  assert argv[1:] == ['cmd', '--ignored', 'positional'], (
      "argv[1:] should be ['cmd', '--ignored', 'positional'] after flaag "
      'parsing,  got "{}"'.format(argv[1:]))

  v = cpp_flag.Get('pyflag_default_overrides_cpp')
  assert v == '1', f'Wrong C++ flag value after flag parsing: {v}.'
  v = cpp_flag.Get('pure_cpp_flag')
  assert v == '0', f'Wrong C++ flag value after flag parsing: {v}.'
  assert (
      FLAGS.cpp_int64 == 18
  ), f'Wrong value for cpp_int64 after parsing: {FLAGS.cpp_int64}'

  assert argv, 'argv cannot be empty.'
  cpp_args = _cpp_flags.get_cpp_args(cpp_flag_objects)
  expected_cpp_args = os.getenv('EXPECTED_CPP_ARGS')
  if expected_cpp_args:
    # These flags always exist.
    expected = {'--cpp_int64=18',
                '--pure_cpp_flag=1',
                '--pyflag_default_overrides_cpp=2'}
    expected.add(expected_cpp_args)
    assert (
        sorted(expected) == cpp_args
    ), f'Wrong cpp_args, expected: {expected}, got: {cpp_args}'
  googleinit.Run(argv[:1] + cpp_args)
  _cpp_flags.synchronize_cpp_flags(cpp_flag_objects)

  v = cpp_flag.Get('pyflag_default_overrides_cpp')
  assert v == '2', f'Wrong C++ flag value after flag parsing: {v}.'
  v = cpp_flag.Get('pure_cpp_flag')
  assert v == '1', f'Wrong C++ flag value after flag parsing: {v}.'

  assert FLAGS.pyflag_default_overrides_cpp != 3, (
      'Make sure the old value is not 3.')
  FLAGS.pyflag_default_overrides_cpp = 3
  v = cpp_flag.Get('pyflag_default_overrides_cpp')
  assert v == '3', 'Overridden C++ flag is not synchronized'


if __name__ == '__main__':
  # Define a flag if asked, this is used to test flag also defined in python
  # should match C++ flag's type.
  pyflag_name = os.getenv('OVERRIDDEN_PY_FLAG_NAME')
  if pyflag_name:
    pyflag_type = os.environ['OVERRIDDEN_PY_FLAG_TYPE']
    if pyflag_type == 'integer':
      flags.DEFINE_integer(pyflag_name, 0, 'help', allow_override_cpp=True)
    elif pyflag_type == 'boolean':
      flags.DEFINE_bool(pyflag_name, False, 'help', allow_override_cpp=True)
    elif pyflag_type == 'float':
      flags.DEFINE_float(pyflag_name, 0, 'help', allow_override_cpp=True)
    elif pyflag_type == 'string':
      flags.DEFINE_string(pyflag_name, '0', 'help', allow_override_cpp=True)
    else:
      assert False, f'Unexpected OVERRIDDEN_PY_FLAG_TYPE: {pyflag_type}'

  main()
