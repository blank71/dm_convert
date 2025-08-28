"""Terraform converter implementation."""

from collections.abc import Mapping, MutableMapping, Sequence
import contextlib
import copy
import dataclasses
import pathlib
import re
from typing import Any, Optional

from absl import logging
import yaml

import base_converter
import conversion_logger
import dm_action_converter
import errors
import layout_parser
import module_generator
import property_parser
import resource_reader
import strings
import template_resolver
import convert_usage_pb2

_REFERENCE_ID_OVERRIDES = {
    'google_kms_key_ring': 'id',
    'google_compute_address': 'address',
    'google_compute_vpn_gateway': 'id',
}


_INSTANCE_GROUP_TYPES = frozenset({
    'compute.v1.instanceGroup',
    'compute.v1.instanceGroups',
    'compute.beta.instanceGroup',
    'gcp-types/compute-v1:instanceGroups',
})

_TARGET_POOL_TYPES = frozenset({
    'gcp-types/compute-v1:targetPools',
    'compute.v1.targetPool',
    'compute.v1.targetPools',
})

_ADD_INSTANCE_ACTION = (
    'gcp-types/compute-v1:compute.instanceGroups.addInstances'
)


@dataclasses.dataclass
class ReferenceContract(object):
  """Class for DM reference definition."""

  resource_name: str
  field_name: str


class TerraformConverter(base_converter.BaseConverter):
  """Deployment Manager to Terraform config converter."""

  def __init__(
      self,
      provider: str,
      tf_import_file: Optional[pathlib.Path] = None,
      layout_file: Optional[pathlib.Path] = None,
      without_deployment_flag: bool = False,
      **kwargs,
  ):
    super().__init__(**kwargs)

    self._load_filters()
    templates_dir = resource_reader.get_templates_dir('actions')

    self.actions_converter = dm_action_converter.DmActionConverter(
        templates_dir=templates_dir,
        template_resolver=template_resolver.get_instance(
            'actions', templates_dir
        ),
    )

    self.provider = provider

    self.tf_import_file = tf_import_file

    self.jinja_env.globals['get_tf_provider'] = provider

    self.layout_file = layout_file

    self.without_deployment_flag = without_deployment_flag

    self.layout_parser = None
    self.unsupported_fields_map = {}

  def convert(
      self,
      resources: Sequence[MutableMapping[str, Any]],  # pytype: disable=signature-mismatch  # overriding-parameter-count-checks
      namespace: Optional[str],
      layout: Optional[MutableMapping[str, Any]] = None,
  ) -> str:
    """Converts a list of DM resources to Terraform format.

    Args:
      resources: Collection of DM resources, each of which is dictionary.
      namespace: resource to narrow down conversion scope.
      layout: the layout content from the expansion service

    Returns:
      Converted resources in string format.
    """

    def is_action(resource: dict[str, Any]) -> bool:
      return resource.get('action') is not None

    self._resources = validate_resources(resources)
    self._action_resources = [r for r in self._resources if is_action(r)]  # pytype: disable=wrong-arg-types  # always-use-return-annotations

    _pre_process_resources(self._resources)
    resources_to_convert = [r for r in self._resources if not is_action(r)]  # pytype: disable=wrong-arg-types  # always-use-return-annotations

    unconvertible_actions, dm_resources = self.actions_converter.convert(
        self._action_resources, namespace=None
    )

    if dm_resources:
      resources_to_convert.extend(yaml.safe_load(dm_resources))

    if self.layout_file is not None or self.without_deployment_flag:
      self.template_conversion(resources_to_convert, layout=layout)

    none_context = contextlib.nullcontext()
    unsupported_resources = {}
    unsupported_resources['resources'] = []
    with (
        open(self.tf_import_file, 'wt')
        if self.tf_import_file is not None
        else none_context
    ) as tf_imp_out_file:
      provider_block = self.get_provider_block(self.provider, self._project_id)
      converted_resources = provider_block

      for resource in resources_to_convert + unconvertible_actions:
        converted_resource = self.convert_resource(
            resource,
            context={},
            output_format='tf',
            unsupported_resources=unsupported_resources,
            tf_import_file=tf_imp_out_file,
        ).strip()
        # Add a comment with the unsupported_fields_map
        # for the current resource
        unsupported_fields_comment = ''
        if self.unsupported_fields_map.get(resource.get('name')):
          for field in self.unsupported_fields_map.get(
              resource.get('name')
          ):
            for field_name, field_value in field.items():
              unsupported_fields_comment += f'# {field_name}: {field_value}\n'
        if unsupported_fields_comment:
          converted_resource_with_unsupported_fields = (
              '\n\n# ----This file was created by Deployment Manager Convertor'
              ' (DMC) Tool. This resource contains resource configuration'
              ' fields that are not supported by Terraform. ---- #\n# ----'
              ' Please review and update those fields as needed by DM Convert'
              f' ---- #\n\n{unsupported_fields_comment}#\n'
          ) + converted_resource
        else:
          converted_resource_with_unsupported_fields = converted_resource
        if converted_resource_with_unsupported_fields:
          converted_resources += (
              '\n' + converted_resource_with_unsupported_fields + '\n'
          )
    if self.tf_import_file is not None and self.layout_parser is not None:
      import_path = (
          self.tf_import_file.parent / 'template_conversion/imports.txt'
      )
      with open(import_path, 'wt') as module_import_file:
        module_import_file.write(
            self.get_module_import_statements(
                self.tf_import_file, self.layout_parser
            )
        )

    if unsupported_resources['resources']:
      with (
          open(self.get_unsupported_resources_file(self.tf_import_file), 'wt')
          if self.tf_import_file is not None
          else none_context
      ) as unsupported_resources_file:
        yaml.dump(unsupported_resources, unsupported_resources_file)
    return converted_resources

  def get_module_import_statements(
      self, import_file: pathlib.Path, layout: layout_parser.LayoutParser
  ) -> str:
    module_import_statements = []
    with open(import_file, 'r') as file:
      import_statements = file.read().split('\n')[:-1]
      for statement in import_statements:
        statement_list = statement.split()
        resource_name = statement_list[-1].split('/')[-1]
        resource_type = '.'.join(statement_list[2].split('.')[:-1])
        template_name = layout.get_template_name(resource_name)

        if template_name == 'main':
          module_import_statements.append(' '.join(statement_list))
          continue

        module_path = layout.path_name[resource_name].replace(
            'module.main.', ''
        )
        terraform_equivalent = '.'.join(
            [module_path, resource_type, template_name]
        )
        statement_list[2] = re.sub(r'-', '_', terraform_equivalent)
        module_import_statements.append(' '.join(statement_list))

    return '\n'.join(module_import_statements) + '\n'

  def template_conversion(
      self,
      resources_to_convert: list[MutableMapping[str, Any]],
      layout: Optional[MutableMapping[str, Any]] = None,
  ):
    """Performs template conversion for the given resources.

    Args:
      resources_to_convert: Collection of DM resources, each of which is a
        dictionary.
      layout: The layout content from the expansion service.

    Raises:
      ConverterError: If error occurs while processing the layout details.
    """
    if self.layout_file is not None:
      self.layout_parser = layout_parser.LayoutParser(self.layout_file)
    elif self.without_deployment_flag:
      self.layout_parser = layout_parser.LayoutParser(None, layout)

    if self.layout_parser is None:
      raise errors.ConverterError(
          'Either of layout_file or without_deployment argument needs to be'
          ' passed for template conversion'
      )
    self.property_parser = property_parser.PropertyParser(
        layoutparser=self.layout_parser
    )

    unsupported_resources = {}
    unsupported_resources['resources'] = []
    if self.tf_import_file is not None:
      template_directory = self.tf_import_file.parent / 'template_conversion'
      template_directory.mkdir(parents=True, exist_ok=True)
      module_directory = template_directory / 'modules'
      module_directory.mkdir(parents=True, exist_ok=True)
    else:
      logging.warn('Template Conversion requires tf import file')
      return

    names = []
    for resource in resources_to_convert:
      self.property_parser.process(copy.deepcopy(resource))
      names.append(resource['name'])
    for template_name in self.property_parser.processed_resources:
      converted_template = self.convert_resource(
          self.property_parser.processed_resources[template_name],
          context={},
          output_format='tf',
          unsupported_resources=unsupported_resources,
          tf_import_file=None,
      ).strip()
      if unsupported_resources['resources']:
        logging.warn(
            'Template conversion requires all resources to be supported'
        )
        return

      current_module_directory = module_directory / template_name
      current_module_directory.mkdir(parents=True, exist_ok=True)

      with open(
          pathlib.Path(current_module_directory / 'main.tf'), 'wt'
      ) as main_file:
        main_file.write(converted_template)
      main_file.close()

      converted_variables = self.property_parser.get_variables(template_name)
      with open(
          pathlib.Path(current_module_directory / 'variables.tf'), 'wt'
      ) as variables_file:
        variables_file.write(converted_variables)
      variables_file.close()

      converted_outputs = self.property_parser.get_outputs(template_name)
      if converted_outputs:
        with open(
            pathlib.Path(current_module_directory / 'outputs.tf'), 'wt'
        ) as outputs_file:
          outputs_file.write(converted_outputs)
        outputs_file.close()

    module_conversion = module_generator.ModuleGenerator(
        names,
        self.layout_parser,
        self.property_parser,
        template_directory,
        module_directory,
    )
    module_conversion.process()
    for output_path in module_conversion.main_file_content:
      with open(pathlib.Path(output_path), 'wt') as output_file:
        output_file.write(
            '\n\n'.join(module_conversion.main_file_content[output_path])
        )
      output_file.close()
    for variable_path in module_conversion.variable_file_content:
      with open(pathlib.Path(variable_path), 'wt') as variable_file:
        variable_file.write(
            '\n\n'.join(module_conversion.variable_file_content[variable_path])
        )
      variable_file.close()

  def get_unsupported_resources_file(
      self, file_path: pathlib.Path
  ) -> pathlib.Path:
    """Get unsupported resources file path.

    File directory is taken same as the directory of import file.

    Args:
      file_path: Import file path.

    Returns:
      Unsupported resources file path.
    """
    return file_path.parent / 'unsupported_resources.txt'

  def get_provider_block(self, provider: str, project_id: str) -> str:
    """Get provider block.

    Args:
      provider: Provider of the resources.
      project_id: Project Id of the resources.

    Returns:
      Provider block in the string format.
    """
    template = self.jinja_env.get_template('tf_provider.jinja')
    provider_block = template.render(provider=provider, project_id=project_id)
    return provider_block

  def get_supported_types(self) -> set[str]:  # pytype: disable=signature-mismatch  # overriding-return-type-checks
    return set(self.template_resolver.list_dm_types())

  def get_supported_actions(self) -> set[str]:
    return set(self.actions_converter.get_supported_types())

  def _load_filters(self):
    """Loads custom jinja filters."""
    self.jinja_env.filters.update({
        'is_list': lambda value: isinstance(value, list),
        # pylint: disable=g-long-lambda
        'make_dependencies': lambda value: make_dependencies(
            value,
            self._resources,
            self.template_resolver,  # pytype: disable=wrong-arg-types
        ),
        'make_reference': lambda value: make_reference(
            value,
            self._resources,
            self.template_resolver,  # pytype: disable=wrong-arg-types
        ),
        'hydrate_ref_field': lambda value: hydrate_ref_field(
            value, self._resources, self._project_id
        ),
        'normalize_resource_name': normalize_resource_name,
        # pylint: enable=g-long-lambda
        'if_null': filter_if_null,
        'match_missing_fields': (
            lambda resource, missing_fields: match_missing_fields(
                resource, missing_fields, self.unsupported_fields_map
            )
        ),
    })


def _pre_process_resources(resources: list[MutableMapping[str, Any]]):
  """In-place method runs pre-processing logic to organize input.

  Args:
    resources: Collection of DM resources, each of which is dictionary.
  """

  if resources is None:
    return

  base_converter.pre_process_billing(resources)
  base_converter.pre_process_service_enable_type(resources)

  for current_resource in resources:
    resource_type = current_resource.get('type', '')
    properties = current_resource.get('properties', {})
    action = current_resource.get('action', '')

    if resource_type in _TARGET_POOL_TYPES and 'instances' in properties:
      _pre_process_target_pool(current_resource, resources)
    elif action == _ADD_INSTANCE_ACTION:
      _pre_process_action_add_instance(current_resource, resources)


def _pre_process_target_pool(
    target_pool: Mapping[str, Any], resources: list[Mapping[str, Any]]
):
  """TF target pool does not support references in instances property.

  Instead references must be a URL format or follow {zone}/compute_instance_name

  Args:
    target_pool: The target pool found in resources.
    resources: Collection of DM resources.
  """

  for instance_idx, instance_ref in enumerate(
      target_pool['properties']['instances']
  ):
    if instance_ref.lower().startswith(('http', 'https')):
      continue
    compute_instance_name = instance_ref.split('.')[1]
    compute_instance = next(
        r for r in resources if r['name'] == compute_instance_name
    )
    new_value = '/'.join(
        (compute_instance['properties'].get('zone'), compute_instance_name)
    )
    target_pool['properties']['instances'][instance_idx] = new_value


def _pre_process_action_add_instance(
    add_instance: Mapping[str, Any], resources: list[Mapping[str, Any]]
):
  """Augments instance group manager resource using addInstances action.

  The action should be removed from the resource list and only instances
  property should be copied to instance group type.

  Args:
    add_instance: The action found in resources.
    resources: Collection of DM resources.
  """

  instance_group_resource_name = add_instance.get('properties', {}).get(
      'instanceGroup', None
  )
  if instance_group_resource_name is None:
    action_name = add_instance.get('name')
    raise errors.ActionMissingRequiredResourceError(
        f'addInstance resource - {action_name!r} is missing '
        f'instanceGroup - {instance_group_resource_name!r}'
    )

  for resource in resources:
    if (
        resource.get('type') in _INSTANCE_GROUP_TYPES
        and resource.get('name', '') == instance_group_resource_name
    ):
      action_instances = add_instance['properties'].get('instances', None)
      if action_instances:
        instances = [instance['instance'] for instance in action_instances]
        resource['properties'].update({'instances': instances})

      resources.remove(add_instance)
      return


def _find_resource(
    name: str, resources: Sequence[Mapping[str, Any]]
) -> Mapping[str, Any]:
  for resource in resources:
    if resource.get('name') == name:
      return resource
  return {}


def _parse_dm_reference(value: str) -> ReferenceContract:
  """Extracts from DM reference values for building TF reference.

  Args:
    value: DM reference.

  Returns:
    DM resource name, DM field name
  """
  match = re.search(strings.Pattern.TYPED_REFERENCE_GROUPS, value)
  groups = match.groupdict() if match else {}

  resource_name = groups.get('name', '')
  dm_field_name = groups.get('path', '')

  if '.' in dm_field_name:
    dm_field_name = dm_field_name.split('.')[-1]

  # Replacing `selfLink` DM attribute with terraform `id` attribute.
  if dm_field_name == 'selfLink':
    dm_field_name = 'id'
  field_name = strings.pascal_to_snake(dm_field_name)

  return ReferenceContract(resource_name, field_name)


def hydrate_ref_field(
    ref_value: str, resources: Sequence[Mapping[str, Any]], arg_project_id: str
) -> str:
  """Hydrates the provided referenced field to the real field value.

  Args:
    ref_value: referenced field value e.g. $(ref.resource-name.field-name)
    resources: Collection of DM resources, each of which is dictionary.
    arg_project_id: passed in project_id as an arg when running the tool.

  Returns:
    Hydrated/resolved field value from the referenced DM resource

  if a project_id was passed via the command like, ignore project references
  in the resource config
  """
  if arg_project_id and '.projectId' in ref_value:
    return arg_project_id

  hydrated_value = ''
  match = re.search(strings.Pattern.TYPED_REFERENCE_GROUPS, ref_value)
  groups = match.groupdict() if match else {}

  project_res_name = groups.get('name', '')
  fq_field_path = groups.get('path', '')
  path_segments = fq_field_path.split('.')

  if path_segments[0] == 'name':
    return project_res_name

  for res in resources:
    if res.get('name') == project_res_name:
      props = res.get('properties', {})
      if bool(props):
        i = 0
        while i < len(path_segments):
          props = props.get(path_segments[i], {})
          i = i + 1
      hydrated_value = str(props)
      break

  return hydrated_value


def make_reference(
    field_value: str,
    resources: Sequence[Mapping[str, Any]],
    resolver: template_resolver.TerraformTemplateResolver,
) -> str:
  """Generate reference for resource referenced by the given field value.

  Args:
    field_value: DM field value which contains reference. The value will be
      returned if not string, otherwise will be processed.
    resources: Collection of DM resources, each of which is dictionary.
    resolver: Terraform template resolver.

  Returns:
    Terraform reference.
  """
  if not isinstance(field_value, str):
    return field_value

  reference = _parse_dm_reference(field_value)
  referenced_target_resource = _find_resource(
      reference.resource_name, resources
  )
  if not referenced_target_resource:
    conversion_logger.log_error(
        error_code=convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_UNSUPPORTED_REFERENCE
    )

    raise errors.UnsupportedReferenceError(
        f'Cannot resolve reference - {field_value!r}.'
    )

  # when we found resource using original name, then transform it to TF format.
  # in jinja template resource name must be constructed using get_name macro.
  reference.resource_name = normalize_resource_name(reference.resource_name)
  dm_type = referenced_target_resource.get(
      'type', referenced_target_resource.get('action')
  )
  tf_resource_type = resolver.resolve(dm_type, referenced_target_resource)
  if tf_resource_type in _REFERENCE_ID_OVERRIDES.keys():
    reference.field_name = _REFERENCE_ID_OVERRIDES[tf_resource_type]

  reference.field_name = normalize_resource_name(reference.field_name)

  if tf_resource_type.startswith('data_'):
    reference_value = f'data.{tf_resource_type[len("data_"):]}.{reference.resource_name}.{reference.field_name}'
  else:
    reference_value = (
        f'{tf_resource_type}.{reference.resource_name}.{reference.field_name}'
    )

  return reference_value


def make_dependencies(
    dm_resource: Mapping[str, Any],
    resources: Sequence[Mapping[str, Any]],
    resolver: template_resolver.TerraformTemplateResolver,
) -> Sequence[str]:
  """Generate list of resource names current resource depends on.

  Args:
    dm_resource: DM with dependencies.
    resources: Collection of DM resources, each of which is dictionary.
    resolver: Terraform template resolver.

  Returns:
    List of dependencies. Each dependency has format `type.name`.
  """
  tf_dependencies = []
  dm_dependencies_names = dm_resource.get('metadata', {}).get('dependsOn', {})
  for dm_name in dm_dependencies_names:
    dependency_resource = _find_resource(dm_name, resources)
    if not dependency_resource:
      conversion_logger.log_error(
          error_code=convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_UNSUPPORTED_DEPENDENCY
      )

      raise errors.UnsupportedDependencyError(
          f'Cannot resolve dependency - {dm_name!r}.'
      )

    tf_resource_type = resolver.resolve(
        dependency_resource.get('type'), dependency_resource
    )
    tf_name = normalize_resource_name(dm_name)
    tf_dependencies.append(f'{tf_resource_type}.{tf_name}')
  return tf_dependencies


def normalize_resource_name(value: str) -> str:
  """Normalize terraform resource name.

  For value normalization method applies the same
  formatting rules that uses for Terraform resource id validation.
  https://www.terraform.io/docs/language/syntax/configuration.html#identifiers

  If a resource name does not begin with a letter or underscore, an underscore
  is prepended to make it valid.

  Args:
    value: The input value.

  Returns:
    Formatted name value.
  """
  validated = strings.tf_id_replace_invalid_char(value)
  validated = strings.tf_resource_name_fix_starting(validated)
  if value != validated:
    logging.warning(
        'Invalid characters are found. Before %s, after %s.', value, validated
    )
  return validated


def validate_resources(
    resources: Sequence[MutableMapping[str, Any]],
) -> list[MutableMapping[str, Any]]:
  """Asserts that each DM resource has a name and either a type or an action.

  These fields are validated to be non-empty.

  Args:
    resources: List of DM resources

  Returns:
    The original resources

  Raises:
    InvalidResourceError if any resource is invalid.
  """
  for resource in resources:
    if not resource.get('name'):
      conversion_logger.log_error(
          error_code=convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_INVALID_RESOURCE
      )
      raise errors.InvalidResourceError('All resources must have a name.')

    if not resource.get('type') and not resource.get('action'):
      conversion_logger.log_error(
          error_code=convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_INVALID_RESOURCE
      )
      raise errors.UnsupportedResourceTypeError(
          f'Resource (name = {resource["name"]}) must have either the "type" or'
          ' "action" field set.'
      )

  return list(resources)


def filter_if_null(field_name: str, varargs: tuple[Any, ...]) -> Optional[Any]:
  """Filter to mimic if_null functionality.

  If field_name not found in the first argument, then function takes next
  argument.

  Args:
    field_name: The field name to be searched for.
    varargs: The tuple with datasources.

  Returns:
    Value from varargs, otherwise None.
  """
  for datasource in varargs:
    if datasource is not None and field_name in datasource:
      return datasource[field_name]

  return None


def find_field(value: Mapping[str, Any], path: list[str]) -> bool:
  """Search given dict for given path, including all elements in lists."""
  for i, step in enumerate(path):
    value = value.get(step)
    if value is None:
      return False
    if isinstance(value, list):
      found = False
      for element in value:
        if find_field(element, path[i + 1 :]):
          found = True
      return found
  return True


def match_missing_fields(
    resource: Mapping[str, Any],
    missing_fields: list[str],
    unsupported_fields_map: MutableMapping[str, list[dict[str, str]]],
) -> str:
  """Jinja filter to identify unsupported DM fields.

  It stores them in the global tracker.
  It returns an empty string to prevent any in-line comments in the HCL.

  Args:
      resource: The full Deployment Manager resource dictionary from the
        template context.
      missing_fields: A list of string paths (e.g., 'properties.disk.foo') of
        fields known to be unsupported for this resource type, as defined
        directly in the Jinja template.
      unsupported_fields_map: The map that holds all the unsupported fields,
        where the function inserts the new unsupported fields.
  Returns:
      An empty string, as we do not want in-line comments.
  """
  # Use the 'name' from the full DM resource for accurate tracking
  resource_name = resource.get('name', 'unknown-resource')

  found_unsupported_for_this_resource = []

  for field_path in missing_fields:
    field_path_list = field_path.split('.')
    # Extract the actual value if the path exists in the DM resource
    field_value = _get_field_value(resource, field_path_list)

    if field_value is not None:
      formatted_value = str(field_value)
      found_unsupported_for_this_resource.append({field_path: formatted_value})
      logging.warning(
          'Field %s is unsupported in conversion for resource %s. Value: %s',
          field_path,
          resource_name,
          formatted_value,
      )

  if found_unsupported_for_this_resource:
    # Populate the instance's global tracker
    unsupported_fields_map.setdefault(resource_name, []).extend(
        found_unsupported_for_this_resource
    )
  return ''


def _get_field_value(value: Mapping[str, Any], path: list[str]) -> Any:
  """Search given dict for given path, including all elements in lists.

  Args:
    value: The dict to search in.
    path: The path to search for.

  Returns:
    The value at the given path, or None if not found.
  """

  current_value = value
  for i, step in enumerate(path):
    if isinstance(current_value, Mapping) and step in current_value:
      current_value = current_value[step]
    elif isinstance(current_value, list):
      found_values_in_list = []
      for element in current_value:
        val = _get_field_value(element, path[i:])
        if val is not None:
          if isinstance(val, list):
            found_values_in_list.extend(val)
          else:
            found_values_in_list.append(val)
      return found_values_in_list if found_values_in_list else None
    else:
      return None
  return current_value

