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
"""Private module for Python and C++ flags integration.

This module allows a google python app to accept all the flags necessary
for the underlying C++ code.

It should only be imported by absl libraries. For how to access C++ flags,
see go/absl.flags.cpp_flags.
"""

import sys

from absl import flags
from absl.flags import _cpp_flags_internal

from google3.base.python.clif import cpp_flag

FLAGS = flags.FLAGS

_boolean_parser = flags.BooleanParser()
_integer_parser = flags.IntegerParser()
_float_parser = flags.FloatParser()

# How to convert a string value to another Python value based on flag type.
_KNOWN_CONVERSION = dict(
    bool=_boolean_parser.parse,
    int32=_integer_parser.parse,
    int64=_integer_parser.parse,
    uint64=_integer_parser.parse,
    double=_float_parser.parse,
)
_NUMERIC_OR_BOOL_TYPES = {
    'bool': bool,
    'int32': int,
    'int64': int,
    'uint64': int,
    'double': (int, float),
}


def set_flag(name, value):
  """Sets the flag value.

  Args:
    name: The flag name.
    value: The flag value.

  Raises:
    ValueError: Raised when `value` is invalid.
  """
  try:
    cpp_flag.Set(name, value if isinstance(value, (str, bytes)) else str(value))
  except ValueError as e:
    raise ValueError('Failure setting flag "--%s": %s' % (name, e))


def set_argv(argv):
  cpp_flag.SetArgv(argv)


def _py_val(t, v):
  """Converts C++ flag value |v| to Python flag type |t|."""
  numeric_or_bool_type = _NUMERIC_OR_BOOL_TYPES.get(t)
  if numeric_or_bool_type is not None and isinstance(v, numeric_or_bool_type):
    return v
  if not isinstance(v, (str, bytes)):
    raise ValueError('Non-numeric/boolean flags only takes {} values, '
                     'found t={}, v={}.'.format((str, bytes), t, v))
  c = _KNOWN_CONVERSION.get(t)
  return c(v) if c else v


_CPP_TO_PY_FLAG_TYPE_MAPPING = {
    'bool': 'bool',
    'int32': 'int',
    'int64': 'int',
    'uint64': 'int',
    'double': 'float',
    'string': 'string',
    '': 'string',
}


def _check_matching_flag_types(pyflag, cppflag_type, is_cppflag_bool):
  """Raises error when Python flag type does not match C++ flag type.

  Args:
    pyflag: flags.Flag, the Python flag.
    cppflag_type: string, the derived C++ flag type. For built-in C++ boolean or
      numeric flags, it's bool/int32/int64/uint64/double, not empty.
    is_cppflag_bool: bool, whether the C++ flag is boolean.

  Raises:
    flags.Error: raised when python flag type does not match C++ flag type.
  """
  flag_name = pyflag.name
  if pyflag.boolean != is_cppflag_bool:
    raise flags.Error(
        'Flag --%s defined as boolean=%s but C++ flag defined as boolean=%s' %
        (pyflag.name, pyflag.boolean, is_cppflag_bool))

  pyflag_type = pyflag.flag_type()
  expected_pyflag_type = _CPP_TO_PY_FLAG_TYPE_MAPPING[cppflag_type]
  if expected_pyflag_type != pyflag_type:
    if not cppflag_type:
      # Give a better message for new style C++ flags.
      raise flags.Error(
          'Non-built-in boolean or numeric new style C++ flag must be defined '
          'as a "string" flag in Python, but found "{}" for flag --{}.'.format(
              pyflag_type, flag_name))
    else:
      raise flags.Error(
          'C++ "{}" flag must be defined as a "{}" flag in Python, '
          'but found "{}" for flag --{}.'.format(cppflag_type,
                                                 expected_pyflag_type,
                                                 pyflag_type, flag_name))


def load():
  """Defines a python flag for each C++ flag.

  This is called by app.py before flag parsing to define C++ flags in Python,
  as well as to override C++ flag's default value if the flag is also defined
  in Python.

  Returns:
    A list of C++ flag objects.
  """
  cpp_flags = []
  main_module_key_flags = FLAGS.get_key_flags_for_module(sys.argv[0])
  for flag in cpp_flag.GetAllFlags():
    flag_type = cpp_flag.GetFlagTypeName(flag.name)
    is_flag_bool = (flag_type == 'bool')
    register_key_flag_for_main = False
    if flag.name in FLAGS:
      pyflag = FLAGS[flag.name]
      if pyflag.allow_hide_cpp:
        continue
      if pyflag.allow_override_cpp:
        _check_matching_flag_types(pyflag, flag_type, is_flag_bool)
        value = pyflag.default if pyflag.value is None else pyflag.value
        # Python's value overrides C++'s. Note this value might be different
        # than the one in the Python flag definition, since it can be updated
        # by FLAGS.set_default or FLAGS.__setattr__ before Python parses flags.
        default_value = _cpp_flags_internal.set_default(flag.name, value)
        register_key_flag_for_main = FLAGS[flag.name] in main_module_key_flags
        # Delete the python flag, a new flag will be defined for C++.
        delattr(FLAGS, flag.name)
      else:
        raise flags.DuplicateFlagError(
            'Flag --%s defined both in C++ and Python. To keep using the '
            'C++ flag, remove Python flag definition from %s or add '
            'allow_override_cpp=True to its Python definition.\n'
            'To use the Python flag (and ignore the C++ flag from %s) '
            'add allow_hide_cpp=True to the Python flag definition.' %
            (flag.name, FLAGS.find_module_defining_flag(
                flag.name), flag.filename))
    else:
      default_value = flag.default_value

    new_flag = _CppFlag(
        _CppParser(flag.name, flag_type),
        flags.ArgumentSerializer(),
        flag.name,
        default_value,
        '[C++] ' + flag.description,
        boolean=is_flag_bool)
    flags.DEFINE_flag(new_flag, module_name=flag.filename)
    if register_key_flag_for_main:
      # When a overridden Python flag is declared as a key flag, we need to
      # re-register for the new C++ flag. This is only needed for main module
      # because key flags are used for including the flag in --help[short]
      # messages.
      FLAGS.register_key_flag_for_module(sys.argv[0], new_flag)
    cpp_flags.append(new_flag)
  return cpp_flags


def get_cpp_args(cpp_flags):
  """Returns a list of C++ flags that are present on the command line."""
  return [
      f'--{f.name}={f.serializer.serialize(f.value)}'
      for f in cpp_flags
      if f.present
  ]


def synchronize_cpp_flags(cpp_flags):
  """Starts to synchronize C++ flags."""
  for flag in cpp_flags:
    flag._synchronize_with_cpp = True  # pylint: disable=protected-access


class _CppFlag(flags.Flag):
  """Class for C++ flags."""

  def __init__(self, *args, **kwargs):
    # Flag parses the default value during initialization. Set synchronization
    # to False during this time since the default value is set separately in
    # load().
    self._synchronize_with_cpp = False
    super().__init__(*args, **kwargs)

  @property
  def value(self):
    if self._synchronize_with_cpp:
      self._value = self.parser.parse(cpp_flag.Get(self.name))
    return self._value

  @value.setter
  def value(self, value):
    if value is None:
      raise ValueError('Cannot set flag "{}" defined in C++ to None.'.format(
          self.name))
    if self._synchronize_with_cpp:
      set_flag(self.name, value)
    self._value = value

  def __deepcopy__(self, memo):
    result = super().__deepcopy__(memo)
    # C++ flags don't expose an interface for copying: there is only a single,
    # global set of flags. To ensure that modifying deep-copied flags can't
    # effect the originals, we disable synchronization for deep-copied C++
    # flags.
    result._synchronize_with_cpp = False  # pylint: disable=protected-access
    return result


class _CppParser(flags.ArgumentParser):
  """ArgumentParser class for C++ flags."""

  def __init__(self, flag_name, flag_type):
    self._name = flag_name
    self._pytype = flag_type

  def flag_type(self):
    return '[C++]'

  def parse(self, value):
    return _py_val(self._pytype, value)
