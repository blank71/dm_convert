# Copyright 2022 The Abseil Authors.
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
"""Test that ensures the flags's types are expected from pytype's view."""

import enum
from typing import List, Optional
from absl import flags


class MyEnum(enum.Enum):
  A = enum.auto()
  B = enum.auto()


# The linter doesn't know `assert_type` is a pytype function.
# pylint: disable=undefined-variable


assert_type(
    flags.DEFINE_string('string_flag_defaults_to_none', None, 'Help text.'),
    flags._flagvalues.FlagHolder[Optional[str]],
)
assert_type(
    flags.DEFINE_string(
        'string_flag_defaults_to_none_required',
        None,
        'Help text.',
        required=True,
    ),
    flags._flagvalues.FlagHolder[str],
)
assert_type(
    flags.DEFINE_string(
        'string_flag_defaults_to_not_none', 'default', 'Help text.'
    ),
    flags._flagvalues.FlagHolder[str],
)

assert_type(
    flags.DEFINE_bool('bool_flag_defaults_to_none', None, 'Help text.'),
    flags._flagvalues.FlagHolder[Optional[bool]],
)
assert_type(
    flags.DEFINE_bool(
        'bool_flag_defaults_to_none_required', None, 'Help text.', required=True
    ),
    flags._flagvalues.FlagHolder[bool],
)
assert_type(
    flags.DEFINE_bool('bool_flag_defaults_to_not_none', 0, 'Help text.'),
    flags._flagvalues.FlagHolder[bool],
)

assert_type(
    flags.DEFINE_float('float_flag_defaults_to_none', None, 'Help text.'),
    flags._flagvalues.FlagHolder[Optional[float]],
)
assert_type(
    flags.DEFINE_float(
        'float_flag_defaults_to_none_required',
        None,
        'Help text.',
        required=True,
    ),
    flags._flagvalues.FlagHolder[float],
)
assert_type(
    flags.DEFINE_float('float_flag_defaults_to_not_none', 0, 'Help text.'),
    flags._flagvalues.FlagHolder[float],
)

assert_type(
    flags.DEFINE_integer('integer_flag_defaults_to_none', None, 'Help text.'),
    flags._flagvalues.FlagHolder[Optional[int]],
)
assert_type(
    flags.DEFINE_integer(
        'integer_flag_defaults_to_none_required',
        None,
        'Help text.',
        required=True,
    ),
    flags._flagvalues.FlagHolder[int],
)
assert_type(
    flags.DEFINE_integer('integer_flag_defaults_to_not_none', 0, 'Help text.'),
    flags._flagvalues.FlagHolder[int],
)

assert_type(
    flags.DEFINE_enum(
        'enum_flag_defaults_to_none', None, ['a', 'b'], 'Help text.'
    ),
    flags._flagvalues.FlagHolder[Optional[str]],
)
assert_type(
    flags.DEFINE_enum(
        'enum_flag_defaults_to_none_required',
        None,
        ['a', 'b'],
        'Help text.',
        required=True,
    ),
    flags._flagvalues.FlagHolder[str],
)
assert_type(
    flags.DEFINE_enum(
        'enum_flag_defaults_to_not_none', 'a', ['a', 'b'], 'Help text.'
    ),
    flags._flagvalues.FlagHolder[str],
)


assert_type(
    flags.DEFINE_enum_class(
        'enum_class_flag_defaults_to_none', None, MyEnum, 'Help text.'
    ),
    flags._flagvalues.FlagHolder[Optional[MyEnum]],
)
assert_type(
    flags.DEFINE_enum_class(
        'enum_class_flag_defaults_to_none',
        None,
        MyEnum,
        'Help text.',
        required=True,
    ),
    flags._flagvalues.FlagHolder[MyEnum],
)
assert_type(
    flags.DEFINE_enum_class(
        'enum_class_flag_defaults_to_not_none', MyEnum.A, MyEnum, 'Help text.'
    ),
    flags._flagvalues.FlagHolder[MyEnum],
)


assert_type(
    flags.DEFINE_list('list_flag_defaults_to_none', None, 'Help text.'),
    flags._flagvalues.FlagHolder[Optional[List[str]]],
)
assert_type(
    flags.DEFINE_list(
        'list_flag_defaults_to_none', None, 'Help text.', required=True
    ),
    flags._flagvalues.FlagHolder[List[str]],
)
assert_type(
    flags.DEFINE_list(
        'list_flag_defaults_to_not_none', ['something'], 'Help text.'
    ),
    flags._flagvalues.FlagHolder[List[str]],
)


assert_type(
    flags.DEFINE_spaceseplist(
        'spaceseplist_flag_defaults_to_none', None, 'Help text.'
    ),
    flags._flagvalues.FlagHolder[Optional[List[str]]],
)
assert_type(
    flags.DEFINE_spaceseplist(
        'spaceseplist_flag_defaults_to_none', None, 'Help text.', required=True
    ),
    flags._flagvalues.FlagHolder[List[str]],
)
assert_type(
    flags.DEFINE_spaceseplist(
        'spaceseplist_flag_defaults_to_not_none', ['something'], 'Help text.'
    ),
    flags._flagvalues.FlagHolder[List[str]],
)


assert_type(
    flags.DEFINE_multi_string(
        'multi_string_flag_defaults_to_none', None, 'Help text.'
    ),
    flags._flagvalues.FlagHolder[Optional[List[str]]],
)
assert_type(
    flags.DEFINE_multi_string(
        'multi_string_flag_defaults_to_none', None, 'Help text.', required=True
    ),
    flags._flagvalues.FlagHolder[List[str]],
)
assert_type(
    flags.DEFINE_multi_string(
        'multi_string_flag_defaults_to_not_none', ['something'], 'Help text.'
    ),
    flags._flagvalues.FlagHolder[List[str]],
)

assert_type(
    flags.DEFINE_multi_integer(
        'multi_integer_flag_defaults_to_none', None, 'Help text.'
    ),
    flags._flagvalues.FlagHolder[Optional[List[int]]],
)
assert_type(
    flags.DEFINE_multi_integer(
        'multi_integer_flag_defaults_to_none', None, 'Help text.', required=True
    ),
    flags._flagvalues.FlagHolder[List[int]],
)
assert_type(
    flags.DEFINE_multi_integer(
        'multi_integer_flag_defaults_to_not_none', [1], 'Help text.'
    ),
    flags._flagvalues.FlagHolder[List[int]],
)

assert_type(
    flags.DEFINE_multi_float(
        'multi_float_flag_defaults_to_none', None, 'Help text.'
    ),
    flags._flagvalues.FlagHolder[Optional[List[float]]],
)
assert_type(
    flags.DEFINE_multi_float(
        'multi_float_flag_defaults_to_none', None, 'Help text.', required=True
    ),
    flags._flagvalues.FlagHolder[List[float]],
)
assert_type(
    flags.DEFINE_multi_float(
        'multi_float_flag_defaults_to_not_none', [1], 'Help text.'
    ),
    flags._flagvalues.FlagHolder[List[float]],
)

assert_type(
    flags.DEFINE_multi_enum(
        'multi_enum_flag_defaults_to_none', None, ['a', 'b'], 'Help text.'
    ),
    flags._flagvalues.FlagHolder[Optional[List[str]]],
)
assert_type(
    flags.DEFINE_multi_enum(
        'multi_enum_flag_defaults_to_none',
        None,
        ['a', 'b'],
        'Help text.',
        required=True,
    ),
    flags._flagvalues.FlagHolder[List[str]],
)
assert_type(
    flags.DEFINE_multi_enum(
        'multi_enum_flag_defaults_to_not_none', ['a'], ['a', 'b'], 'Help text.'
    ),
    flags._flagvalues.FlagHolder[List[str]],
)

assert_type(
    flags.DEFINE_multi_enum_class(
        'multi_enum_class_flag_defaults_to_none', None, MyEnum, 'Help text.'
    ),
    flags._flagvalues.FlagHolder[Optional[List[MyEnum]]],
)
assert_type(
    flags.DEFINE_multi_enum_class(
        'multi_enum_class_flag_defaults_to_none',
        None,
        MyEnum,
        'Help text.',
        required=True,
    ),
    flags._flagvalues.FlagHolder[List[MyEnum]],
)
assert_type(
    flags.DEFINE_multi_enum_class(
        'multi_enum_class_flag_defaults_to_element',
        MyEnum.A,
        MyEnum,
        'Help text.',
    ),
    flags._flagvalues.FlagHolder[List[MyEnum]],
)
assert_type(
    flags.DEFINE_multi_enum_class(
        'multi_enum_class_flag_defaults_to_list',
        [MyEnum.A],
        MyEnum,
        'Help text.',
    ),
    flags._flagvalues.FlagHolder[List[MyEnum]],
)
assert_type(
    flags.DEFINE_multi_enum_class(
        'multi_enum_class_flag_defaults_to_list_empty', [], MyEnum, 'Help text.'
    ),
    flags._flagvalues.FlagHolder[List[MyEnum]],
)

assert_type(
    flags.DEFINE_alias('alias_flag', 'old_flag'),
    flags._flagvalues.FlagHolder,
)
