"""KRM converter implementation."""
from collections.abc import Mapping, MutableMapping, Sequence
import functools
import json
import re
from typing import Any, Optional

from absl import logging
import yaml

import base_converter
import conversion_logger
import errors
import strings
import convert_usage_pb2


class KrmConverter(base_converter.BaseConverter):
  """Deployment Manager to KRM config converter."""

  def __init__(self, **kwargs):
    super(KrmConverter, self).__init__(**kwargs)

    self._load_filters()

  def convert(
      self,
      resources: list[Any],
      namespace: str,
      layout: Optional[MutableMapping[str, Any]] = None,
  ) -> str:  # pytype: disable=signature-mismatch  # overriding-parameter-count-checks
    """Converts a list of DM resources to KRM format.

    Args:
      resources: List of DM resources, each of which is dictionary.
      namespace: resource to narrow down conversion scope.
      layout: Layout content from expansion service.

    Returns:
      Converted resources in yaml format.

    Raises:
      ContainsActionError: in case of the type is an action.
    """

    self._resources = resources
    _pre_process_resources(self._resources)
    context = {'namespace': namespace} if namespace else {}
    converted_resources = []
    for resource in self._resources:
      resource_action = resource.get('action')
      if resource_action is not None:
        conversion_logger.log_error(
            error_code=convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_CONTAINS_ACTION,
            action_name=resource_action,
        )
        raise errors.ContainsActionError(
            f'Resource {resource_action!r} is an action that cannot be'
            'converted to KRM'
        )

      converted_resource = self.convert_resource(
          resource, context, output_format='krm'
      )
      if converted_resource:
        converted_resources.extend(list(yaml.safe_load_all(converted_resource)))

    return yaml.dump_all(converted_resources, Dumper=yaml.SafeDumper)

  def _load_filters(self):
    self.jinja_env.filters.update(
        {
            'dump_json': lambda obj: json.dumps(obj, indent=2),
            'enumerate': enumerate,
            'set_difference': lambda a, b: set(a) - set(b),
            'set_intersection': lambda a, b: set(a) & set(b),
            # pylint: disable=g-long-lambda
            'typed_reference': lambda value: resolve_typed_reference(
                value, self._resources
            ),
            'arbitrary_reference': lambda value: resolve_arbitrary_reference(
                value, self._resources
            ),
            'reference_type': lambda value: get_reference_type(
                value, self._resources
            ),
            'missing_fields': lambda resource, paths: missing_fields(
                resource, paths, self._skip_unsupported_fields
            ),
            # pylint: enable=g-long-lambda
        }
    )


def _pre_process_resources(resources: list[MutableMapping[str, Any]]):
  """In-place method runs pre-processing logic to organize input.

  Args:
    resources: Collection of DM resources, each of which is dictionary.
  """

  if resources is None:
    return

  base_converter.pre_process_billing(resources)


#
# Helper functions used by Jinja2 env.templates
#
def detect_pattern(pattern: str, value: str) -> Mapping[Any, Any]:
  match = re.search(pattern, value)
  return match.groupdict() if match else {}


def typed_reference_groups(field_value: str) -> Mapping[Any, Any]:
  return detect_pattern(strings.Pattern.TYPED_REFERENCE_GROUPS, field_value)


def resolve_typed_reference(
    field_value: str, resources: Sequence[Mapping[str, Any]]
) -> Mapping[Any, Any]:
  """Convert a typed reference field in Config Connector."""
  if not isinstance(field_value, str):
    logging.debug(
        'Attempt to resolve ref on non-string object: %s', field_value
    )
    return
  groups = typed_reference_groups(field_value)
  # If the value in the field is not using $ref references, use the actual
  # value with 'external'
  if not groups:
    # Reference value should be set to 'default' for
    # compute instances/networkInterfaces/network
    # (b/198780021)
    if field_value == 'global/networks/default':
      field_value = 'default'
    return {'external': field_value}
  # Otherwise, use the name of referent
  name = groups.get('name')
  for resource in resources:
    if resource.get('name') == name:
      return {'name': name}

  conversion_logger.log_error(
      error_code=convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_UNSUPPORTED_REFERENCE
  )

  raise errors.UnsupportedReferenceError(
      f'The referenced resource {name!r} not found.'
  )


@functools.singledispatch
def resolve_arbitrary_reference(field_value: Any, _: list[Any]) -> str:
  """Default dispatcher on field_value type."""
  return field_value


@resolve_arbitrary_reference.register(str)
def _(field_value: str, resources: list[Any]) -> str:
  """Dispatch on field_value type str."""
  groups = detect_pattern(strings.Pattern.ARBITRARY_REFERENCE, field_value)
  if not groups:
    return field_value
  prefix = groups.get('prefix', '')
  name = groups.get('name')
  path = groups.get('path')
  suffix = groups.get('suffix', '')
  resolved_value = resolve_ref(prefix, name, path, suffix, resources)

  if not resolved_value:
    conversion_logger.log_error(
        error_code=convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_UNSUPPORTED_REFERENCE
    )
    error_message = f'The reference {field_value} cannot be resolved.'
    raise errors.UnsupportedReferenceError(error_message)
  return resolved_value


@resolve_arbitrary_reference.register(list)
def _(field_value: list[Any], resources: list[Any]) -> list[Any]:
  """Dispatch on field_value type list."""
  return [
      resolve_arbitrary_reference(element, resources) for element in field_value
  ]


@resolve_arbitrary_reference.register(dict)
def _(
    field_value: Mapping[Any, Any], resources: list[Any]
) -> Mapping[Any, Any]:
  """Dispatch on field_value type dict."""
  return {
      key: resolve_arbitrary_reference(value, resources)
      for key, value in field_value.items()
  }


def find_resource(name: str, resources: list[Any]) -> Mapping[Any, Any]:
  for resource in resources:
    properties = resource.get('properties', {})
    if properties.get('name', resource.get('name')) == name:
      return resource
  return {}


def resolve_ref(
    prefix: str, name: str, path: str, suffix: str, resources: list[Any]
) -> str:
  """Resolve reference values over given resourses."""
  resource = find_resource(name, resources)
  if resource and isinstance(resource, dict):
    # Follow steps of dot separated path starting at properties.
    value = resource.get('properties').copy()
    # Include resource name in properties object.
    value['name'] = value.get('name', resource['name'])
    for field in path.split('.'):
      value = resolve_ref_for_path(value, field)
      if not value:
        return ''
  else:
    return ''
  return f'{prefix}{value}{suffix}'


def resolve_ref_for_path(properties: Mapping[Any, Any], field: str) -> Any:
  """Resolve reference using properties dict."""
  groups = detect_pattern(strings.Pattern.FIELD, field)
  if not groups:
    properties = properties.get(field)
  else:
    # Resolve field in the list item.
    field = groups.get('field')
    item_idx = int(groups.get('item_idx'))
    properties = properties.get(field)[item_idx]
  if not properties:
    logging.error('The property does not exist: %s', field)
  return properties


def get_reference_type(field_value: Any, resources: list[Any]) -> str:
  """Get the type of the resource referenced by the given field value."""

  def _format_ref(ref_str):
    return strings.recapitalize(strings.depluralize(ref_str)) + 'Ref'

  groups = typed_reference_groups(field_value)
  if not groups:
    return _format_ref(field_value.split('/')[-2])
  referant_type = find_resource(groups.get('name'), resources).get('type')
  if not referant_type:
    conversion_logger.log_error(
        error_code=convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_UNSUPPORTED_REFERENCE
    )
    raise errors.UnsupportedReferenceError(
        'Reference to action is not supported.'
    )
  # Handle both gcp and legacy types by taking last part after any ':' or '.'.
  return _format_ref(referant_type.rpartition(':')[2].rpartition('.')[2])


def find_path(value: Mapping[str, Any], path: list[str]) -> bool:
  """Search given dict for given path, including all elements in lists."""
  for i, step in enumerate(path):
    value = value.get(step)
    if not value:
      return False
    if isinstance(value, list):
      found = False
      for element in value:
        if find_path(element, path[i + 1 :]):
          found = True
      return found
  return True


def missing_fields(
    resource: Mapping[str, Any], paths: list[str], skip_unsupported_fields: bool
) -> list[str]:
  """Log warning or raise exception if any of given paths are in given resource."""
  found = []
  for path in paths:
    if find_path(resource, path.split('.')):
      # Path was found in resource.
      found.append(path)
      if skip_unsupported_fields:
        logging.warning('Field %s has no KRM equivalent.', path)
      else:
        conversion_logger.log_error(
            error_code=convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_UNCONVERTIBLE_PROPERTY
        )
        raise errors.UnconvertableFieldError(
            f'Field {path} has no KRM equivalent.'
        )
  return found


def _str_scalar_representor(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
  if '\n' in data:
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
  return dumper.represent_scalar('tag:yaml.org,2002:str', data)


yaml.add_representer(str, _str_scalar_representor, Dumper=yaml.SafeDumper)
