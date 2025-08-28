"""Python client library to write logs to Clearcut (see go/clearcut).

This class is intended to be general-purpose, usable for any Clearcut LogSource.

Design Doc: go/clearcutpythonlibrary


  Typical usage example:

  client = clearcut_client = clearcut.Clearcut(
      clientanalytics_dmc_pb2.LogRequest.MY_LOGSOURCE)
  clent.Log(my_event)
"""

# b/155389497 workaround to avoid LookupError: unknown encoding: idna
import encodings.idna  # pylint: disable=unused-import
import ssl
import threading
import time
import urllib

from absl import flags
from absl import logging

import clientanalytics_dmc_pb2
import resource_reader
from google.protobuf import message

_DISABLE_THROTTLING = flags.DEFINE_bool(
    'disable_throttling', False, 'Disables automatic throttling [DANGEROUS]')

_CLEARCUT_PROD_URL = 'https://play.googleapis.com/log'
_DEFAULT_BUFFER_SIZE = 1000  # Maximum number of events to be buffered.
_DEFAULT_FLUSH_INTERVAL_SEC = 60  # 1 Minute.
_BUFFER_FLUSH_RATIO = 0.5  # Flush buffer when we exceed this ratio.
_CAFILE_RESOURCE = 'certs/roots.pem'


class ClearcutError(Exception):  # pylint: disable=g-bad-exception-name
  """Exception class for unsuccessful send requests to Clearcut.

  Attributes:
    retry: A boolean indicating if we will retry sending after the error.
  """

  def __init__(self, retry):
    """Initializes a ClearcutError.

    Args:
      retry: Whether we want to retry sending after this error (boolean).
    """
    Exception.__init__(self)
    self.retry = retry

  def __str__(self):
    """Returns a string representation of the error."""
    return 'retry: %r' % self.retry


class Clearcut(object):
  """Handles logging to Clearcut."""

  def __init__(self,
               log_source,
               get_token=None,
               url=None,
               buffer_size=None,
               flush_interval_sec=None,
               retry_on_failure=True):
    """Initializes a Clearcut client.

    Args:
      log_source: The log source.
      get_token: A function that returns an OAuth 2.0 berear token (aka access
        token). This is not required but without it the logs will not have GAIA
        IDs. The token must have the scope
          'https://www.googleapis.com/auth/cclog'.
      url: The Clearcut url to connect to.
      buffer_size: The size of the client buffer in number of events.
      flush_interval_sec: The flush interval in seconds.
      retry_on_failure: Whether to retry sending the log request on failure.
    """
    self._clearcut_url = url if url else _CLEARCUT_PROD_URL
    self._log_source = log_source
    self._get_token = get_token
    self._buffer_size = buffer_size if buffer_size else _DEFAULT_BUFFER_SIZE
    self._pending_events = []
    if flush_interval_sec:
      self._flush_interval_sec = flush_interval_sec
    else:
      self._flush_interval_sec = _DEFAULT_FLUSH_INTERVAL_SEC
    self._pending_events_lock = threading.Lock()
    self._retry_on_failure = retry_on_failure
    self._scheduled_flush_thread = None
    self._scheduled_flush_time = float('inf')
    self._min_next_request_time = 0

  def Log(self, event):
    """Logs events to Clearcut.

    Logging an event can potentially trigger a flush of queued events. Flushing
    is triggered when the buffer is more than half full or after the flush
    interval has passed.
    This function also sets the event_time_ms field to current time.

    Args:
      event: A LogEvent to send to Clearcut.
    """
    event.event_time_ms = int(round(time.time() * 1000))  # Add timestamps.
    self._AppendEventsToBuffer([event])

  def _SerializeEventsToProto(self, events):
    log_request = clientanalytics_dmc_pb2.LogRequest()
    log_request.request_time_ms = int(time.time() * 1000)
    log_request.client_info.client_type = clientanalytics_dmc_pb2.ClientInfo.PYTHON
    log_request.log_source = self._log_source
    log_request.log_event.extend(events)
    return log_request

  def _AppendEventsToBuffer(self, events, retry=False):
    with self._pending_events_lock:
      self._pending_events.extend(events)
      if len(self._pending_events) > self._buffer_size:
        index = len(self._pending_events) - self._buffer_size
        del self._pending_events[:index]
      self._ScheduleFlush(retry)

  def _ScheduleFlush(self, retry):
    """Schedules flushing at intervals or when buffer exceeds flushing ratio."""
    if (not retry and len(self._pending_events) >= int(
        self._buffer_size * _BUFFER_FLUSH_RATIO) and
        self._scheduled_flush_time > time.time()):
      # Cancel whatever is scheduled and schedule an immediate flush.
      if self._scheduled_flush_thread:
        self._scheduled_flush_thread.cancel()
      self._ScheduleFlushThread(0)
    elif self._pending_events and not self._scheduled_flush_thread:
      # Schedule a flush to run later.
      self._ScheduleFlushThread(self._flush_interval_sec)

  def _ScheduleFlushThread(self, time_from_now):
    wall_time = time.time()
    min_wait_sec = self._min_next_request_time - wall_time
    if min_wait_sec > time_from_now:
      time_from_now = min_wait_sec
    logging.debug('Scheduling thread to run in %f seconds', time_from_now)
    self._scheduled_flush_thread = threading.Timer(time_from_now, self._Flush)
    self._scheduled_flush_time = wall_time + time_from_now
    self._scheduled_flush_thread.start()

  def _Flush(self):
    """Flush buffered events to Clearcut.

    If the send request is unsuccessful the events are added back to the buffer
    to go out with the next scheduled flush.
    """
    with self._pending_events_lock:
      self._scheduled_flush_time = float('inf')
      self._scheduled_flush_thread = None
      events = self._pending_events
      self._pending_events = []
    if self._min_next_request_time > time.time():
      self._AppendEventsToBuffer(events, retry=True)
      return

    log_request = self._SerializeEventsToProto(events)

    token = self._get_token() if self._get_token else None
    try:
      self._SendToClearcut(log_request.SerializeToString(), token=token)
    except ClearcutError as e:
      if self._retry_on_failure and e.retry:
        self._AppendEventsToBuffer(events, retry=True)

  def _SendToClearcut(self, data, token=None):
    """Sends a POST request with data as the body.

    Args:
      data: The serialized proto to send to Clearcut.
      token: An OAuth 2.0 berear token to authenticate with the Clearcut server.
    """
    request = urllib.request.Request(self._clearcut_url, data=data)
    if token:
      request.add_header('Authorization', 'Bearer ' + self._EnsureStr(token))
    else:
      logging.debug('No access token given, GAIA ID will not be logged.')
    try:
      response = urllib.request.urlopen(
          request,
          context=self._ConnectToGoogleSSLContext(cafile=_CAFILE_RESOURCE))
    except urllib.error.HTTPError as e:
      logging.exception('Failed to push events to Clearcut. Error code: %d',
                        e.code)
      raise ClearcutError(e.code >= 400)
    except urllib.error.URLError:
      logging.exception('Failed to push events to Clearcut.')
      raise ClearcutError(False)
    try:
      msg = response.read()
      logging.debug('LogRequest successfully sent to Clearcut.')
      log_response = clientanalytics_dmc_pb2.LogResponse()
      try:
        log_response.ParseFromString(msg)
        # Throttle based on next_request_wait_millis value.
        if not _DISABLE_THROTTLING.value:
          self._min_next_request_time = (
              log_response.next_request_wait_millis // 1000 + time.time())
        logging.debug('LogResponse: %s', log_response)
      except message.DecodeError as e:
        # We do not intend to retry if the response is not parsable.
        logging.exception('Cannot decode Clearcut response: %s', e)
        raise ClearcutError(False)

    except IOError as e:
      logging.exception(e)
      raise ClearcutError(False)

  def _EnsureStr(self, str_or_bytes):
    """Returns a string representation of the object.

    Replicates six.ensure_str for python3 only

    Args:
      str_or_bytes: string or utf-8 encoded string as bytes.
    """
    if isinstance(str_or_bytes, str):
      return str_or_bytes
    else:
      return str(str_or_bytes, 'utf-8')

  def _ConnectToGoogleSSLContext(self, cafile):
    """Returns text content of the certificate.

    Args:
      cafile: the certificate file that allows connection to the target TLS
        service.
    """
    cadata = resource_reader.read_resource_utf8(
        file=resource_reader.get_base_dir().joinpath(cafile))
    return ssl.create_default_context(cadata=self._EnsureStr(cadata))
