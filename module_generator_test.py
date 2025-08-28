import pathlib

import yaml

import layout_parser
import module_generator
import property_parser
import resource_reader
from absl.testing import absltest


class CreateModulesTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.layout_path = resource_reader.get_testdata_dir() / pathlib.Path(
        'property_parser_test/layout_file.yaml'
    )
    self.layout = layout_parser.LayoutParser(self.layout_path)
    self.property_parser = property_parser.PropertyParser(self.layout)
    self.leaves = ['vm-1', 'network-1', 'vm-2', 'firewall-1']
    self.template_dir = self.create_tempdir('template_dir')
    self.modules_dir = self.create_tempdir('templates_dir/modules')
    self.modules_class = module_generator.ModuleGenerator(
        self.leaves,
        self.layout,
        self.property_parser,
        pathlib.Path(self.template_dir.full_path),
        pathlib.Path(self.modules_dir.full_path),
    )

  def test_get_file_write_path(self):
    actual = self.modules_class.template_directory / 'main.tf'
    self.assertEqual(
        actual,
        self.modules_class.get_file_write_path(
            'module.vm-1', 'module.main', 'main'
        ),
    )
    actual = self.modules_class.module_directory / 'vm_template/variables.tf'
    self.assertEqual(
        actual,
        self.modules_class.get_file_write_path(
            'vm-1', 'module.vm-1', 'variables'
        ),
    )

  def test_add_to_file(self):
    actual = {}
    actual[str(self.modules_class.template_directory / 'main.tf')] = [
        'hi',
        'this is a test',
    ]
    module_path = str(
        self.modules_class.module_directory / 'vm_template/variables.tf'
    )
    actual[module_path] = ['inside the module!']
    file_content = {}
    self.modules_class.add_to_file(
        file_content, 'module.vm-1', 'module.main', 'hi', 'main'
    )
    self.modules_class.add_to_file(
        file_content, 'module.vm-1', 'module.main', 'this is a test', 'main'
    )
    self.modules_class.add_to_file(
        file_content, 'vm-1', 'module.vm-1', 'inside the module!', 'variables'
    )
    self.assertEqual(actual, file_content)

  def test_normalize_name(self):
    self.assertEqual(
        'module.vm_1', self.modules_class.normalize_name('module.vm-1')
    )
    self.assertEqual('a_name', self.modules_class.normalize_name('a-name'))

  def test_get_source(self):
    self.assertEqual(
        './modules/vm_template',
        self.modules_class.get_source('module.vm-1', 'vm-1'),
    )
    self.layout.template['child'] = 'child-module'
    self.assertEqual(
        '../child_module', self.modules_class.get_source('vm-1', 'child')
    )

  def test_get_property_name(self):
    self.assertEqual(
        'vm_1_name', self.modules_class.get_property_name('module.vm-1', 'name')
    )
    self.assertEqual(
        'network_name',
        self.modules_class.get_property_name('module.network', 'name'),
    )

  def test_resolve_inputs(self):
    self.modules_class.layout.inputs['module.main'] = {'parent_val': 'value'}
    self.modules_class.layout.reverse_maps['module.main'] = {
        'value': 'parent_val'
    }
    inputs = {
        'name': 'abc',
        'machine': 'big',
        'from_parent': 'value',
        'dependsOn': ['something_random'],
        'dependency1': 'network-1',
        'dependency2': 'module.main',
    }
    self.property_parser.references['network-1'] = {'selfLink': 'ID'}
    self.modules_class.leaves = ['network-1', 'module.main']
    properties, variables, not_default = self.modules_class.resolve_inputs(
        inputs, 'module.vm-1', 'vm-1', 'module.main')
    actual_properties = {
        'properties': {
            'name': 'abc',
            'machine': 'big',
            'from_parent': '${var.parent_val}',
            'dependency1': 'module.network_1.network_template_ID',
            'dependency2': '${var.vm_1_dependency2}',
            'source': './modules/vm_template'},
        'name': 'vm_1',
        'references': {'dependency1': True}}
    actual_variable = {'parent_val': 'value', 'vm_1_dependency2': 'module.main'}
    actual_not_default = {'parent_val': True, 'dependency2': True}
    actual_inputs_parent = {
        'vm_1_dependency2': 'module.main', 'parent_val': 'value'}
    actual_reverse_maps_parent = {
        'module.main': 'vm_1_dependency2', 'value': 'parent_val'}
    self.assertEqual(actual_properties, properties)
    self.assertEqual(actual_variable, variables)
    self.assertEqual(actual_not_default, not_default)
    self.assertEqual(actual_inputs_parent, self.layout.inputs['module.main'])
    self.assertEqual(actual_reverse_maps_parent,
                     self.modules_class.layout.reverse_maps['module.main'])
    actual_properties['properties'] = {'source': './modules/vm_template'}
    actual_properties['references'] = {}
    properties, _, _ = self.modules_class.resolve_inputs(
        None, 'module.vm-1', 'vm-1', 'module.main')
    self.assertEqual(actual_properties, properties)


class CreateModulesOutputTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.layout_path = resource_reader.get_testdata_dir() / pathlib.Path(
        'module_test/layout.yaml'
    )
    self.layout = layout_parser.LayoutParser(self.layout_path)
    self.property_parser = property_parser.PropertyParser(self.layout)
    self.config_path = self.layout_path.parent / 'config.yaml'
    self.config = None
    with open(self.config_path, 'r') as config_file:
      self.config = yaml.safe_load(config_file)['resources']
    config_file.close()
    for resource in self.config:
      self.property_parser.process(resource)
    self.leaves = ['vm-1', 'network-1']
    self.template_dir = self.create_tempdir('template_dir')
    self.modules_dir = self.create_tempdir('templates_dir/modules')
    self.modules_class = module_generator.ModuleGenerator(
        self.leaves,
        self.layout,
        self.property_parser,
        pathlib.Path(self.template_dir.full_path),
        pathlib.Path(self.modules_dir.full_path),
    )
    self.modules_class.process()

  def test_file_contents(self):
    actual = None
    with open(self.layout_path.parent / 'engine_module.txt', 'r') as file:
      actual = file.read()
    file.close()
    path = str(self.modules_class.module_directory / 'engine/main.tf')
    self.assertEqual(
        actual, '\n\n'.join(self.modules_class.main_file_content[path])
    )

    with open(self.layout_path.parent / 'engine_variables.txt', 'r') as file:
      actual = file.read()
    file.close()
    path = str(self.modules_class.module_directory / 'engine/variables.tf')
    self.assertEqual(
        actual, '\n\n'.join(self.modules_class.variable_file_content[path])
    )

    with open(self.layout_path.parent / 'main.txt', 'r') as file:
      actual = file.read()
    file.close()
    path = str(self.modules_class.template_directory / 'main.tf')
    self.assertEqual(
        actual, '\n\n'.join(self.modules_class.main_file_content[path])
    )

  def test_processed_resources(self):
    self.assertEqual(
        (-2, True), self.modules_class.processed_modules['module.vm-1']
    )
    self.assertEqual(
        (-2, True), self.modules_class.processed_modules['module.network-1']
    )
    self.assertEqual(
        (-1, True), self.modules_class.processed_modules['module.some_engine']
    )


if __name__ == '__main__':
  absltest.main()
