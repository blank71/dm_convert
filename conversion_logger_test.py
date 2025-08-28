from unittest import mock

import clearcut
import conversion_logger
import conversion_logger_setting
import convert_usage_extension_pb2
import convert_usage_pb2
from absl.testing import absltest
from absl.testing import parameterized


class TelemetryHelperTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.mock_clearcut_log = mock.patch.object(
        clearcut.Clearcut, 'Log', return_value=None).start()

  def tearDown(self):
    super().tearDown()
    mock.patch.stopall()

  def test_log_input(self):
    conversion_logger_setting.init('test_run_id', None, 'dev')
    conversion_logger.log_input(
        conversion_format='KRM',
        is_config_specified=True,
        is_project_id_specified=False,
        is_project_number_specified=False,
        is_output_file_specified=True,
        is_deployment_name_specified=True)
    log_event_args = self.mock_clearcut_log.call_args[0]
    log_event = log_event_args[0]
    actual_input = convert_usage_extension_pb2.ConvertUsageExtension.FromString(
        log_event.source_extension).convert_usage.conversion_input

    self.assertEqual(actual_input.conversion_format,
                     convert_usage_pb2.ConversionInput.ConversionFormat.KRM)
    self.assertTrue(actual_input.is_config_specified)
    self.assertFalse(actual_input.is_project_id_specified)
    self.assertFalse(actual_input.is_project_number_specified)
    self.assertTrue(actual_input.is_output_file_specified)
    self.assertTrue(actual_input.is_deployment_name_specified)

  def test_log_success(self):
    conversion_logger_setting.init('test_run_id', None, 'dev')
    conversion_logger.log_success()
    log_event_args = self.mock_clearcut_log.call_args[0]
    log_event = log_event_args[0]
    actual_result = convert_usage_extension_pb2.ConvertUsageExtension.FromString(
        log_event.source_extension).convert_usage.conversion_result

    self.assertEqual(actual_result.status,
                     convert_usage_pb2.ConversionResult.Status.SUCCESS)

  def test_log_failure(self):
    conversion_logger_setting.init('test_run_id', None, 'dev')
    conversion_logger.log_error(error_code=convert_usage_pb2.ConversionMessage
                                .ErrorCode.USER_ERROR_UNSUPPORTED_REFERENCE)
    log_event_args = self.mock_clearcut_log.call_args[0]
    log_event = log_event_args[0]
    actual_result = convert_usage_extension_pb2.ConvertUsageExtension.FromString(
        log_event.source_extension).convert_usage.conversion_result

    self.assertEqual(actual_result.status,
                     convert_usage_pb2.ConversionResult.Status.FAILURE)
    self.assertLen(actual_result.conversion_message, 1)

    actual_message = actual_result.conversion_message[0]

    self.assertEqual(actual_message.level,
                     convert_usage_pb2.ConversionMessage.Level.ERROR)
    self.assertEqual(
        actual_message.error_code, convert_usage_pb2.ConversionMessage.ErrorCode
        .USER_ERROR_UNSUPPORTED_REFERENCE)

  def test_opt_out_none_log_to_clearcut(self):
    conversion_logger_setting.init('test_run_id', None, 'dev')
    conversion_logger.log(convert_usage_pb2.ConvertUsage())
    self.assertTrue(self.mock_clearcut_log.called)

  def test_opt_out_false_log_to_clearcut(self):
    conversion_logger_setting.init('test_run_id', False, 'dev')
    conversion_logger.log(convert_usage=convert_usage_pb2.ConvertUsage())
    self.assertTrue(self.mock_clearcut_log.called)

  def test_opt_out_true_client_logging(self):
    conversion_logger_setting.init('test_run_id', True, 'dev')
    conversion_logger.log(convert_usage=convert_usage_pb2.ConvertUsage())
    self.assertFalse(self.mock_clearcut_log.called)

  def test_scrub_customized_type(self):
    test_type = 'my-types:my-collection'
    self.assertEqual(
        conversion_logger._scrub_customized_text(test_type), 'customized')

  def test_not_scrub_gcp_type(self):
    test_type = 'gcp-types/cloudfunctions-v1:virtual.projects.locations.functions.iamMemberBinding'
    self.assertEqual(
        conversion_logger._scrub_customized_text(test_type), test_type)


if __name__ == '__main__':
  absltest.main()
