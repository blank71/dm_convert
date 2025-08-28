"""Run stock tests under Google3."""

import sys
from absl.testing import absltest

from yaml.tests import test_all


class TestYaml(absltest.TestCase):

  def testAll(self):
    test_all.main()


if __name__ == '__main__':
  absltest.main()
