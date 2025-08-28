"""Converts DM configs to KRM and Terraform formats."""

import pathlib
import time
from typing import Any, Optional

from absl import logging
import yaml

from expansion import expansion
import base_converter
import conversion_logger
import errors
import convert_usage_pb2


class ConverterRunner(object):
  """Reads DM config, expands it, and runs conversion."""

  def __init__(self, config_file: pathlib.Path,
               output_file: Optional[pathlib.Path], namespace: str,
               project_id: str, project_number: int, deployment_name: str,
               converter: base_converter.BaseConverter):
    self._converter = converter
    self._config_file = config_file
    self._output_file = output_file
    self._namespace = namespace
    self._project_id = project_id
    self._project_number = project_number
    self._deployment_name = deployment_name

  def _load_config(self) -> str:
    logging.info('Reading DM config from file: %s', self._config_file)
    try:
      return expansion.ReadFileToString(self._config_file)
    except IOError:
      raise errors.InputFileNotFoundError from IOError(
          f'--config file "{self._config_file.absolute()}" does not exist or'
          ' cannot be accessed.'
      )

  def _expand_config_and_layout(self, config_string: str):
    """Builds expanded config."""
    env = {}
    imports = {}
    if self._deployment_name:
      env['deployment'] = self._deployment_name
    if self._project_id:
      env['project'] = self._project_id
    if self._project_number > 0:
      env['project_number'] = self._project_number
    env['current_time'] = int(time.time())
    try:
      loaded_config = yaml.safe_load(config_string)
    except (yaml.parser.ParserError, yaml.scanner.ScannerError) as e:
      conversion_logger.log_error(error_code=convert_usage_pb2.ConversionMessage
                                  .ErrorCode.USER_ERROR_CORRUPTED_INPUT)
      raise errors.CorruptedInputError(
          f'The input file does not contain valid yaml: {e}')
    try:
      expansion.BuildImports(
          imports=imports,
          config=loaded_config,
          working_dir=pathlib.Path(''),
          config_dir=self._config_file.parent)
      # The tool is used for client side expansion, thus `restrict_open = False`
      # meaning expansion will not redefine `open` in `sandbox_loader.py`
      expanded = expansion.Expand(
          config_string, imports, env=env, restrict_open=False)
      yaml_content = yaml.safe_load(expanded)
      return yaml_content.get('config'), yaml_content.get('layout')
    except Exception as e:
      conversion_logger.log_error(error_code=convert_usage_pb2.ConversionMessage
                                  .ErrorCode.USER_ERROR_EXPANSION_FAILED)
      raise errors.ExpansionFailedError(
          'Expansion error encountered evaluating input: ' + str(e))

  def _parse_resources(
      self, expanded_config: dict[str, Any]
  ) -> list[dict[str, Any]]:
    """The loaded _resource object type is dict[str, Any], value could be str and dict types."""
    if 'resources' in expanded_config:
      return expanded_config['resources']
    else:
      conversion_logger.log_error(error_code=convert_usage_pb2.ConversionMessage
                                  .ErrorCode.USER_ERROR_CORRUPTED_INPUT)
      raise errors.NoResourcesFoundError(
          'Empty config or no resources found in DM config.')

  def run(self):
    """Runs DM converter."""
    config_string = self._load_config()
    expanded_config, layout = self._expand_config_and_layout(config_string)

    resources = self._parse_resources(expanded_config)
    converted_config = self._converter.convert(
        resources=resources, namespace=self._namespace, layout=layout)
    if self._output_file is None:
      print(converted_config, end='')
    else:
      logging.info('Saving to file: %s', self._output_file)
      with open(self._output_file, 'wt') as output_file:
        output_file.write(converted_config)
    logging.info('Completed successfully.')
    conversion_logger.log_success()

  def run_on_string(self, config_string: str) -> str:
    """Runs DM converter on an input string."""
    try:
      expanded_config = yaml.safe_load(config_string)
      resources = self._parse_resources(expanded_config)
      self._converter.convert(
          resources=resources, namespace=self._namespace)
      logging.info('Completed successfully.')
      conversion_logger.log_success()
      return 'Pass'
    except errors.ConverterError as e:
      conversion_logger.log_error(error_code=convert_usage_pb2.ConversionMessage
                                  .ErrorCode.USER_ERROR_CORRUPTED_INPUT)
      return str(e)
