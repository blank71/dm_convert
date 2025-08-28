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

"""Tests for GOOGLE_LOGTOSTDERR and GOOGLE_ALSOLOGTOSTDERR support."""

import os
import random
import subprocess

from absl.testing import _bazelize_command
from absl.testing import absltest


class LogtostderrEnvironment(absltest.TestCase):

  HELPER_TYPE = 'clif'

  def _random_canary(self, outlen=32):
    s = ''
    for _ in range(outlen):
      s += random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
    return s

  def _run_subprocess(self, canary):
    helper = _bazelize_command.get_executable_path(
        f'absl/logging/tests/google_env_test_helper_{self.HELPER_TYPE}'
    )
    args = [helper, '--name=%s' % canary]
    proc = subprocess.Popen(args, stderr=subprocess.PIPE, text=True)
    unused_stdoutdata, stderrdata = proc.communicate()
    return stderrdata

  def test_none(self):
    if os.getenv('GOOGLE_LOGTOSTDERR'):
      del os.environ['GOOGLE_LOGTOSTDERR']
    if os.getenv('GOOGLE_ALSOLOGTOSTDERR'):
      del os.environ['GOOGLE_ALSOLOGTOSTDERR']

    canary = self._random_canary()
    res = self._run_subprocess(canary)
    self.assertNotIn(canary, res)

  def test_all(self):
    os.environ['GOOGLE_LOGTOSTDERR'] = 'True'
    os.environ['GOOGLE_ALSOLOGTOSTDERR'] = 'True'

    canary = self._random_canary()
    res = self._run_subprocess(canary)
    self.assertIn(canary, res)

  def test_log(self):
    os.environ['GOOGLE_LOGTOSTDERR'] = 'True'
    if os.getenv('GOOGLE_ALSOLOGTOSTDERR'):
      del os.environ['GOOGLE_ALSOLOGTOSTDERR']

    canary = self._random_canary()
    res = self._run_subprocess(canary)
    self.assertIn(canary, res)

  def test_alsolog(self):
    if os.getenv('GOOGLE_LOGTOSTDERR'):
      del os.environ['GOOGLE_LOGTOSTDERR']
    os.environ['GOOGLE_ALSOLOGTOSTDERR'] = 'True'

    canary = self._random_canary()
    res = self._run_subprocess(canary)
    self.assertIn(canary, res)


if __name__ == '__main__':
  absltest.main()
