"""Base converter class."""

from collections.abc import Mapping, MutableMapping, Sequence
import pathlib
import re
from typing import Any, IO, Optional

from absl import logging
import jinja2

import conversion_logger
import errors
from template_resolver import BaseTemplateResolver
import convert_usage_pb2

_GCP_PROJECT_TYPES = [
    'gcp-types/cloudresourcemanager-v1:projects',
    'cloudresourcemanager.v1.project',
]
_RE_IMPORT_STATEMENT = 'tfimport-(.*)\n'
_IMPORT_PROJECT_PLACEHOLDER = '__project__'


class BaseConverter(object):
  """Base class that all converter implementations derive from."""

  def __init__(
      self,
      templates_dir: pathlib.Path,
      template_resolver: BaseTemplateResolver,
      skip_unsupported_fields: bool = False,
      project_id: Optional[str] = None,
  ):
    self._skip_unsupported_fields = skip_unsupported_fields
    self.template_resolver = template_resolver
    self._project_id = project_id

    self.jinja_env = jinja2.Environment(
        keep_trailing_newline=True,
        loader=jinja2.FileSystemLoader(templates_dir),
    )

    self._load_globals()

  def convert(self, **kwargs) -> str:
    raise NotImplementedError('Base converter.')

  def convert_resource(
      self,
      resource: Mapping[str, str],
      context: Mapping[str, str],
      output_format: str,
      unsupported_resources: Optional[Mapping[str, Any]] = None,
      tf_import_file: Optional[IO[str]] = None,
  ) -> str:
    """Converts single DM resource.

    Args:
      resource: DM resource map.
      context: resource context (e.g. PROJECT_ID).
      output_format: format for the output.( tf for TF, krm for KRM, action for
        actions)
      unsupported_resources: optional resource map for unsupported resources for
        TF output
      tf_import_file: optional tf import file parameter for TF output

    Returns:
      The string representation of the converted resource.
      If the resource is not supported returns an empty string.

    Raises:
      UnsupportedResourceType: Type is not supported.
    """

    if resource.get('type') and resource.get('action'):
      raise errors.UnsupportedResourceTypeError(
          f'Resource {resource!r} should define either a type or an action, but'
          ' not both'
      )

    resource_type = (
        resource.get('type') if resource.get('type') else resource.get('action')
    )

    supported_resource_types = self.template_resolver.list_dm_types()

    if resource_type not in supported_resource_types and output_format == 'krm':
      raise errors.UnsupportedResourceTypeError(
          f'Resource type {resource_type!r} is not supported.'
      )

    template = self.template_resolver.resolve(resource_type, resource)
    # Checks for unsupported_resource
    if template == 'unsupported_resource':
      logging.info(
          'Template conversion requires all resources to be supported',
      )
      logging.info(
          'Unsupported resource type: %s with name: %s',
          resource_type,
          resource.get('name'),
      )

      unsupported_resources['resources'].append(resource)
      return ''

    logging.info('Ready to convert resource type: %s', resource_type)
    jinja_filename = f'{template}.jinja'

    template = self.jinja_env.get_template(jinja_filename)

    expanded = template.render(resource=resource, context=context)

    if tf_import_file is not None:
      tf_import_statements = get_tf_import_statements(
          expanded, self._project_id
      )

      if tf_import_statements is None:
        tf_import_file.write(f'#future tf import command for {resource_type}\n')
      else:
        for statement in tf_import_statements:
          tf_import_file.write(f'{statement}\n')

    return expanded

  def get_supported_types(self) -> Sequence[str]:
    return self.template_resolver.list_dm_types()

  def get_supported_actions(self) -> set[str]:
    return set()

  def _load_globals(self):
    self.jinja_env.globals['raise_unsupported_action_state'] = (
        _raise_unsupported_action_state
    )


def _raise_unsupported_action_state(error_message: str) -> None:
  """The global jinja function to raise an UnsupportedActionStateError.

  Args:
    error_message: The error details.

  Raises:
    UnsupportedActionStateError.
  """
  raise errors.UnsupportedActionStateError(error_message)


def get_tf_import_statements(
    expanded: str, project_id: Optional[str]
) -> Optional[list[str]]:
  """Creates tf import statements.

  Args:
    expanded: Converted tf resource which has imprinted as comment the tf import
      statement.
    project_id: Project id passed in as optional parameter into the tool.

  Returns:
    The tf import statements as a list of string or None.
  """
  if expanded is None:
    return None

  results = re.finditer(_RE_IMPORT_STATEMENT, expanded)
  processed = []

  for result in results:
    if result is None or result.group(1) is None:
      continue

    import_statement = result.group(1)
    project_idx = import_statement.find(_IMPORT_PROJECT_PLACEHOLDER)

    if project_idx < 0:
      processed.append(import_statement)
      continue

    if project_id is None:
      import_statement_without_project_id = import_statement.replace(
          f'{_IMPORT_PROJECT_PLACEHOLDER}/', ''
      )
      processed.append(
          '#WARNING: This import statement was generated without explicit'
          f' project id\n{import_statement_without_project_id}'
      )
    else:
      processed.append(
          import_statement.replace(_IMPORT_PROJECT_PLACEHOLDER, project_id)
      )
  return processed


def pre_process_service_enable_type(resources: list[MutableMapping[str, Any]]):
  """Translate service enable to gcp type to deployment manager action.

  Changes the servicemanagement-v1:servicemanagement.services.enable type to
  deploymentmanager.v2.virtual.enableService action.

  Args:
    resources: List of DM resources, each of which is dictionary.
  """
  for resource in resources:
    if (
        resource.get('type')
        == 'gcp-types/servicemanagement-v1:servicemanagement.services.enable'
    ):
      resource['type'] = 'deploymentmanager.v2.virtual.enableService'


def pre_process_billing(resources: list[MutableMapping[str, Any]]):
  """Copies billing data to parent project.

  Checks for deploymentmanager.v2.virtual.projectBillingInfo type then copies
  billing data to parent project and deletes billing from the given resources.

  Also removes the Depends on billing from the resources.

  Args:
    resources: List of DM resources, each of which is dictionary.

  Raises:
    ReferencedResourceNotFoundError: in case a referenced resource cannot be
    found.
  """
  billing_items = [
      item
      for item in resources
      if item.get('type') == 'deploymentmanager.v2.virtual.projectBillingInfo'
  ]

  for billing_info in billing_items:
    billing_project_name = billing_info['properties'].get('name')

    if billing_project_name is None:
      raise errors.BillingConfigMissingParentError(
          (
              f'Resource with id={billing_info["name"]!r} does not have a'
              ' project configured. Please set the "name" property of the'
              ' resource to "projects/PROJECT_ID" for conversion to succeed.'
          )
      )

    parent_project_id = billing_project_name.split('/')[-1]

    if parent_project_id.startswith('$'):
      ref_segments = parent_project_id.split('.')
      ref_resource = ref_segments[1]

      for resource in resources:
        if (
            resource.get('name', '') == ref_resource
            and resource['type'] in _GCP_PROJECT_TYPES
        ):
          project_resource = resource
          break
    else:
      project_resource = next(
          item
          for item in resources
          if 'properties' in item
          and item.get('properties', {}).get('projectId', '')
          == parent_project_id
      )

    if project_resource is None:
      conversion_logger.log_error(
          error_code=convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_UNSUPPORTED_REFERENCE
      )
      raise errors.ReferencedResourceNotFoundError(
          'Cannot find project reference. Search by name -'
          f' {parent_project_id!r}.'
      )

    billing_value = billing_info['properties'].get('billingAccountName')

    project_resource['properties'].update({'billingAccountName': billing_value})
    resources.remove(billing_info)

    # The first check is only done for krm converter, because it does not
    # validate the presence of billing_info['name']
    if billing_info.keys().__contains__('name'):
      for resource in resources:
        if resource.keys().__contains__('metadata') and resource[
            'metadata'
        ].keys().__contains__('dependsOn'):
          if resource['metadata']['dependsOn'].__contains__(
              billing_info['name']
          ):
            resource['metadata']['dependsOn'].remove(billing_info['name'])
