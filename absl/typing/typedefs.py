"""Common type definitions that complement the `typing` module."""

import os
from typing import Callable, TypeVar, Union
from typing_extensions import TypeAlias

# TODO: Add g-bare-generic lint support to these types.

T = TypeVar("T")
U = TypeVar("U")

# A `Callable` that returns `True`/`False` based on a single input.
Predicate: TypeAlias = Callable[[T], bool]

# A `Callable` that returns `True`/`False` based on two inputs.
BinaryPredicate: TypeAlias = Callable[[T, U], bool]

# A `Callable` that computes a result based on a single input and returns a
# value of the same type.
UnaryOperator: TypeAlias = Callable[[T], T]

# A `Callable` that computes a result based on a two inputs and returns a
# value. The inputs and output are all of the same type.
BinaryOperator: TypeAlias = Callable[[T, T], T]

# A `Callable` that receives a single input and has no return value.
Consumer: TypeAlias = Callable[[T], None]

# A `Callable` that supplies a single value on each call.
#
# There are no guarantees that the supplied value will be identical on
# successive calls.
Supplier: TypeAlias = Callable[[], T]

# A `Callable` that takes no arguments and has no return value.
Runnable: TypeAlias = Callable[[], None]

# A general type that can act like string file paths, i.e.
# `str | os.PathLike[str]`. If you need both str and bytes, use
# `StrOrBytesPath`.
StrPath: TypeAlias = Union[str, os.PathLike[str]]

# A general type that can act like file paths. This covers both primitive types
# (str and bytes) as well as their os.PathLike variants. If you just need string
# paths, use `StrPath`.
StrOrBytesPath: TypeAlias = Union[
    str, bytes, os.PathLike[str], os.PathLike[bytes]]
