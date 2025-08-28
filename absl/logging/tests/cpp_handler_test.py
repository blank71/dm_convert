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

"""Tests for using CppHandler from logging module."""

import logging
import logging.config
import sys
from unittest import mock

from absl import logging as absl_logging
from absl.testing import absltest
from absl.testing import flagsaver

# This needs to be imported for the call to use_cpp_logging to work.
from google3.base.python import pywrapbase  # pylint: disable=unused-import


class _FakeLogSink(pywrapbase.LogSink):
  """Fake log sink to test whether flush is called."""

  def __init__(self):
    self.was_flushed = False
    super().__init__()

  def SendLogEntry(self, log_entry):
    pass

  def Flush(self):
    self.was_flushed = True


class CppHandlerTest(absltest.TestCase):
  """Tests the use of adapter's CppHandler from python logging."""

  def setUp(self):
    mock.patch.object(pywrapbase, 'LogToStderr').start()
    mock.patch.object(pywrapbase, 'SetStderrLogging').start()
    mock.patch.object(pywrapbase, 'SetLogDestination').start()
    mock.patch.object(pywrapbase, 'SetLogSymlink').start()
    mock.patch.object(pywrapbase, 'LogMessageScript').start()
    self.cpp_handler = absl_logging.CppHandler()
    self.record = logging.makeLogRecord({
        'name': 'test',
        'levelno': logging.INFO,
        'pathname': 'source',
        'lineno': 13,
        'msg': 'test',
        'exc_info': None,
    })

  def tearDown(self):
    mock.patch.stopall()

  def test_start_logging_to_file(self):
    with mock.patch.object(absl_logging, 'find_log_dir_and_names') as mock_find:
      mock_find.return_value = ('here', 'prog1', 'prog1')
      self.cpp_handler.start_logging_to_file()
    self.assertEqual(
        [mock.call(pywrapbase.INFO, '%s.INFO.' % 'here/prog1'),
         mock.call(pywrapbase.WARNING, '%s.WARNING.' % 'here/prog1'),
         mock.call(pywrapbase.ERROR, '%s.ERROR.' % 'here/prog1'),
         mock.call(pywrapbase.FATAL, '%s.FATAL.' % 'here/prog1')],
        pywrapbase.SetLogDestination.mock_calls)
    self.assertEqual(
        [mock.call(pywrapbase.INFO, 'prog1'),
         mock.call(pywrapbase.WARNING, 'prog1'),
         mock.call(pywrapbase.ERROR, 'prog1'),
         mock.call(pywrapbase.FATAL, 'prog1')],
        pywrapbase.SetLogSymlink.mock_calls)

  def test_flush(self):
    fake_log_sink = _FakeLogSink()
    pywrapbase.AddLogSink(fake_log_sink)
    # must emit something to ensure that the handler locates pywrapbase,
    # since flush() does nothing if pywrapbase is None.
    self.cpp_handler.emit(self.record)
    self.cpp_handler.flush()
    pywrapbase.RemoveLogSink(fake_log_sink)

    self.assertTrue(fake_log_sink.was_flushed)

  def test_set_google_log_file_no_log_to_stderr(self):
    with mock.patch.object(self.cpp_handler, 'start_logging_to_file'):
      self.cpp_handler.use_absl_log_file()
      self.cpp_handler.start_logging_to_file.assert_called_once_with(
          program_name=None, log_dir=None)

  @flagsaver.flagsaver(logtostderr=True)
  def test_set_google_log_file_with_log_to_stderr(self):
    self.cpp_handler.use_absl_log_file()
    pywrapbase.LogToStderr.assert_called_once()

  def test_emit_fatal_absl(self):
    self.record.levelno = logging.FATAL
    self.record.__dict__[absl_logging._ABSL_LOG_FATAL] = True
    self.cpp_handler.emit(self.record)
    pywrapbase.LogMessageScript.assert_called_once_with(
        'source', 13, 3, 'test')

  def test_emit_fatal_non_absl(self):
    self.record.levelno = logging.FATAL
    self.cpp_handler.emit(self.record)
    pywrapbase.LogMessageScript.assert_called_once_with(
        'source', 13, 2, 'CRITICAL - test')

  def _throw_error(self, unused_record):
    ei = sys.exc_info()
    e = ei[1]
    del ei
    raise e

  def test_cpp_from_stdlib_logging_with_config(self):
    logging.config.dictConfig({
        'version': 1,
        'handlers': {
            'company': {
                'class': 'absl.logging.CppHandler'
            }
        },
        'loggers': {
            'testCpp': {
                'handlers': ['company'],
                'level': 'WARNING'
            }
        }
    })
    with mock.patch.object(
        logging.Handler, 'handleError', new=self._throw_error):
      # If this fails, it will be because CppHandler will have tried to call
      # a method in pywrapbase without having set the global variable
      # correctly. For example:
      # AttributeError: 'NoneType' object has no attribute 'LogMessageScript'
      logging.getLogger('testCpp').warning('this should go through cpp')


if __name__ == '__main__':
  absltest.main()
