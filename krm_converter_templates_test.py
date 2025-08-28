"""Tests for krm_converter.

Unittests comparing result of conversion to KRM format
of various GCP resources types.
"""
import pathlib

import yaml

import krm_converter
import resource_reader
import template_resolver
from absl.testing import absltest
from absl.testing import parameterized


def _get_testable_dirs() -> list[pathlib.Path]:
  for cur_dir, _, files in resource_reader.walk_testdata_folder():
    if 'krms.yaml' in files and 'deployment.yaml' in files:
      yield pathlib.Path(cur_dir)


class KrmConvertTemplateTest(parameterized.TestCase):

  def _convert_dm_config(self, config_dir: pathlib.Path):
    dm_content = yaml.safe_load(
        resource_reader.read_resource_bytes(
            config_dir.joinpath('deployment.yaml')))
    dm_resources = dm_content.get('resources')
    return list(yaml.safe_load_all(self.converter.convert(dm_resources, '')))

  def _assert_krm_equal(self, expected_krms, actual_krms):
    """Compares two KRM configs.

    KRM container may contain KRM instances in any order. This assert converts
    sequences into dictionaries, and compares them.

    Args:
      expected_krms: list of expected KRMs.
      actual_krms: list of actual KRMs.
    """

    def _get_krm_name(krm):
      kind, name = krm['kind'], krm['metadata']['name'].lower()
      return f'{kind}{name}'

    def _make_krm_map(krms):
      return {_get_krm_name(krm): krm for krm in krms}

    self.assertIsInstance(
        expected_krms, list, msg='Expected KRM resources not a list.')
    self.assertIsInstance(
        actual_krms, list, msg='Actual KRM resources not a list.')
    self.assertEqual(len(expected_krms), len(expected_krms))
    actual_krm_dict = _make_krm_map(actual_krms)
    expected_krm_dict = _make_krm_map(expected_krms)
    self.assertDictEqual(expected_krm_dict, actual_krm_dict)

  def _test_template_one_case(self, test_dir: pathlib.Path):
    msg = '/'.join(test_dir.parts[-2:])
    with self.subTest(msg=msg):
      actual = self._convert_dm_config(test_dir)
      expected = list(
          yaml.safe_load_all(
              resource_reader.read_resource_bytes(
                  test_dir.joinpath('krms.yaml'))))
      self._assert_krm_equal(expected, actual)

  def setUp(self):
    super().setUp()
    templates_dir = resource_reader.get_templates_dir('krm')
    self.converter = krm_converter.KrmConverter(
        templates_dir=templates_dir,
        template_resolver=template_resolver.get_instance('krm', templates_dir))

  # pylint: disable=g-complex-comprehension
  @parameterized.named_parameters({
      # generates test case names by taking the folder name of each test case in
      # 'testdata/', for example:
      # 'test_convert_templates_all_:gcp_bigquery_dataset/gcp-bigquery-dataset'
      'testcase_name': f':{"/".join(path.parts[-2:])}',
      'path': path,
  } for path in _get_testable_dirs())
  def test_convert_templates_all(self, path):
    self._test_template_one_case(path)

  # Use to debug one test in `test_convert_templates_all`.
  # `blaze test :krm_converter_templates_test \
  # --test_filter=KrmConvertTemplateTest.test_convert_sample_case`
  def test_convert_sample_case(self):
    test_dir = resource_reader.get_testdata_dir().joinpath(
        'legacy_compute_vpntunnel/compute-vpntunnel')
    self._test_template_one_case(test_dir=test_dir)


if __name__ == '__main__':
  absltest.main()
