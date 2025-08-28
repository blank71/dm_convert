"""Tests for typedefs.

In addition to checking the assignments to fields/parameters, this test also
leverages the synthetic `assert_type` function from `pytype_extension`. See
go/pytype-faq#can-i-find-out-what-pytype-thinks-the-type-of-my-expression-is for
more.
"""

from typing import Callable
from absl.typing import typedefs


def predicate(x: int) -> bool:
  return x > 2


def accept_predicate(p: Callable[[int], bool]) -> bool:
  return p(0)


assigned_predicate: typedefs.Predicate[int] = predicate
assert_type(assigned_predicate, "Callable[[int], bool]")  # pylint: disable=undefined-variable
accept_predicate(assigned_predicate)


def binary_predicate(x: int, y: float) -> bool:
  return x + y > 2


def accept_binary_predicate(p: Callable[[int, float], bool]) -> bool:
  return p(0, 1.0)


assigned_binary_predicate: typedefs.BinaryPredicate[int, float] = (
    binary_predicate)
assert_type(assigned_binary_predicate, "Callable[[int, float], bool]")  # pylint: disable=undefined-variable
accept_binary_predicate(assigned_binary_predicate)


def unary_operator(x: int) -> int:
  return x


def accept_unary_operator(o: Callable[[int], int]) -> int:
  return o(0)


assigned_unary_operator: typedefs.UnaryOperator[int] = unary_operator
assert_type(assigned_unary_operator, "Callable[[int], int]")  # pylint: disable=undefined-variable
accept_unary_operator(assigned_unary_operator)


def binary_operator(x: int, y: int) -> int:
  return x + y


def accept_binary_operator(o: Callable[[int, int], int]) -> int:
  return o(0, 0)


assigned_binary_operator: typedefs.BinaryOperator[int] = binary_operator
assert_type(assigned_binary_operator, "Callable[[int, int], int]")  # pylint: disable=undefined-variable
accept_binary_operator(assigned_binary_operator)


def consumer(x: int):
  print(x)


def accept_consumer(c: Callable[[int], None]):
  return c(0)


assigned_consumer: typedefs.Consumer[int] = consumer
assert_type(assigned_consumer, "Callable[[int], None]")  # pylint: disable=undefined-variable
accept_consumer(assigned_consumer)


def supplier() -> int:
  return 1


def accept_supplier(s: Callable[[], int]) -> int:
  return s()


assigned_supplier: typedefs.Supplier[int] = supplier
assert_type(assigned_supplier, "Callable[[], int]")  # pylint: disable=undefined-variable
accept_supplier(assigned_supplier)
