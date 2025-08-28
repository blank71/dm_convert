"""Utilities for general purpose typing related tasks."""

import typing


def issubclass_generic_aware(cls, bases):
  """Like `issubclass()`, but allows generics.

  As of Python 3.7 and PEP 560, `issubcclass()` raises an error when
  passed instantiated generics or certain generic types for the type
  being checked. e.g., these invocations raise an error:

      issubclass(MyGeneric[int], MyGeneric)
      issubclass(typing.List, list)
      issubclass(typing.List[int], list)

  This function allows such types to be checked (e.g, all the examples
  would return True, as they did in Python 3.6).

  Args:
    cls: A class type or an instantiated generic of one (e.g. `list[int]`), to
      check if it is a subclass of `bases`.
    bases: A base type, or tuple of types, that `cls` is being checked as a
      subclass of (see `issubclass()` docs).

  Returns:
    bool, True if it is a subclass, False if not. NOTE: invalid
    input will raise an error, not False.

  """
  actual_cls = _get_logical_class(cls)
  return issubclass(actual_cls, bases)


def _get_logical_class(cls):
  """Returns the class a generic has wrapped, or the class itself if none."""
  origin = typing.get_origin(cls)
  if origin is not None:
    return origin
  else:
    return cls
