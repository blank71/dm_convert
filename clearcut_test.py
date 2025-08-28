import threading
from unittest import mock

import clearcut
import clientanalytics_dmc_pb2
from absl.testing import absltest


_DUMMY_SERIALIZED_PROTO = b'dummy serialzed proto'
_SMALL_BUFFER_SIZE = 11  # No need to use _DEFAULT_BUFFER_SIZE for the tests.
_SMALL_NUMBER_OF_EVENTS = 3  # Should be less than half of _SMALL_BUFFER_SIZE.


def CreateDummyEvent():
  log_event = clientanalytics_dmc_pb2.LogEvent()
  log_event.source_extension = _DUMMY_SERIALIZED_PROTO
  return log_event


class ClearcutTest(absltest.TestCase):

  def setUp(self):
    super(ClearcutTest, self).setUp()
    self.addCleanup(mock.patch.stopall)
    self.mock_urlopen = mock.patch.object(
        clearcut.urllib.request, 'urlopen', autospec=True).start()
    self._InterceptThreads()
    self.mock_response = self._CreateMockResponse()
    self.addCleanup(mock.patch.stopall)

  def tearDown(self):
    # Make sure all threads are finished.
    for t in self._current_threads:
      t.join(1)
      self.assertFalse(t.is_alive())
    super(ClearcutTest, self).tearDown()

  def _InterceptThreads(self):
    real_timer = threading.Timer
    self._current_threads = []

    def FakeTimer(*args, **kwargs):
      timer_thread = real_timer(*args, **kwargs)
      self._current_threads.append(timer_thread)
      return timer_thread

    self.enter_context(mock.patch.object(threading, 'Timer', new=FakeTimer))

  def _CreateMockResponse(self):
    log_response = clientanalytics_dmc_pb2.LogResponse()
    log_response.next_request_wait_millis = 3000
    response_msg = log_response.SerializeToString()

    mock_response = mock.MagicMock()
    mock_read = mock.patch.object(mock_response, 'read').start()
    mock_read.return_value = response_msg
    return mock_response

  def testLogWithFewEvents(self):
    """Log a few events so that a later flush is scheduled."""
    self.client = clearcut.Clearcut(1667, flush_interval_sec=0.1)
    self.mock_urlopen.return_value = self.mock_response

    for _ in range(_SMALL_NUMBER_OF_EVENTS):
      self.client.Log(CreateDummyEvent())

    # Make sure that a later flush is scheduled.
    self.assertLen(self._current_threads, 1)
    self._current_threads[0].join()

    # Verify the call to urlopen and intercept the request.
    self.mock_urlopen.assert_called_once()
    request_args, request_kwargs = self.mock_urlopen.call_args
    request = request_args[0]
    context = request_kwargs.get('context')

    reconstructed_request = clientanalytics_dmc_pb2.LogRequest()
    reconstructed_request.ParseFromString(request.data)
    self.assertGreater(reconstructed_request.request_time_ms, 0)

    events = reconstructed_request.log_event
    self.assertLen(events, _SMALL_NUMBER_OF_EVENTS)
    self.assertEqual(events[0].source_extension, _DUMMY_SERIALIZED_PROTO)
    self.assertGreater(events[0].event_time_ms, 0)
    self.assertIsNotNone(context)

  def testLogAndImmediateFlush(self):
    """Log exactly enough events to schedule an immediate flush."""
    self.client = clearcut.Clearcut(1667, buffer_size=_SMALL_BUFFER_SIZE)

    self.mock_urlopen.return_value = self.mock_response
    nof_events = int(self.client._buffer_size * clearcut._BUFFER_FLUSH_RATIO)
    for _ in range(nof_events):
      self.client.Log(CreateDummyEvent())

    # Only two threads are supposed to be created.
    self.assertLen(self._current_threads, 2)
    # Wait for the scheduled thread to run.
    self._current_threads[-1].join()
    self.assertEmpty(self.client._pending_events)

    # Verify the call to urlopen and intercept the request.
    self.mock_urlopen.assert_called_once()
    request_args, request_kwargs = self.mock_urlopen.call_args
    request = request_args[0]
    context = request_kwargs.get('context')

    reconstructed_request = clientanalytics_dmc_pb2.LogRequest()
    reconstructed_request.ParseFromString(request.data)
    self.assertGreater(reconstructed_request.request_time_ms, 0)

    events = reconstructed_request.log_event
    self.assertLen(events, nof_events)
    self.assertEqual(events[0].source_extension, _DUMMY_SERIALIZED_PROTO)
    self.assertGreater(events[0].event_time_ms, 0)
    self.assertIsNotNone(context)

  def testLogAndClearcutRespondsWith404(self):
    """Log an event, Clearcut responds with 404 and retry sending."""
    self.client = clearcut.Clearcut(1667, buffer_size=1, flush_interval_sec=0.1)

    error = clearcut.urllib.error.HTTPError('', 404, 'Something went wrong!!',
                                            None, None)
    self.mock_urlopen.side_effect = [error, self.mock_response]

    self.client.Log(CreateDummyEvent())
    self.assertLen(self._current_threads, 1)
    self._current_threads[0].join()
    self.assertLen(self.client._pending_events, 1)
    # Make sure retry thread is scheduled.
    self.assertLen(self._current_threads, 2)
    self._current_threads[1].join()

    # Two calls expected: the first attempt and the retry.
    self.mock_urlopen.assert_has_calls([
        mock.call(mock.ANY, context=mock.ANY),
        mock.call(mock.ANY, context=mock.ANY)
    ])

  def testResponseWithNextRequestWaitMillis(self):
    """Honor response.next_request_wait_millis to next request wait time."""
    self.client = clearcut.Clearcut(1667, buffer_size=1, flush_interval_sec=1)

    self.mock_urlopen.return_value = self.mock_response

    self.assertEqual(self.client._min_next_request_time, 0)
    self.client.Log(CreateDummyEvent())

    self.assertLen(self._current_threads, 1)
    self._current_threads[0].join()
    self.assertEqual(self._current_threads[0].interval, 0)
    # Wait for the scheduled thread to run.
    self._current_threads[-1].join()
    self.assertGreater(self.client._min_next_request_time, 0)
    # Make sure a later flush interval change to _min_request_wait_sec.
    self.client.Log(CreateDummyEvent())
    self.assertLen(self._current_threads, 2)
    self._current_threads[1].join()
    self.assertGreater(self._current_threads[1].interval, 1)

    # Two calls expected: the first attempt and the retry.
    self.mock_urlopen.assert_has_calls([
        mock.call(mock.ANY, context=mock.ANY),
        mock.call(mock.ANY, context=mock.ANY)
    ])

  def testRetryOnFailureDisabled(self):
    """Log an event, Clearcut responds with 502, but don't retry sending."""
    self.client = clearcut.Clearcut(
        1667, buffer_size=1, flush_interval_sec=0.1, retry_on_failure=False)

    # Use the mock to simulate an internal server error.
    error = clearcut.urllib.error.HTTPError('', 502, 'Internal server error',
                                            None, None)
    self.mock_urlopen.return_value = error

    self.client.Log(CreateDummyEvent())
    self.assertLen(self._current_threads, 1)
    self._current_threads[0].join()
    self.assertEmpty(self.client._pending_events)
    # Make sure retry thread is not scheduled.
    self.assertLen(self._current_threads, 1)

    # urlopen will be called once (no retry).
    clearcut.urllib.request.urlopen.assert_called_once_with(
        mock.ANY, context=mock.ANY)


if __name__ == '__main__':
  absltest.main()
