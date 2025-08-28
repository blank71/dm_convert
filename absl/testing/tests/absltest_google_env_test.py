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

"""Google3 specific tests for absltest."""

import os
import subprocess

from absl.testing import _bazelize_command
from absl.testing import absltest


class GoogleEnvTest(absltest.TestCase):

  def test_flag_values_without_env(self):
    helper_name = 'absl/testing/tests/absltest_google_env_test_helper'
    helper = _bazelize_command.get_executable_path(helper_name)
    env = os.environ.copy()
    for key in ('TEST_SRCDIR', 'TEST_TMPDIR'):
      del env[key]
    process = subprocess.Popen(
        [helper],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
    )
    stdout, stderr = process.communicate()
    self.assertEqual(
        0, process.returncode,
        'Expected success, but failed with '
        'stdout:\n{}\nstderr:\n{}\n'.format(stdout, stderr))


if __name__ == '__main__':
  absltest.main()
