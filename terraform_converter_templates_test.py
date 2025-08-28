"""Tests for tf_converter.

Unittests comparing result of conversion to terraform format
of various GCP resources types.
"""
import pathlib
import pprint

import hcl2
import yaml

import resource_reader
import template_resolver
import tf_converter
from absl.testing import absltest
from absl.testing import parameterized


def _get_testable_dirs() -> list[pathlib.Path]:
  for cur_dir, _, files in resource_reader.walk_testdata_folder():
    if all(x in files for x in ('resources.tf', 'deployment.yaml')):
      yield pathlib.Path(cur_dir)


class TerraformConvertTemplatesTest(parameterized.TestCase):

  def _assert_terraform_configs_equal(self, expected_tfs: str, actual_tfs: str):
    """Compares two terraform configs.

    terraform container may contain terraform instances in any order.
    This assert converts sequences into dictionaries, and compares them.

    Args:
      expected_tfs: list of expected tfs.
      actual_tfs: list of actual tfs.
    """

    def _make_tf_map(tf):
      tf_resource_map = {}
      tfson = hcl2.loads(tf)
      for resource in tfson.get('resource', []) + tfson.get('data', []):
        # resource attributes are nested dicts, flatten first two levels
        for resource_type, resource_obj in resource.items():
          for resource_name, attributes in resource_obj.items():
            r = {f'{resource_type}_{resource_name}': attributes}
            tf_resource_map.update(r)
      return tf_resource_map

    actual_tf_dict = _make_tf_map(actual_tfs)
    expected_tf_dict = _make_tf_map(expected_tfs)

    self.assertLen(expected_tf_dict, len(actual_tf_dict))
    # compare each resource individually
    for expected_name, expected_resource in expected_tf_dict.items():
      self.assertIn(expected_name, actual_tf_dict)
      self.assertDictEqual(
          expected_resource,
          actual_tf_dict[expected_name],
          msg='\n'.join([
              f'in {expected_name}', 'expected:',
              pprint.pformat(expected_resource), 'actual:',
              pprint.pformat(actual_tf_dict[expected_name])
          ]))

  def _convert_dm_config(self, config_dir: pathlib.Path):
    dm_content = list(
        yaml.safe_load_all(
            resource_reader.read_resource_bytes(
                config_dir.joinpath('deployment.yaml'))))
    dm_resources = dm_content[0].get('resources')
    return self.converter.convert(dm_resources, '')

  def _test_template_one_case(self, test_dir: pathlib.Path):
    msg = '/'.join(test_dir.parts[-2:])
    with self.subTest(msg=msg):
      actual = self._convert_dm_config(test_dir)
      expected = resource_reader.read_resource_utf8(
          test_dir.joinpath('resources.tf'))
      self._assert_terraform_configs_equal(expected, actual)

  def setUp(self):
    super(TerraformConvertTemplatesTest, self).setUp()
    templates_dir = resource_reader.get_templates_dir('tf')
    self.converter = tf_converter.TerraformConverter(
        templates_dir=templates_dir,
        template_resolver=template_resolver.get_instance('tf', templates_dir),
        provider='google-beta')

  # pylint: disable=g-complex-comprehension
  @parameterized.named_parameters({
      'testcase_name': f':{"/".join(path.parts[-2:])}',
      'path': path,
  } for path in _get_testable_dirs())
  def test_convert_templates_all(self, path):
    self._test_template_one_case(path)

  # Use to debug one test in `test_convert_templates_all`.
  # `blaze test :terraform_converter_templates_test \
  # --test_filter=TerraformConvertTemplatesTest.test_convert_sample_case`
  def test_convert_sample_case(self):
    self._test_template_one_case(test_dir=resource_reader.get_testdata_dir(
    ).joinpath('legacy_compute_firewall/deny-rule-firewall'))


if __name__ == '__main__':
  absltest.main()
