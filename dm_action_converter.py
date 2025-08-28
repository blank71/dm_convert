"""Converts DM actions into DM declarative equivalents."""

from collections.abc import Mapping, Sequence
from typing import Any, Optional

import base_converter

PROJECT_SET_IAM_POLICY = "gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy"


class DmActionConverter(base_converter.BaseConverter):
  """Deployment Manager (DM) Action to DM declarative resource converter."""

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    self._load_filters()

  def convert(
      self,
      actions: Sequence[Mapping[str, Any]],  # pytype: disable=signature-mismatch  # overriding-parameter-count-checks
      namespace: Optional[str],
  ) -> tuple[list[Mapping[str, Any]], str]:
    """Converts actions to DM declarative equivalents.

    Args:
      actions: Collection of DM actions, each of which is a dict.
      namespace: namespace to narrow down conversion scope.

    Returns:
      Tuple of actions that this converter could not convert, and a string
      representing all successfully converted actions in DM YAML format.
    """
    converted_resources = []
    unconvertible_actions = []
    for resource in actions:
      action = resource.get("action")
      if self.template_resolver.is_ignored(action):
        continue

      if not self.template_resolver.is_supported(action):
        unconvertible_actions.append(resource)
        continue

      if (
          action == PROJECT_SET_IAM_POLICY
          and "gcpIamPolicyPatch" not in resource.get("properties")
      ):
        # setIamPolicy actions that replace, not patch, a project are handled by
        # tf_converter instead.
        unconvertible_actions.append(resource)
        continue

      converted_resources.append(
          self.convert_resource(resource, context={}, output_format="action")
      )

    return unconvertible_actions, "\n\n".join(
        [r.strip() for r in converted_resources]
    )

  def _load_filters(self) -> None:
    """Loads custom Jinja filters."""
    self.jinja_env.filters.update({
        "is_list": lambda value: isinstance(value, list),
    })
