# Copyright 2017 The Abseil Authors.
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

"""Helper test for absltest_google_env_test.py."""

import os
import sys
import unittest

from absl.testing import absltest


def _is_file_in_dir(file_path: str, prefix_dir: str) -> bool:
  """Determine if a file exists and is under a certain directory."""

  assert os.name != 'nt', 'This function has not been tested on windows'

  file_path = os.path.normpath(file_path)
  prefix_dir = os.path.normpath(prefix_dir)
  common_path = os.path.commonpath([prefix_dir, file_path])
  return os.path.exists(file_path) and common_path == prefix_dir


class HelperTest(absltest.TestCase):

  def test_test_srddir(self):
    self.assertTrue(absltest.TEST_SRCDIR.value.startswith('/'))

  @unittest.skipIf(
      sys.platform == 'darwin',
      "Mac's have a different tmp directory than linux",
  )
  def test_test_tmpdir(self):
    self.assertTrue(
        os.getenv('UNITTEST_ON_BORG', '0') == '1'
        or _is_file_in_dir(absltest.TEST_TMPDIR.value, '/usr/local/google')
    )


if __name__ == '__main__':
  absltest.main()
