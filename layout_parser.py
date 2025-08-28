"""Defines a LayoutParser Class that captures the structure of the deployment."""

from collections.abc import MutableMapping
import pathlib
from typing import Any, Optional

from absl import logging
import yaml

import errors


class LayoutParser:
  """This class captures the structure of the deployment.

  Attributes:
    layout_file: Contains the path of layout file.
    parent: Mapping containing the parent of the sub-layouts.
    template: Mapping containing what template the sub-layout belongs to.
    calls_template: Mapping containing whether sub-layout calls a template.
    path_name: Contains the location of the sub-layout as a string.
    inputs: Inputs what the current sub-layout passes to its child.
    reverse_maps: Reverse mapping of the inputs.
    depth: Mapping containing the depth of the sub-layouts.
    layout: Layout file content.
  """

  def __init__(self, layout_file: Optional[pathlib.Path] = None,
               layout: Optional[MutableMapping[str, Any]] = None):
    self.layout_file = layout_file
    self.parent = {}
    self.template = {}
    self.calls_template = {}
    self.path_name = {}
    self.inputs = {}
    self.reverse_maps = {}
    self.depth = {}
    self.layout = layout
    self._file_type = ('.py', '.jinja')
    self._build(self.generate_layout(), 'main', 'main', '', 0)
    self._build_reverse_maps()
    logging.info('Successfully processed the layout file')

  def generate_layout(self) -> MutableMapping[str, Any]:
    if self.layout is not None:
      self.layout['name'] = 'main'
      self.layout['type'] = 'main.py'
      return self.layout
    return self.read_file()

  def read_file(self) -> MutableMapping[str, Any]:
    """Reads the layout file and initializes the placeholder."""
    layout_content = None
    if self.layout_file is None or not self.layout_file.is_file():
      raise FileNotFoundError(
          f'--layout file "{self.layout_file}" does not exist or cannot be'
          ' accessed.'
      )
    with open(self.layout_file, 'r') as opened_layout_file:
      layout_content = opened_layout_file.read()
    opened_layout_file.close()

    loaded_layout = yaml.safe_load(layout_content)
    loaded_layout['name'] = 'main'
    loaded_layout['type'] = 'main.py'
    logging.info('Successfully loaded the layout file.')
    return loaded_layout

  def _build(
      self,
      layout: MutableMapping[str, Any],
      parent: str,
      template: str,
      path: str,
      depth: int,
  ):
    """Builds the corresponding mapppings defined in the attributes recursively.

    Args:
      layout: The name of the current layout.
      parent: Stores the parent name
      template: Stores what template the current layout is part of
      path: Path in the form of terraform equivalent module
      depth: Tree depth of the resource.
    """
    if layout.get('name') is None or layout.get('type') is None:
      raise errors.InvalidLayoutError(
          'Encountered a child layout without a name or type.'
      )
    if (
        not (
            layout['type'].endswith(self._file_type)
        )
        and layout.get('resources') is not None
    ):
      raise errors.InvalidLayoutError('Not a Template but calls more resources')
    if (
        layout['type'].endswith(self._file_type)
    ) and layout.get('resources') is None:
      raise errors.InvalidLayoutError(
          'Not a template type but has more resources as its child'
      )

    layout_name = None
    if layout.get('resources') is not None:
      layout_name = '.'.join(['module', layout.get('name')])
      self.calls_template[layout_name] = True
      layout_path = (
          '.'.join([path, layout_name]) if path else layout_name
      )
      for resource in layout.get('resources'):
        self._build(
            resource,
            layout_name,
            layout['type'].split('.')[0],
            layout_path,
            depth+1,
        )
      self.inputs[layout_name] = layout.get('properties')
    else:
      layout_name = layout.get('name')
      self.calls_template[layout_name] = False

    self.template[layout_name] = template
    self.parent[layout_name] = parent
    self.path_name[layout_name] = path
    self.depth[layout_name] = depth

  def _build_reverse_maps(self):
    for layout_name in self.inputs:
      if layout_name not in self.reverse_maps:
        self.reverse_maps[layout_name] = {}
      if self.inputs[layout_name] is None:
        continue
      for (property_name, value) in self.inputs[layout_name].items():
        self.reverse_maps[layout_name][str(value)] = property_name

  def get_relative_module_path(
      self, dependent: str, dependee: str
  ) -> Optional[str]:
    """Takes in two layout names and finds the relative module path.

    Args:
      dependent: The layout name that depends on dependee.
      dependee: The resource name that is being depended on.

    Returns:
      returns a relative module path or
      None if the input is coming from its parent.
    """
    parent_list = self.get_module_path(dependent).split('.')
    child_list = self.get_module_path(dependee).split('.')
    if len(parent_list) > len(child_list):
      return None
    for index, value in enumerate(parent_list):
      if value != child_list[index]:
        return None
    return '.'.join(child_list[len(parent_list) :])

  def get_parent(self, layout_name: str) -> str:
    """Finds the corresponding parent of a given layout name.

    Args:
      layout_name: The parent of the layout name we want.

    Returns:
      Corresponding parent.
    """
    if layout_name in self.parent:
      return self.parent[layout_name]
    raise errors.InvalidQueryError('Invalid layout_name')

  def get_template_name(self, layout_name: str) -> str:
    """Finds the corresponding template name of a given layout name.

    Args:
      layout_name: The template name of the layout we want.

    Returns:
      Corresponding template name.
    """
    if layout_name in self.template:
      return self.template[layout_name]
    raise errors.InvalidQueryError('Invalid layout_name')

  def get_module_path(self, layout_name: str) -> str:
    """Finds the corresponding module path of a given layout name.

    Args:
      layout_name: The module path of the layout name we want.

    Returns:
      Corresponding module path.
    """
    if layout_name in self.path_name:
      return self.path_name[layout_name]
    raise errors.InvalidQueryError('Invalid layout_name')

  def get_depth(self, layout_name: str) -> int:
    """Finds the corresponding depth of a given layout name.

    Args:
      layout_name: The tree depth of the layout name we want.

    Returns:
      Corresponding depth.
    """
    if layout_name in self.depth:
      return self.depth[layout_name]
    raise errors.InvalidQueryError('Invalid layout_name')
