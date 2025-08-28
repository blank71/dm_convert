import pathlib

import yaml

import errors
import layout_parser
import property_parser
import resource_reader
from absl.testing import absltest


class PropertyParserPropertiesTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.layout_path = resource_reader.get_testdata_dir() / pathlib.Path(
        'property_parser_test/layout_file.yaml'
    )
    self.layout = layout_parser.LayoutParser(self.layout_path)
    self.property_parser = property_parser.PropertyParser(self.layout)

  def test_parse_variables(self):
    self.assertEqual(
        '${var.some_name}', self.property_parser.parse_variable('some_name'))
    self.assertEqual(
        '${var.abcdef}', self.property_parser.parse_variable('abcdef'))

  def test_flag_as_not_default(self):
    self.property_parser.template_type = 'some_template'
    self.property_parser.flag_as_non_default('some_name')
    self.property_parser.flag_as_non_default('other_property')
    self.property_parser.template_type = 'other_template'
    self.property_parser.flag_as_non_default('important')
    self.property_parser.flag_as_non_default('other_property')
    actual = {
        'some_template': {'some_name': True, 'other_property': True},
        'other_template': {'important': True, 'other_property': True},
    }
    self.assertEqual(actual, self.property_parser.not_default)

  def test_change_to_variable(self):
    self.property_parser.processed_variables = {
        'some_template': {'some_name': 'template_name'},
        'other_template': {'other_name': 'other_template_name'},
    }
    self.property_parser.layoutparser.inputs['placeholder'] = {}
    self.property_parser.resource_parent = 'placeholder'

    self.property_parser.template_type = 'some_template'
    self.property_parser.change_to_variable(
        'some_name', 'property', 'property_name'
    )
    self.property_parser.change_to_variable(
        'abc_type', 'property', 'abc_property_name'
    )

    self.property_parser.template_type = 'other_template'
    self.property_parser.change_to_variable(
        'other_name', '', 'other_property_name'
    )
    self.property_parser.change_to_variable(
        'type', 'property', 'compute_instance'
    )

    self.property_parser.template_type = 'template'
    self.property_parser.change_to_variable('name', '', 'template_name')
    actual = {
        'some_template': {
            'some_name': 'template_name',
            'property_some_name': 'property_name',
            'abc_type': 'abc_property_name',
        },
        'other_template': {
            'other_name': 'other_template_name',
            '_other_name': 'other_property_name',
            'property_type': 'compute_instance',
        },
        'template': {'name': 'template_name'},
    }

    self.assertEqual(actual, self.property_parser.processed_variables)

  def test_move_to_parent(self):
    self.property_parser.layoutparser.inputs = {
        'module_1': {},
        'module_2': {'name': 'template_name', 'reference': 'reference_name'},
    }

    self.property_parser.move_to_parent('name', 'template_name', 'module_1')
    self.property_parser.move_to_parent(
        'reference', 'some_reference', 'module_1')
    self.property_parser.move_to_parent(
        'reference', 'some_reference', 'module_2')
    actual = {
        'module_1': {'name': 'template_name', 'reference': 'some_reference'},
        'module_2': {
            'name': 'template_name',
            'reference': 'some_reference',
        },
    }
    self.assertEqual(actual, self.property_parser.layoutparser.inputs)

  def test_resolve_reference(self):
    self.property_parser.references = {'reference-1': {'selfLink': 'ID'}}
    self.property_parser.resolve_reference('reference-2', 'selfLink')
    actual = {
        'reference-1': {
            'selfLink': 'ID',
        },
        'reference-2': {'selfLink': 'ID'},
    }
    self.assertEqual(actual, self.property_parser.references)

  def test_resolve_reference_error(self):
    with self.assertRaises(errors.InvalidReferenceError):
      self.property_parser.resolve_reference('reference-1', 'some_type')

  def test_check_dependency(self):
    self.assertEqual(
        False, self.property_parser.check_dependency('vm-1', ['network-1'])
    )
    self.assertEqual(
        True, self.property_parser.check_dependency('vm-1', ['vm-network'])
    )

  def test_parse(self):
    resource = {'name': 'testing', 'list': [{'type1': 'a', 'type': 'b'}]}
    self.property_parser.layoutparser.inputs['parent'] = {}
    self.property_parser.resource_parent = 'parent'
    actual = {
        'name': '${var.name}',
        'list': [{'type1': '${var.type1}', 'type': '${var.list_type}'}],
    }
    self.assertEqual(actual, self.property_parser.parse(resource, 'parent'))


class PropertyParserTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.layout_path = resource_reader.get_testdata_dir() / pathlib.Path(
        'property_parser_test/variables_test/layout_file.yaml'
    )
    self.layout = layout_parser.LayoutParser(self.layout_path)
    self.property_parser = property_parser.PropertyParser(self.layout)
    self.config_path = resource_reader.get_testdata_dir() / pathlib.Path(
        'property_parser_test/variables_test/config_file.yaml'
    )
    self.config = None
    with open(self.config_path, 'r') as opened_config_file:
      self.config = yaml.safe_load(opened_config_file.read())['resources']
    opened_config_file.close()
    for resource in self.config:
      self.property_parser.process(resource)
    self.root_dir = resource_reader.get_testdata_dir() / pathlib.Path(
        'property_parser_test/variables_test/'
    )

  def test_get_variables(self):
    with open(self.root_dir / 'vm_template/variables.tf', 'r') as var_file:
      file_content = var_file.read()
    self.assertEqual(
        file_content, self.property_parser.get_variables('vm_template')
    )

    with open(self.root_dir / 'network_template/variables.tf', 'r') as var_file:
      file_content = var_file.read()
    self.assertEqual(
        file_content, self.property_parser.get_variables('network_template')
    )
    variables = {'name': 'vm', 'boolean_property': 'true',
                 'random_property': 'cat'}
    not_default = {'name': True}
    self.assertEqual(file_content, self.property_parser.get_variables(
        variables_dict=variables, not_default_dict=not_default))

    with open(self.root_dir /'firewall_template/variables.tf', 'r') as var_file:
      file_content = var_file.read()
    self.assertEqual(
        file_content, self.property_parser.get_variables('firewall_template')
    )

  def test_get_variables_error(self):
    with self.assertRaises(errors.InvalidQueryError):
      self.property_parser.get_variables('invalid_template')
    with self.assertRaises(errors.InvalidInputsError):
      self.property_parser.get_variables()

  def test_get_outputs(self):
    with open(self.root_dir / 'network_template/outputs.tf', 'r') as var_file:
      file_content = var_file.read()
    self.assertEqual(
        file_content, self.property_parser.get_outputs('network_template')
    )
    self.assertEqual(
        '', self.property_parser.get_outputs('firewall_template')
    )

  def test_move_to_parent(self):

    actual_inputs = {
        'property1': 'foo',
        'network': 'network-1',
        'property2': 'bar',
        'name': 'vm-1',
        'dependsOn': ['network-1'],
    }
    actual_reverse_maps = {
        'foo': 'property1',
        'network-1': 'network',
        'bar': 'property2',
        'vm-1': 'name',
        "['network-1']": 'dependsOn',
    }
    self.assertEqual(
        actual_inputs, self.property_parser.layoutparser.inputs['module.vm-1']
    )
    self.assertEqual(
        actual_reverse_maps,
        self.property_parser.layoutparser.reverse_maps['module.vm-1']
    )

    actual_inputs = {'name': 'network-1'}
    actual_reverse_maps = {'network-1': 'name'}
    self.assertEqual(
        actual_inputs,
        self.property_parser.layoutparser.inputs['module.network-1']
    )
    self.assertEqual(
        actual_reverse_maps,
        self.property_parser.layoutparser.reverse_maps['module.network-1']
    )

  def test_processed_variables(self):
    actual = {
        'name': 'vm-1',
        'property1': 'foo',
        'property2': 'bar',
        'property3': 'baz',
        'network': '$(ref.network-1.selfLink)',
    }
    self.assertEqual(
        actual, self.property_parser.processed_variables['vm_template']
    )

  def test_selective_conversion_of_variables(self):
    """Create a mock environment where there is another vm-3 module."""
    self.layout.template['vm-3'] = 'vm-template'
    self.layout.parent['vm-3'] = 'module.vm-3'
    self.layout.inputs['module.vm-3'] = {'network': 'network-2'}
    resource = {
        'name': 'vm-3',
        'properties': {'network': '$(ref.network-2.selfLink)'},
        'type': 'compute.v1.instance',
    }
    self.property_parser.process(resource)
    self.assertIsNotNone(self.property_parser.references.get('network-2'))


if __name__ == '__main__':
  absltest.main()
