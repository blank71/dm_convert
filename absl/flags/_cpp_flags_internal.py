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
"""Private model used by cpp_flags and absl.flags for C++ flag support."""

from google3.base.python.clif import cpp_flag

# Names of flags defined in C++.
_CFLAGNAMES = frozenset(f.name for f in cpp_flag.GetAllFlags())


def set_default(name, value):
  """Sets C++ flag default value.

  Args:
    name: flag name
    value: new default

  Returns:
    string representation of the |value|
  Raises:
    NameError: unknown C++ flag |name|
    ValueError: error setting C++ flag |name| to |value|
  """
  if value is None:
    raise ValueError("Cannot set C++ flag --%s's value to None" % name)
  as_str = value if isinstance(value, (str, bytes)) else str(value)
  ok = cpp_flag.SetDefault(name, as_str)
  if ok:
    return as_str
  raise ValueError() if name in _CFLAGNAMES else NameError()


def is_retired(name):
  """Returns a tuple (is_retired, type_is_bool) for the flag."""
  return cpp_flag.IsRetired(name)
