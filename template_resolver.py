"""Type resolver factory and implementations."""

from collections.abc import Callable, Mapping, Sequence
import pathlib
from typing import Optional

import yaml

import errors


class BaseTemplateResolver:
  """Base class that all type resolver implementations derive from."""

  def __init__(self, templates: Mapping[str, str]):
    self._templates = templates
    self._override_rules = {}
    self._ignored_types = set()

  def add_override_rule(
      self,
      target_dm_type: str,
      rule_condition: Callable[[Mapping[str, str]], str],
  ):
    """Add override rule to resolve dm type.

    Args:
      target_dm_type: Target DM type to resolve.
      rule_condition: Rule condition that applies to resolve target DM type.
    """
    if target_dm_type is None:
      raise errors.InvalidOverrideRuleError(
          'Target DM type for override rule is required.'
      )
    if rule_condition is None:
      raise errors.InvalidOverrideRuleError(
          'Condition for override rule is required.'
      )
    if target_dm_type in self._override_rules:
      raise errors.AmbiguousOverrideRuleError(
          f'{target_dm_type!r} is already registered in templates.yaml'
      )

    self._override_rules.update({target_dm_type: rule_condition})

  def add_ignore_type(self, dm_type: str):
    """Adds ignore DM type to the template resolver.

    Args:
      dm_type: The DM resource type.
    """
    self._ignored_types.add(dm_type)

  def resolve(self, dm_type: str, resource: Optional[Mapping[str, str]]) -> str:
    """Returns corresponding type to provided DM resource type.

    Args:
      dm_type: The DM resource type.
      resource: The DM resource.

    Returns:
      The corresponding type based on DM resource type and context.
      If the resource type is not supported then it returns
      'unsupported_resource' as placeholder.

    Raises:
      TemplateResolverMissingContext: Type is being resolved by override rule
      without provided resource.
    """

    if dm_type in self._override_rules.keys():
      if resource is None:
        raise errors.TemplateResolverMissingContextError(
            f'Missing required context for {dm_type!r}'
        )

      override_rule = self._override_rules[dm_type]
      target_template = override_rule(resource)
    else:
      target_template = self._templates.get(dm_type, None)

    if target_template is None:
      return 'unsupported_resource'

    return target_template

  def list_dm_types(self) -> Sequence[str]:
    """Returns list of supported DM types.

    Returns:
      Plain list of supported DM types.
    """
    types = {**self._templates, **self._override_rules}
    return list(types.keys())

  def is_supported(self, dm_type: str) -> bool:
    """Checks if given DM type is supported.

    Args:
      dm_type: DM type to check.

    Returns:
      True if given DM type is supported, otherwise false.
    """
    return dm_type in self.list_dm_types() and not self.is_ignored(dm_type)

  def is_ignored(self, dm_type: str) -> bool:
    """Checks if given DM type is ignored.

    Args:
      dm_type: DM type to check.

    Returns:
      True if given DM type is ignored, otherwise false.
    """
    return dm_type in self._ignored_types


class KrmTemplateResolver(BaseTemplateResolver):
  """The KRM template resolver implementation."""

  pass


class TerraformTemplateResolver(BaseTemplateResolver):
  """The Terraform template resolver implementation."""

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    self.add_override_rule(
        'gcp-types/compute-v1:instances', self._override_compute_instance
    )
    self.add_override_rule(
        'compute.v1.instance', self._override_compute_instance
    )

  def _override_compute_instance(self, resource: Mapping[str, str]) -> str:
    if 'sourceInstanceTemplate' in resource.get('properties', {}):
      return 'google_compute_instance_from_template'
    return 'google_compute_instance'


class ActionTemplateResolver(BaseTemplateResolver):
  """The Actions template resolver implementation."""

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    self.add_ignore_type(
        'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy'
    )
    self.add_ignore_type(
        'gcp-types/compute-v1:compute.instanceGroups.addInstances'
    )


def get_instance(
    instance_type: str, templates_dir: pathlib.Path
) -> BaseTemplateResolver:
  """Template resolver factory method.

  Args:
    instance_type: Either tf or krm values are supported, argument is
      case-insensitive.
    templates_dir: The directory with jinja conversion templates.

  Returns:
    Template resolver based on value passed to instance_type argument.

  Throws:
    InvalidTemplateResolverTypeError: if instance_type has anything else but tf
    or krm values.
  """
  with templates_dir.with_suffix('.yaml').open(mode='r') as templates_map_file:
    templates = yaml.safe_load(templates_map_file)

    if instance_type.lower() == 'tf':
      template_resolver = TerraformTemplateResolver(templates=templates)
    elif instance_type.lower() == 'krm':
      template_resolver = KrmTemplateResolver(templates=templates)
    elif instance_type.lower() == 'actions':
      template_resolver = ActionTemplateResolver(templates=templates)
    else:
      raise errors.InvalidTemplateResolverTypeError(
          f'{instance_type!r} is not supported. Only "tf" or "krm" are valid'
          ' values.'
      )

  return template_resolver
