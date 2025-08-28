"""Logger of conversion usage data."""

import logging
import time
from typing import Any

import clearcut
import clientanalytics_dmc_pb2
import conversion_logger_setting
import timestamp_pb2
import convert_usage_extension_pb2
import convert_usage_pb2
import strings


def log_input(conversion_format: str, is_config_specified: bool,
              is_project_id_specified: bool, is_project_number_specified: bool,
              is_output_file_specified: bool,
              is_deployment_name_specified: bool):
  """Log the conversion input data.

  Args:
    conversion_format: The value of the conversion format.
    is_config_specified: Whether the config is specified.
    is_project_id_specified: Whether the project_id is specified.
    is_project_number_specified: Whether the project_number is specified.
    is_output_file_specified: Whether the output file is specified.
    is_deployment_name_specified: Whether the deployment name is specified.
  """
  if conversion_format:
    conversion_format_input = convert_usage_pb2.ConversionInput.ConversionFormat.Value(
        conversion_format.upper())
  else:
    conversion_format_input = convert_usage_pb2.ConversionInput.ConversionFormat.FORMAT_UNSPECIFIED
  conversion_input = convert_usage_pb2.ConversionInput(
      conversion_format=conversion_format_input,
      is_config_specified=is_config_specified,
      is_project_id_specified=is_project_id_specified,
      is_project_number_specified=is_project_number_specified,
      is_output_file_specified=is_output_file_specified,
      is_deployment_name_specified=is_deployment_name_specified)
  convert_usage = convert_usage_pb2.ConvertUsage(
      start_time=_get_current_time(), conversion_input=conversion_input)

  log(convert_usage)


def log_success():
  """Log the result of the conversion which succeeds."""
  log_conversion_result(
      status=convert_usage_pb2.ConversionResult.Status.SUCCESS)


def log_error(**kwargs: Any):
  """Log the result of the conversion which fails."""
  log_conversion_result(
      status=convert_usage_pb2.ConversionResult.Status.FAILURE,
      level=convert_usage_pb2.ConversionMessage.Level.ERROR,
      **kwargs)


def log_conversion_result(status: convert_usage_pb2.ConversionResult.Status,
                          **kwargs: Any):
  """Log the conversion results.

  Args:
    status: The final status of the conversion.
    **kwargs: Any more conversion details.

  Returns:
    The result of the conversion.
  """
  conversion_result = convert_usage_pb2.ConversionResult(status=status)

  if status == convert_usage_pb2.ConversionResult.Status.FAILURE:
    conversion_message = conversion_result.conversion_message.add()
    if kwargs.get('error_code'):
      conversion_message.error_code = kwargs.get('error_code')
    if kwargs.get('level'):
      conversion_message.level = kwargs.get('level')
    if kwargs.get('action_name'):
      conversion_message.action_name = _scrub_customized_text(
          kwargs.get('action_name'))
    if kwargs.get('unsupported_type'):
      conversion_message.unsupported_type = _scrub_customized_text(
          kwargs.get('unsupported_type'))
    if kwargs.get('unsupported_reference'):
      conversion_message.unsupported_reference = kwargs.get(
          'unsupported_reference')
    if kwargs.get('exception_type'):
      conversion_message.exception_type = kwargs.get(
          'exception_type')
  convert_usage = convert_usage_pb2.ConvertUsage(
      end_time=_get_current_time(), conversion_result=conversion_result)

  log(convert_usage)


def log(convert_usage: convert_usage_pb2.ConvertUsage):
  """Log the conversion usage telemetry data.

  Args:
    convert_usage: The conversion usage data.
  """
  if not conversion_logger_setting.log_env:
    return

  if convert_usage:
    logging.debug('run_id: %s', conversion_logger_setting.run_id)
    logging.debug('The conversion usage data is: \n%s', convert_usage)

  if not conversion_logger_setting.opt_out_data_collection:
    convert_usage_extension = convert_usage_extension_pb2.ConvertUsageExtension(
        run_id=conversion_logger_setting.run_id, convert_usage=convert_usage)

    convert_usage_event = clientanalytics_dmc_pb2.LogEvent()
    convert_usage_event.source_extension = convert_usage_extension.SerializeToString(
    )

    log_to_clearcut_client(convert_usage_event)


def log_to_clearcut_client(
    convert_usage_event: clientanalytics_dmc_pb2.LogEvent):
  """Build Clearcut client based on the log environment and send logs to Clearcut.

  Args:
    convert_usage_event: The entire convert usage log event to be sent.
  """
  if conversion_logger_setting.log_env == 'prod':
    clearcut_client = clearcut.Clearcut(log_source=1667, buffer_size=1)
    clearcut_client.Log(convert_usage_event)
    logging.debug('Logs successfully sent.')
  elif conversion_logger_setting.log_env == 'dev':
    logging.debug('In the Development mode')
    clearcut_client = clearcut.Clearcut(log_source=1741, buffer_size=1)
    clearcut_client.Log(convert_usage_event)
    logging.debug('Logs successfully sent.')
  else:
    logging.warning(
        'Failed to send logs because the log environment variable %s is invalid.',
        conversion_logger_setting.log_env)


def _get_current_time() -> timestamp_pb2.Timestamp:
  now = time.time()
  seconds = int(now)
  nanos = int((now - seconds) * 10**9)
  now_timestamp = timestamp_pb2.Timestamp(seconds=seconds, nanos=nanos)
  return now_timestamp


def _scrub_customized_text(text: str) -> str:
  """Scrub the non DM GCP types/actions or non DM legacy types and replace it with 'customized'.

  Args:
    text: The text to check.

  Returns:
    The text where customized text is scrubbed.
  """
  if strings.is_gcp_types_actions(text) or strings.is_legacy_types(text):
    return text
  return 'customized'
