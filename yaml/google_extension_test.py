"""Test availability of extension module."""

import yaml

from absl.testing import absltest


class TestExtensionModule(absltest.TestCase):

  def testExtensionIsUsed(self):
    """Test that the _yaml extension module is available and used by yaml."""
    self.assertTrue(yaml.__with_libyaml__)


if __name__ == '__main__':
  absltest.main()
