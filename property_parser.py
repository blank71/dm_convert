"""Defines a property parser that converts all properties to variables.

It also handles what properties to set as output in terraform.
"""

from collections.abc import MutableMapping
import re
from typing import Any, Optional

from absl import logging
import jinja2

import errors
import layout_parser
import resource_reader
import template_resolver


class PropertyParser:
  """This class converts the properties of a resource into variables.

  Attributes:
    layoutparser: Layout Parser which captures the structure of deployment.
    processed_resources: Stores the processed templates.
    processed_variables: Stores the processed variables.
    not_default: Stores whether a template property has non default value.
    references: Stores references and its type for a template
    resolver: Template Resolver
    jinja_env: Creates a jinja environment.
    name: Placeholder for the current template name being processed.
    template_type: Placeholder for the current template type being processed.
    resource_parent: Placeholder for the current template parent being
    processed.
  """

  def __init__(self, layoutparser: layout_parser.LayoutParser):
    self.layoutparser = layoutparser
    self.processed_resources = {}
    self.processed_variables = {}
    self.not_default = {}
    self.references = {}
    templates_dir = resource_reader.get_templates_dir('tf')
    self.resolver = template_resolver.get_instance('tf', templates_dir)
    self.jinja_env = jinja2.Environment(
        keep_trailing_newline=True,
        loader=jinja2.FileSystemLoader(templates_dir))
    self.name = None
    self.template_type = ''
    self.resource_parent = ''

  def process(self, resource: MutableMapping[str, Any]):
    """Processes the Resource.

    Args:
      resource: The DM resource that we want to process.
    """
    self.name = resource.get('name')
    self.template_type = self.layoutparser.get_template_name(self.name)
    self.template_type = re.sub(r'-', '_', self.template_type)
    self.resource_parent = self.layoutparser.get_parent(self.name)

    if self.resource_parent != 'module.main':
      self.move_to_parent('name', resource['name'], self.resource_parent)

    if 'metadata' in resource and resource['metadata']['dependsOn'] is not None:
      if not self.check_dependency(
          self.name, resource['metadata']['dependsOn']
      ):
        self.move_to_parent('dependsOn', resource['metadata']['dependsOn'],
                            self.resource_parent)
        del resource['metadata']

    if self.processed_resources.get(self.template_type) is not None:
      self.parse(resource, '', False)
      return

    parsed_resource = self.parse(resource, '')
    parsed_resource['resource_name'] = self.template_type

    self.processed_resources[self.template_type] = parsed_resource
    self.name = None
    self.template_type = ''
    self.resource_parent = ''

  def parse(
      self,
      resource: MutableMapping[str, Any],
      parent: str,
      var_flag: bool = True,
  ) -> MutableMapping[str, Any]:
    """Recursively converts the properties to variables and marks outputs.

    Args:
      resource: DM resource dictionary.
      parent: Name of the parent
      var_flag: True to convert all properties else only references.

    Returns:
      Converted Resource Dictionary
    """
    for property_name in resource:
      if property_name == 'type' and not parent:
        continue

      if property_name == 'name' and var_flag:
        self.flag_as_non_default(property_name)
      if isinstance(resource[property_name], MutableMapping):
        resource[property_name] = self.parse(
            resource[property_name], property_name, var_flag
        )
      if isinstance(resource[property_name], str):
        convert_flag = True
        if '(ref' in resource[property_name]:
          reference_name = resource[property_name].split('.')[1]
          reference_type = resource[property_name].split('.')[-1][:-1]
          if (
              self.template_type in self.processed_resources and
              self.processed_resources[self.template_type].get(property_name)
              is not None
          ):
            convert_flag = False
          self.resolve_reference(reference_name, reference_type)

        if var_flag and convert_flag:
          resource[property_name] = self.change_to_variable(
              property_name, parent, resource[property_name]
          )

      if isinstance(resource[property_name], bool) and var_flag:
        resource[property_name] = self.change_to_variable(
            property_name, parent, str(resource[property_name]).lower()
        )

      if isinstance(resource[property_name], list):
        only_str = True
        for index, item in enumerate(resource[property_name]):
          if isinstance(item, dict):
            resource[property_name][index] = self.parse(
                item, property_name, var_flag
            )
            only_str = False
        if only_str and var_flag:
          resource[property_name] = self.change_to_variable(
              property_name, parent, resource[property_name]
          )

    return resource

  def check_dependency(self, dependent: str, dependees: list[str]) -> bool:
    for dependee in dependees:
      if (
          self.layoutparser.get_relative_module_path(dependent, dependee)
          is None
      ):
        return False
    return True

  def resolve_reference(self, reference_name: str, reference_type: str):
    """Resolves the reference.

    Args:
      reference_name: The name of the resource being referenced.
      reference_type: The type of reference.
    """
    if reference_name not in self.references:
      self.references[reference_name] = {}
    if reference_type == 'selfLink':
      self.references[reference_name][reference_type] = 'ID'
    else:
      raise errors.InvalidReferenceError(
          'The reference type %s is not supported.' % reference_type
      )

  def move_to_parent(self, key: str, value: str, parent: str):
    if parent not in self.layoutparser.reverse_maps:
      self.layoutparser.reverse_maps[parent] = {}
    if self.layoutparser.inputs[parent] is None:
      self.layoutparser.inputs[parent] = {}
    self.layoutparser.inputs[parent][key] = value
    self.layoutparser.reverse_maps[parent][str(value)] = key

  def change_to_variable(
      self, property_name: str, parent: str, value: Any
  ) -> str:
    """Assigns variable to the property and adds it in processed variables.

    Args:
      property_name: Property name to be converted to variable
      parent: Parent of the current property name
      value: The value corresponding to the property

    Returns:
      Returns the converted variable name.
    """
    if self.processed_variables.get(self.template_type) is None:
      self.processed_variables[self.template_type] = {}

    variable_name = property_name
    if (
        self.processed_variables[self.template_type].get(variable_name) is None
        and property_name != 'type'
    ):
      self.processed_variables[self.template_type][variable_name] = value
    else:
      variable_name = parent + '_' + property_name
      self.processed_variables[self.template_type][variable_name] = value

    parsed_name = self.parse_variable(variable_name)
    if variable_name in self.layoutparser.inputs[self.resource_parent]:
      self.flag_as_non_default(variable_name)

    return parsed_name

  def parse_variable(self, property_name: str) -> str:
    return '${var.%s}' % property_name

  def flag_as_non_default(self, property_name: str):
    """Marks the specific property of a template as not default.

    Args:
      property_name: the name of the property that does not has a default value.
    """
    if self.not_default.get(self.template_type) is None:
      self.not_default[self.template_type] = {}
    self.not_default[self.template_type][property_name] = True

  def get_variables(
      self,
      template_name: Optional[str] = None,
      variables_dict: Optional[MutableMapping[str, Any]] = None,
      not_default_dict: Optional[MutableMapping[str, Any]] = None,
  ) -> str:
    """Converts the variables dict into terraform equivalent string.

    Args:
      template_name: The name of the template.
      variables_dict: Dictionary containing the variables.
      not_default_dict: Dictionary containing the not default properties.
    Returns:
      Terraform converted template variables.
    """
    jinja_filename = 'variable_template.jinja'
    variables = None
    not_default = None
    template = self.jinja_env.get_template(jinja_filename)
    variables_list = []
    if template_name is not None:
      if self.processed_variables.get(template_name) is None:
        raise errors.InvalidQueryError(
            'The template name : %s is not processed and is not present'
            % template_name
        )
      variables = self.processed_variables[template_name]
      not_default = self.not_default[template_name]
    else:
      variables = variables_dict
      not_default = not_default_dict
    if variables is None:
      raise errors.InvalidInputsError(
          'The variables dictionary is not present.'
      )
    for property_name in variables:
      variable = {}
      variable['name'] = property_name
      if isinstance(variables[property_name], list):
        variable['isList'] = True

      if property_name not in not_default:
        variable['default'] = variables[property_name]
      converted_variable = template.render(resource=variable, context={})
      variables_list.append(converted_variable)

    return '\n\n'.join(variables_list)

  def get_outputs(self, template_name: str) -> str:
    """Returns terraform converted outputs for a template.

    Args:
      template_name: The name of the template.

    Returns:
      Terraform converted template outputs.
    """
    resource_name = self.processed_variables[template_name]['name']
    if self.references.get(resource_name) is None:
      logging.info('The template: %s has no outputs.', template_name)
      return ''
    jinja_filename = 'outputs_template.jinja'
    template = self.jinja_env.get_template(jinja_filename)
    outputs_list = []

    for reference_type in self.references[resource_name]:
      if reference_type == 'selfLink':
        resource_type = self.processed_resources[template_name]['type']
        terraform_template = self.resolver.resolve(
            resource_type, self.processed_resources[template_name]
        )
        output = {}
        output['name'] = (
            template_name + '_' + self.references[resource_name][reference_type]
        )
        output['reference'] = f'{terraform_template}.{template_name}.id'
        converted_output = template.render(resource=output, context={})
        outputs_list.append(converted_output)

    return '\n\n'.join(outputs_list)
