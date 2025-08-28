"""Tests for absl.typing.typelib."""

from typing import Generic, Iterable, List, TypeVar

from absl.testing import absltest
from absl.testing import parameterized
from absl.typing import typelib

T = TypeVar('T')


class BasicGeneric(Generic[T]):
  pass


class SubGeneric(Iterable[T]):
  pass


class TypelibTest(parameterized.TestCase):

  def assertIsSubclassGenericAware(self, cls, base):
    result = typelib.issubclass_generic_aware(cls, base)
    if not result:
      # Use self.fail() instead because assertTrue() has a vestigial
      # "false is not true" prefix.
      self.fail(f'Class {cls!r} is not a subclass of {base!r}')

  @parameterized.named_parameters(
      ('bool_int', bool, int),
      ('plain_typing_list', List, list),
      ('list_real_list', List[int], list),
      ('list_typing_list', List[int], List),
      ('basic_generic', BasicGeneric[int], BasicGeneric),
      ('sub_generic', SubGeneric[int], Iterable),
  )
  def test_issubclass_generic_aware(self, sub, base):
    self.assertIsSubclassGenericAware(sub, base)


if __name__ == '__main__':
  absltest.main()
