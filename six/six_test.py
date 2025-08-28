"""Test runner for six tests.

This test is a shim around `test_six.py` because of how the `six` module affects
module loading. Basically, `six` installs custom loaders and sets `__path__`
to an empty list, which prevents finding sub-modules in other locations; see PEP
302 about `__path__`.

When `test_six.py` is run directly under `pytest`, it is recognized as `six.test_six`,
so pytest tries to import that, but that fails because nothing was able to
modify `six.__path__` before hand. Hence this shim to modify `__path__` and
then invoke `pytest test_six.py`
"""
from __future__ import print_function

import os

import pytest
import six

from absl.testing import absltest

# This is necessary to allow "import six.test_six" to work.
# six sets up custom import loaders and explicitly sets its __path__ to empty,
# which prevents sub-modules from being searched for in other locations.
rootdir = os.path.dirname(six.__file__)
six.__path__.append(rootdir)
import six.test_six
# Remove after we've imported to avoid potential side-effects later on.
six.__path__.pop()


class TestSix(absltest.TestCase):

  def testSix(self):
    # Here we include the default py.test options from six itself, as
    # well as a flag to generate familiar tracebacks.
    # pytest has to be invoked this way because we have to modify six.__path__
    # before pytest tries to run test_six.
    self.assertEqual(
        0,
        pytest.main([
            '-rfsxX',
            '--tb=native',
            '--rootdir=' + rootdir,
            six.test_six.__file__,
        ]),
    )

  def testTkinterImport(self):
    # Throws if the required third_party libraries are not at expected paths.
    from six.moves import tkinter


if __name__ == '__main__':
  absltest.main()
