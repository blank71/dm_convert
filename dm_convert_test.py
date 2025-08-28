import contextlib
import io
import sys
from unittest import mock

from absl.testing import absltest
from absl.testing import flagsaver

import dm_convert
import errors
from absl.testing import absltest
from absl.testing import parameterized

_DATA_COLLECTION_POLICY_OPT_OUT = ('Because you specified '
                                   '--opt_out_data_collection=True in your '
                                   'command, the tool will not collect usage '
                                   'data to send to Google for this current '
                                   'execution. The data Google collects is '
                                   'anonymous, and excludes any Personally '
                                   'Identifiable Information, Sensitive '
                                   'Personally Identifiable Information, or '
                                   'Business Data. Google uses the collected '
                                   'data for improving the tool. To change your'
                                   ' data collection preference, specify a '
                                   'different value for the flag '
                                   '--opt_out_data_collection when you next run'
                                   ' a command. For help text for the data '
                                   'collection flag, use the flag --help or '
                                   'refer to the User Guide.')

_DATA_COLLECTION_POLICY_DEFAULT = ('This tool collects usage data upon '
                                   'execution and sends that data to Google. '
                                   'The data Google collects is anonymous, and '
                                   'excludes any Personally Identifiable '
                                   'Information, Sensitive Personally '
                                   'Identifiable Information, or Business Data.'
                                   ' Google uses the collected data for '
                                   'improving the tool. To disable this data '
                                   'collection, include the flag '
                                   '--opt_out_data_collection when you next run'
                                   ' a command. For help text for the data '
                                   'collection flag, use the flag --help or '
                                   'refer to the User Guide.')


class DmConvertTest(parameterized.TestCase, absltest.TestCase):

  @parameterized.named_parameters(
      {
          'testcase_name': 'krm_format',
          'output_format': 'KRM'
      }, {
          'testcase_name': 'terraform_format',
          'output_format': 'TF'
      })
  def test_flag_list_supported_types_with(self, output_format: str):
    runtime_flags = {
        'list_supported_types': True,
        'output_format': output_format,
    }
    with flagsaver.flagsaver(**runtime_flags):
      with mock.patch('pprint.pprint') as mock_print:
        dm_convert.main(None)

    actual = [call[0][0] for call in mock_print.call_args_list]

    self.assertIsNotNone(actual)

  def test_tf_import_flag(self):
    runtime_flags = {'output_tf_import_file': '/some/path',
                     'config': 'some/config',
                     'output_format': 'KRM'}
    with flagsaver.flagsaver(**runtime_flags):
      with mock.patch('builtins.print') as mock_print:
        dm_convert.main(None)

    lines = [call[0][0] for call in mock_print.call_args_list]
    actual = ''.join(lines)

    self.assertTrue(_is_not_none_or_empty(actual))

  def test_flag_licenses(self):
    runtime_flags = {'licenses': True}
    with flagsaver.flagsaver(**runtime_flags):
      with mock.patch('builtins.print') as mock_print:
        dm_convert.main(None)

    lines = [call[0][0] for call in mock_print.call_args_list]
    actual = ''.join(lines)

    self.assertTrue(_is_not_none_or_empty(actual))

  def test_get_data_collection_policy_opt_out(self):
    actual = dm_convert._get_data_collection_policy(True, True)
    self.assertEqual(actual, _DATA_COLLECTION_POLICY_OPT_OUT)

  def test_get_data_collection_policy_default(self):
    actual = dm_convert._get_data_collection_policy(False, None)
    self.assertEqual(actual, _DATA_COLLECTION_POLICY_DEFAULT)


def _is_not_none_or_empty(string):
  return bool(string and string.strip())


class ErrorsTest(absltest.TestCase):

  def test_excepthook(self):
    err = io.StringIO()
    try:
      raise errors.UnsupportedReferenceError('Custom message')
    except errors.UnsupportedReferenceError:
      except_hook_args = sys.exc_info()

    sys.excepthook = dm_convert.except_hook
    with contextlib.redirect_stderr(err):
      sys.excepthook(*except_hook_args)
    self.assertRegex(
        err.getvalue(), r'^E.*dm_convert.py:\d+] '
        r'UnsupportedReferenceError: Custom message\n$')


if __name__ == '__main__':
  absltest.main()
