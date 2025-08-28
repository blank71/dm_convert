"""Creates the modules for templates."""

from collections.abc import MutableMapping
import pathlib
import queue
import re
from typing import Any

from absl import logging

import layout_parser
import property_parser


class ModuleGenerator:
  """This class creates the modules for templates.

  Attributes:
    leaves: Contains the leaf resources of the deployment.
    main_file_content: Dict to store the file paths and main file contents.
    variable_file_content: Dict to store the file paths and variable contents.
    layout: layout parser for the current deployment.
    property_parser: Property Parser for the current deployment
    queue: Priority queue initialized to process the modules.
    module_template: Jinja env for module template.
    template_directory: Directory of template conversion.
    module_directory: Dicrectory of modules.
    processed_modules: Contains already processed modules.
  """

  def __init__(
      self,
      leaves: list[str],
      layoutparser: layout_parser.LayoutParser,
      propertyparser: property_parser.PropertyParser,
      template_directory: pathlib.Path,
      module_directory: pathlib.Path,
  ):

    self.leaves = leaves
    self.main_file_content = {}
    self.variable_file_content = {}
    self.layout = layoutparser
    self.property_parser = propertyparser
    self.queue = queue.PriorityQueue()
    self.module_template = propertyparser.jinja_env.get_template(
        'module_template.jinja'
    )
    self.template_directory = template_directory
    self.module_directory = module_directory
    self.processed_modules: MutableMapping[str, Any] = {}
    self.prepare()

  def prepare(self,):
    for leaf_name in self.leaves:
      parent_name = self.layout.get_parent(leaf_name)
      parent_depth = self.layout.get_depth(parent_name)
      # Negative parent depth to process largest depth first.
      self.queue.put((-parent_depth, parent_name, leaf_name))

  def process(self,):
    """Processes the modules by using a priority queue."""

    while not self.queue.empty():
      depth, module_name, child_name = self.queue.get()
      logging.info('Currently processing module: %s', module_name)
      if module_name in self.processed_modules:
        continue
      parent_name = self.layout.get_parent(module_name)
      module_properties, variables, not_default = self.resolve_inputs(
          self.layout.inputs[module_name], module_name, child_name, parent_name
      )
      output = self.module_template.render(
          resource=module_properties, context={}
      )
      variables_out = self.property_parser.get_variables(
          variables_dict=variables, not_default_dict=not_default
      )

      self.add_to_file(self.main_file_content, module_name, parent_name,
                       output, 'main')
      if variables_out:
        self.add_to_file(self.variable_file_content, module_name,
                         parent_name, variables_out, 'variables')
      if parent_name != 'module.main':
        self.queue.put((depth+1, parent_name, module_name))
      self.processed_modules[module_name] = (depth, True)

  def add_to_file(
      self, file: MutableMapping[str, Any], module_name: str, parent_name: str,
      output: str, file_type: str,):
    path_to_write = str(
        self.get_file_write_path(module_name, parent_name, file_type)
    )
    if path_to_write not in file:
      file[path_to_write] = []
    file[path_to_write].append(output)

  def get_file_write_path(
      self, module_name: str, parent_name: str, file_type: str
  ) -> pathlib.Path:
    """Gets the path corresponding to arguments passed.

    Args:
      module_name: Name of the module.
      parent_name: Name of parent of the module.
      file_type: Type of file we need path of.[main, variables]

    Returns:
      The path corresponding to the arguments.
    """
    file_name = file_type + '.tf'
    if parent_name == 'module.main':
      path_to_write = self.template_directory / file_name
    else:
      template_name = self.normalize_name(
          self.layout.get_template_name(module_name))
      module_directory = self.module_directory / template_name
      module_directory.mkdir(parents=True, exist_ok=True)
      path_to_write = module_directory / file_name
    return path_to_write

  def resolve_inputs(
      self,
      inputs: MutableMapping[str, Any],
      module_name: str,
      child_name: str,
      parent_name: str,
  ) -> ...:
    """Resolves the inputs of a module with its parent.

    Args:
      inputs: Inputs the current module is passing to its child.
      module_name: Current module name.
      child_name: child name of the current module.
      parent_name: parent name of the current module.

    Returns:
      module_properties: Contains all the modified properties for main file.
      variables: Contains what variables are being used in the module
      not_default: Contains which variables are not default for the module.
    """

    properties = {}
    variables = {}
    not_default = {}
    references = {}
    if inputs is None:
      inputs = {}
    for property_name, value in inputs.items():
      if str(value) in self.layout.reverse_maps[parent_name]:
        parent_property_name = self.layout.reverse_maps[parent_name][str(value)]
        variables[parent_property_name] = value
        properties[property_name] = self.property_parser.parse_variable(
            parent_property_name
        )
        not_default[parent_property_name] = True
        continue

      if property_name == 'dependsOn':
        continue

      if value in self.leaves and property_name != 'name':
        relative_path = self.layout.get_relative_module_path(module_name, value)
        if relative_path is None:
          changed_property_name = self.get_property_name(
              module_name, property_name
          )
          self.property_parser.move_to_parent(
              changed_property_name, value, parent_name
          )
          properties[property_name] = self.property_parser.parse_variable(
              changed_property_name
          )
          variables[changed_property_name] = value
          not_default[property_name] = True

        else:
          reference_type = self.property_parser.references[value]['selfLink']
          reference = (self.normalize_name(
              relative_path+'.'+self.layout.get_template_name(value))
                       + '_' + reference_type)
          properties[property_name] = reference
          references[property_name] = True
      else:
        properties[property_name] = value
    module_properties: MutableMapping[str, Any] = {}
    module_properties['properties'] = properties
    module_properties['properties']['source'] = self.get_source(
        module_name, child_name,
    )
    module_properties['name'] = self.normalize_name(module_name.split('.')[-1])
    module_properties['references'] = references
    return module_properties, variables, not_default

  def normalize_name(self, name: str) -> str:
    """Normalizes the name by replacing hyphens with underscores."""
    return  re.sub(r'-', '_', name)

  def get_source(self, module_name: str, child_name: str) -> str:
    """Gets the source of the module being called."""
    template_name = self.normalize_name(
        self.layout.get_template_name(child_name).split('.')[0])
    if self.layout.get_parent(module_name) == 'module.main':
      return './modules/'+template_name
    else:
      return '../'+template_name

  def get_property_name(self, module_name: str, property_name: str) -> str:
    """Extracts the name from module definition and adds it to property name.

    Args:
      module_name: The name of the module defition.(module.<name>)
      property_name: name of the property.(<property>)
    Returns:
      The combined name and property name. (<name>_<property>)
    """
    return self.normalize_name(module_name.split('.')[-1] + '_' + property_name)
