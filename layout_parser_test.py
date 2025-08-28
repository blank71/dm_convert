import pathlib

import errors
import layout_parser
import resource_reader
from absl.testing import absltest


class LayoutParserBuildTest(absltest.TestCase):

  def test_layout_without_type_error(self):

    layout_path = (
        resource_reader.get_testdata_dir() /
        pathlib.Path('layout_tests/layout_without_type.yaml')
    )
    with self.assertRaises(errors.InvalidLayoutError):
      layout_parser.LayoutParser(layout_path)

  def test_layout_without_name_error(self):

    layout_path = (
        resource_reader.get_testdata_dir() /
        pathlib.Path('layout_tests/layout_without_name.yaml')
    )
    with self.assertRaises(errors.InvalidLayoutError):
      layout_parser.LayoutParser(layout_path)

  def test_wrong_layout_path_error(self):

    layout_path = (
        resource_reader.get_testdata_dir() /
        pathlib.Path('layout_tests/xyz.yaml')
    )
    with self.assertRaises(FileNotFoundError):
      layout_parser.LayoutParser(layout_path)

  def test_template_not_calling_resource_error(self):

    layout_path = (
        resource_reader.get_testdata_dir() /
        pathlib.Path('layout_tests/template_not_calling_resource.yaml')
    )
    with self.assertRaises(errors.InvalidLayoutError):
      layout_parser.LayoutParser(layout_path)

  def test_non_template_calling_resource_error(self):

    layout_path = (
        resource_reader.get_testdata_dir() /
        pathlib.Path('layout_tests/non_template_calling_resource.yaml')
    )
    with self.assertRaises(errors.InvalidLayoutError):
      layout_parser.LayoutParser(layout_path)


class LayoutParserTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.layout_path = resource_reader.get_testdata_dir() / pathlib.Path(
        'layout_tests/correct_layout.yaml'
    )
    self.layout = layout_parser.LayoutParser(self.layout_path)

  def test_parent_method(self):
    self.assertEqual('module.main', self.layout.get_parent('qux'))
    self.assertEqual('module.bar', self.layout.get_parent('def'))
    self.assertEqual('module.abc', self.layout.get_parent('abc_leaf'))
    self.assertEqual('module.main', self.layout.get_parent('module.foo'))

    with self.assertRaises(errors.InvalidQueryError):
      self.layout.get_parent('this_name_does_not_exist')

  def test_template_name(self):
    self.assertEqual('main', self.layout.get_template_name('qux'))
    self.assertEqual('bar_template', self.layout.get_template_name('def'))
    self.assertEqual('abc_template', self.layout.get_template_name('abc_leaf'))
    self.assertEqual(
        'foo_template', self.layout.get_template_name('module.abc')
    )

    with self.assertRaises(errors.InvalidQueryError):
      self.layout.get_template_name('this_name_does_not_exist')

  def test_module_path_name(self):
    self.assertEqual('module.main', self.layout.get_module_path('qux'))
    self.assertEqual(
        'module.main.module.bar', self.layout.get_module_path('def')
    )
    self.assertEqual(
        'module.main.module.foo.module.abc',
        self.layout.get_module_path('abc_leaf'),
    )
    self.assertEqual(
        'module.main.module.foo', self.layout.get_module_path('module.abc')
    )

    with self.assertRaises(errors.InvalidQueryError):
      self.layout.get_module_path('this_does_not_exist')

  def test_calls_template(self):

    self.assertTrue(self.layout.calls_template.get('module.main'))
    self.assertTrue(self.layout.calls_template.get('module.bar'))
    self.assertTrue(self.layout.calls_template.get('module.foo'))
    self.assertFalse(self.layout.calls_template.get('branch'))

  def test_relative_module_path_name(self):

    self.assertIsNone(
        self.layout.get_relative_module_path('abc_leaf', 'branch')
    )
    self.assertEqual(
        'module.tree',
        self.layout.get_relative_module_path('module.abc', 'branch'),
    )
    self.assertIsNone(self.layout.get_relative_module_path('branch', 'cat'))

  def test_depth(self):
    self.assertEqual(3, self.layout.get_depth('abc_leaf'))
    self.assertEqual(2, self.layout.get_depth('module.abc'))
    self.assertEqual(2, self.layout.get_depth('def'))
    self.assertEqual(1, self.layout.get_depth('qux'))
    self.assertEqual(1, self.layout.get_depth('module.foo'))

    with self.assertRaises(errors.InvalidQueryError):
      self.layout.get_depth('this_does_not_exist')

  def test_inputs(self):
    actual = {'machineType': 'foomachine', 'zone': 'foozone'}
    self.assertEqual(actual, self.layout.inputs['module.foo'])

    actual = {'machineType': 'barmachine', 'zone': 'barzone'}
    self.assertEqual(actual, self.layout.inputs['module.bar'])

    self.assertIsNone(self.layout.inputs.get('module.abc'))

  def test_reverse_maps(self):
    actual = {'foomachine': 'machineType', 'foozone': 'zone'}
    self.assertEqual(actual, self.layout.reverse_maps['module.foo'])

    actual = {'barmachine': 'machineType', 'barzone': 'zone'}
    self.assertEqual(actual, self.layout.reverse_maps['module.bar'])

    self.assertEqual({}, self.layout.reverse_maps.get('module.abc'))


if __name__ == '__main__':
  absltest.main()
