"""Main entry point for dm_convert CLI.

Takes DM config and output_format and outputs converted config to STDOUT/file.
"""

import os
import pathlib
import pprint
import sys
import traceback
from typing import Optional
import uuid

from absl import app
from absl import flags
from absl import logging

import conversion_logger
import conversion_logger_setting
import errors
import resource_reader
import template_resolver
from converter_runner import ConverterRunner
from errors import UnsupportedFormatError
from krm_converter import KrmConverter
from tf_converter import TerraformConverter
import convert_usage_pb2

_KRM_FORMAT = 'KRM'
_TF_FORMAT = 'TF'

_DATA_COLLECTED = (
    'The data Google collects is anonymous, and excludes'
    ' any Personally Identifiable Information, Sensitive'
    ' Personally Identifiable Information, or Business '
    'Data. Google uses the collected data for improving '
    'the tool.'
)

_DATA_COLLECTION_HELP_GUIDE = (
    'the flag --opt_out_data_collection when you '
    'next run a command. For help text for the data '
    'collection flag, use the flag --help or refer '
    'to the User Guide.'
)

_OUTPUT_FORMAT = flags.DEFINE_enum(
    name='output_format',
    default=_TF_FORMAT,
    enum_values=[_KRM_FORMAT, _TF_FORMAT],
    help=(
        'Destination format for converted output. Currently '
        'supported formats are KRM and TF(Terraform).'
    ),
    case_sensitive=False,
)

_CONFIG = flags.DEFINE_string(
    'config', None, 'Deployment Manager root configuration file to convert.'
)

_LAYOUT_FILE = flags.DEFINE_string(
    'layout_file',
    None,
    'Optional layout file.If empty, does not do template conversion',
)

_WITHOUT_DEPLOYMENT = flags.DEFINE_bool(
    'without_deployment',
    False,
    'Optional flag. If true, read layout contentfrom the expansion service',
)

_OUTPUT_FILE = flags.DEFINE_string(
    'output_file',
    None,
    (
        'Optional destination file for converted output.'
        ' If empty, generated output is printed to STDOUT.'
    ),
)

_OUTPUT_TF_IMPORT_FILE = flags.DEFINE_string(
    'output_tf_import_file',
    None,
    (
        'Optional destination file for Terraform import commands.'
        ' If empty, no output file is generated.'
    ),
)

_PROJECT_ID = flags.DEFINE_string(
    'project_id',
    None,
    (
        'GCP project ID. Set this value if you are using '
        'env["project"] in our DM templates, or when converting to'
        ' KRM if you want to explicitly configure the KRM '
        'namespace for converted resources. A randomly generated '
        'string will be used if not specified. If the value is set when '
        'converting to TF and output_tf_import_file option is used, '
        'the project_id will be used to generate tf import statements when '
        'resource`s project_id reference was not explicitly provided.'
    ),
)

_PROJECT_NUMBER = flags.DEFINE_integer(
    'project_number',
    0,
    (
        'GCP project number. Set this value if you are using '
        'env["project_number"] in our DM templates.'
    ),
)

_DEPLOYMENT_NAME = flags.DEFINE_string(
    'deployment_name',
    None,
    (
        'Set this value if env["deployment"] from DM templates is '
        'being used. A randomly generated string will be used if '
        'not specified.'
    ),
)

_OPT_OUT_DATA_COLLECTION = flags.DEFINE_bool(
    'opt_out_data_collection',
    None,
    'Set to true in order to opt out usage data collection from the tool.',
)

_SKIP_UNSUPPORTED_FIELDS = flags.DEFINE_bool(
    'skip_unsupported_fields',
    False,
    (
        'Set to true in order to continue conversion even if fields '
        'are found which are not supported by output configs.'
    ),
)

_LIST_SUPPORTED_TYPES = flags.DEFINE_bool(
    'list_supported_types',
    False,
    (
        'Prints the list of supported resource types for the '
        'given --output_format.'
    ),
)

_LICENSES = flags.DEFINE_bool(
    'licenses',
    False,
    'Show third party licenses for packages used by the tool.',
)

_VERBOSE = flags.DEFINE_bool('verbose', None, 'Enable verbose logging')

_QUIET = flags.DEFINE_bool('quiet', None, 'Only log warnings and above')

_TF_PROVIDER = flags.DEFINE_string(
    'tf_provider',
    'google-beta',
    (
        'Set provider which will be used due terraform conversion.'
        '"google-beta" value is set by default.'
    ),
)


def get_converter(
    output_format: str,
    skip_unsupported_fields: bool,
    templates_dir: Optional[pathlib.Path] = None,
    tf_import_file: Optional[pathlib.Path] = None,
    project_id: Optional[str] = None,
    layout_file: Optional[pathlib.Path] = None,
):
  """Creates a converter instance for the given output format.

  Args:
    output_format: Sets output format type, either KRM or Terraform.
    skip_unsupported_fields: Indicates if converter should skip unsupported
      fields instead of raises an error.
    templates_dir: Sets directory jinja templates for conversion.
    tf_import_file: Optional output file to tf import commands.
    project_id: Optional project_id passed into the DM Convert tool.
    layout_file: Optional Layout file passed into the DM Convert tool.

  Returns:
    Converter implementation.

  Raises:
    UnsupportedFormatError: An error occurred when output_format is unsupported.
  """
  if output_format == _KRM_FORMAT:
    if templates_dir is None:
      templates_dir = resource_reader.get_templates_dir('krm')
    return KrmConverter(
        templates_dir=templates_dir,
        template_resolver=template_resolver.get_instance('krm', templates_dir),
        project_id=None,
        skip_unsupported_fields=skip_unsupported_fields)
  elif output_format == _TF_FORMAT:
    if templates_dir is None:
      templates_dir = resource_reader.get_templates_dir('tf')
    return TerraformConverter(
        templates_dir=templates_dir,
        template_resolver=template_resolver.get_instance('tf', templates_dir),
        project_id=project_id,
        skip_unsupported_fields=skip_unsupported_fields,
        provider=_TF_PROVIDER.value,
        tf_import_file=tf_import_file,
        layout_file=layout_file,
        without_deployment_flag=_WITHOUT_DEPLOYMENT.value)
  else:
    raise UnsupportedFormatError(
        f'The format "{output_format}" is not supported. Only KRM or TF are supported.'
    )


def except_hook(kind, message, tb):
  """Handles how exceptions are shown to the user.

  Args:
    kind: Exception type.
    message: Exception message.
    tb: Exception traceback.
  """
  if errors.ConverterError in kind.__bases__:
    logging.error('%s: %s', kind.__name__, message)

  else:
    conversion_logger.log_error(error_code=convert_usage_pb2.ConversionMessage
                                .ErrorCode.SYSTEM_ERROR_UNHANDLED_EXCEPTION,
                                exception_type=kind.__name__)
    logging.error('Unhandled exception: "%s": "%s". Traceback:\n%s',
                  kind.__name__, message,
                  ''.join(traceback.format_tb(tb)))


def _print_supported_types(types: set[str], actions: set[str]):
  """Pretty-print types and actions supported by this converter.

  Args:
    types: Set of types e.g.
      {'gcp-types/cloudkms-v1:projects.locations.keyRings'}
    actions: Set of actions e.g. {'gcp-types/dns-v1:dns.changes.create}
  """
  groups = {'GCP Type Providers': list(), 'Resource Types': list()}
  for t in types:
    if t.startswith('gcp-types'):
      groups['GCP Type Providers'].append(t)
    else:
      groups['Resource Types'].append(t)

  if actions:
    groups['Actions'] = actions

  pprint.pprint({k: sorted(v) for k, v in groups.items()})


def _get_data_collection_policy(flag_specified: bool, opt_out_value: bool):
  """Prints Data Collection Policy to the user.

  Args:
    flag_specified: whether the opt_out_data_collection flag is specified.
    opt_out_value: the bool value of opt_out_data_collection flag.

  Returns:
    The Data Collection Policy.
  """
  if flag_specified:
    data_collection_policy = (
        f'Because you specified --opt_out_data_collection={opt_out_value}'
        ' in your command, the tool will' + (' not' if opt_out_value else '') +
        ' collect usage data to send to Google for this current execution. '
        f'{_DATA_COLLECTED}'
        ' To change your data collection preference, specify a different '
        f'value for {_DATA_COLLECTION_HELP_GUIDE}')
  else:
    data_collection_policy = (
        'This tool collects usage data upon execution and sends that data '
        f'to Google. {_DATA_COLLECTED}'
        ' To disable this data collection, include '
        f'{_DATA_COLLECTION_HELP_GUIDE}')
  return data_collection_policy


def main(argv) -> None:
  del argv  # unused

  # overwrite log level if specified
  if _VERBOSE.value:
    logging.set_verbosity(logging.DEBUG)
  elif _QUIET.value:
    logging.set_verbosity(logging.ERROR)

  data_collection_policy = _get_data_collection_policy(
      _OPT_OUT_DATA_COLLECTION.value is not None,
      _OPT_OUT_DATA_COLLECTION.value)
  logging.info(data_collection_policy)

  conversion_logger_setting.init(
      str(uuid.uuid4()), _OPT_OUT_DATA_COLLECTION.value,
      os.getenv('GOOGLE_DM_CONVERT_LOG_ENV'))

  # record the conversion input
  conversion_logger.log_input(
      conversion_format=_OUTPUT_FORMAT.value,
      is_config_specified=_CONFIG.value is not None,
      is_project_id_specified=_PROJECT_ID.value is not None,
      is_project_number_specified=_PROJECT_NUMBER.value != 0,
      is_output_file_specified=_OUTPUT_FILE.value is not None,
      is_deployment_name_specified=_DEPLOYMENT_NAME.value is not None)

  if _LICENSES.value:
    path = resource_reader.get_license_file()
    print(path.read_text(encoding='utf-8'))
    return

  if _OUTPUT_FORMAT.value == _KRM_FORMAT and _OUTPUT_TF_IMPORT_FILE.value is not None:
    print('Flag --output_tf_import_file cannot be used for KRM output.')
    return

  if _OUTPUT_FORMAT.value is None:
    print('Flag --output_format must have a value other than None.')
    return

  tf_import_file = None
  if _OUTPUT_TF_IMPORT_FILE.value:
    tf_import_file = pathlib.Path(
        _OUTPUT_TF_IMPORT_FILE.value).resolve(strict=False)

  # The flag "log_dir" is defined in the absl.logging. If a non-empty directory
  # is specified for the flag "log_dir", absl.logging logs will be written to
  # the specified directory.
  if flags.FLAGS.log_dir:
    logging.get_absl_handler().use_absl_log_file()

  layout_file = None
  if _LAYOUT_FILE.value:
    layout_file = pathlib.Path(_LAYOUT_FILE.value).resolve(strict=False)
    if not layout_file.is_file():
      raise FileNotFoundError(
          f'--layout file "{str(layout_file)}" does not exist or cannot be'
          ' accessed.'
      )

  converter = get_converter(
      _OUTPUT_FORMAT.value,
      _SKIP_UNSUPPORTED_FIELDS.value,
      tf_import_file=tf_import_file,
      project_id=_PROJECT_ID.value,
      layout_file=layout_file
  )

  sys.excepthook = except_hook

  if _LIST_SUPPORTED_TYPES.value:
    _print_supported_types(
        converter.get_supported_types(), converter.get_supported_actions()
    )
    return

  if _CONFIG.value is None:
    # This case might happen when list_supported_types set to false
    # but config is required for rest of operations
    raise Exception('Missing value for required flag --config.')

  config_file = pathlib.Path(_CONFIG.value)
  if not config_file.is_file():
    raise FileNotFoundError(
        f'--config file "{str(config_file)}" does not exist or cannot be accessed.'
    )

  output_file = None
  if _OUTPUT_FILE.value:
    output_file = pathlib.Path(_OUTPUT_FILE.value).resolve(strict=False)

  runner = ConverterRunner(
      config_file=pathlib.Path(_CONFIG.value).resolve(),
      output_file=output_file,
      namespace='',
      project_id=_PROJECT_ID.value,
      project_number=_PROJECT_NUMBER.value,
      deployment_name=_DEPLOYMENT_NAME.value,
      converter=converter)
  runner.run()


if __name__ == '__main__':
  flags.mark_flags_as_required(['output_format'])
  flags.mark_flags_as_mutual_exclusive(
      flag_names=['verbose', 'quiet'], required=False)
  flags.register_validator(
      'tf_provider',
      lambda value: value,
      message='Value is required.')

  app.run(main)
