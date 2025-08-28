import contextlib
import io
import pathlib
import sys

import conversion_logger_setting
import dm_convert
import errors
import resource_reader
from absl.testing import absltest
from absl.testing import parameterized

_DM_CONFIG = """
imports:
- path: import.jinja

resources:
- name: custom-topic
  type: import.jinja
"""

_IMPORT_TEMPLATE = """
resources:
- name: test-resource
  properties:
    description: Fake resource.
    topic: pubsub-topic
  type: gcp-types/foo-v1:bar.res
"""

_KRM_TEMPLATE = """apiVersion: foo.cnrm.cloud.google.com/v1bar
kind: FooBar
metadata:
  name: "{{ resource['name'] }}"
  description: {{ resource['properties']['description'] }}
"""

_KRM_CONFIG = """apiVersion: foo.cnrm.cloud.google.com/v1bar
kind: FooBar
metadata:
  description: Fake resource.
  name: test-resource
"""

_TF_TEMPLATE = """
resource "google_foo_bar" "{{ resource['name'] | replace("-", "_") }}" {
  name = "{{ resource['name'] }}"
  description = "{{ resource['properties']['description'] }}"
}"""

_FAKE_PROVIDER_TEMPLATE = """provider "{{provider}}" {
  project = "{{project_id}}"
}
"""
_TF_CONFIG = """provider "google-beta" {
  project = "None"
}

resource "google_foo_bar" "test_resource" {
  name = "test-resource"
  description = "Fake resource."
}
"""

_TEMPLATES = {'TF': _TF_TEMPLATE, 'KRM': _KRM_TEMPLATE}
_OUTPUT = {'TF': _TF_CONFIG, 'KRM': _KRM_CONFIG}

_FAKE_KIND_MAP = 'gcp-types/foo-v1:bar.res: fake'


class ConverterRunnerTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self._test_configs_dir = pathlib.Path(
        self.create_tempdir('configs').full_path
    )
    conversion_logger_setting.init('test_run_id', True, None)

  @parameterized.named_parameters(('krm', 'KRM'), ('tf', 'TF'))
  def test_converter_expands_and_converts_dm_config_to(self, output_format):
    self._templates_dir = (
        pathlib.Path(self.create_tempdir('templates').full_path)
        / pathlib.Path(output_format.lower())
        / 'templates'
    )

    config = self._test_configs_dir / 'config.yaml'
    self._write_to_temp_file(config, content=_DM_CONFIG)
    fake_template_map = self._templates_dir.with_suffix('.yaml')
    self._write_to_temp_file(fake_template_map, content=_FAKE_KIND_MAP)
    fake_template = self._templates_dir / 'fake.jinja'
    self._write_to_temp_file(fake_template, content=_TEMPLATES[output_format])
    fake_provider_template = self._templates_dir / 'tf_provider.jinja'
    self._write_to_temp_file(
        fake_provider_template, content=_FAKE_PROVIDER_TEMPLATE
    )
    fake_import = self._test_configs_dir / 'import.jinja'
    self._write_to_temp_file(fake_import, content=_IMPORT_TEMPLATE)

    output_file = self._test_configs_dir / 'converted.out'

    converter = dm_convert.get_converter(
        output_format,
        templates_dir=self._templates_dir,
        skip_unsupported_fields=False,
    )
    runner = dm_convert.ConverterRunner(
        config_file=config,
        output_file=output_file,
        namespace='',
        project_id=None,
        project_number=0,
        deployment_name=None,
        converter=converter,
    )

    runner.run()

    self.assertTrue(pathlib.Path(output_file).exists())
    with open(output_file) as f:
      self.assertEqual(_OUTPUT[output_format], f.read())

  def test_converter_with_input_string_to_tf(self):
    converter = dm_convert.get_converter('TF', skip_unsupported_fields=True)
    runner = dm_convert.ConverterRunner(
        config_file='',
        output_file='',
        namespace='',
        project_id=None,
        project_number=0,
        deployment_name=None,
        converter=converter,
    )
    dm_template = """
      resources:
      - name: test-resource
        properties:
          description: Fake resource.
          topic: pubsub-topic
        type: compute.v1.instance
      """
    result = runner.run_on_string(dm_template)
    self.assertEqual(result, 'Pass')

  @parameterized.named_parameters(('krm', 'KRM'), ('tf', 'TF'))
  def test_typed_referenced_value_not_found_raises_unsupported_reference_error(
      self, output_format
  ):
    self._run_test_asserting_exception_raised(
        resource_reader.get_testdata_dir()
        / pathlib.Path('invalid_inputs/reference_not_found.yaml'),
        output_format,
        errors.UnsupportedReferenceError,
    )

  @parameterized.named_parameters(('krm', 'KRM'), ('tf', 'TF'))
  def test_malformed_file_raises_scanner_error(self, output_format):
    self._run_test_asserting_exception_raised(
        resource_reader.get_testdata_dir()
        / pathlib.Path('invalid_inputs/malformed_yaml.yaml'),
        output_format,
        errors.CorruptedInputError,
    )

  @parameterized.named_parameters(('krm', 'KRM'), ('tf', 'TF'))
  def test_corrupted_file_raises_corrupted_input_error(self, output_format):
    self._run_test_asserting_exception_raised(
        resource_reader.get_testdata_dir()
        / pathlib.Path('invalid_inputs/corrupted_file.yaml'),
        output_format,
        errors.CorruptedInputError,
    )

  @parameterized.named_parameters(('krm', 'KRM'), ('tf', 'TF'))
  def test_imported_template_not_found_raises_invalid_input_exception(
      self, output_format
  ):
    self._run_test_asserting_exception_raised(
        resource_reader.get_testdata_dir()
        / pathlib.Path('invalid_inputs/imported_template_not_found.yaml'),
        output_format,
        errors.ExpansionFailedError,
    )

  @parameterized.named_parameters(('krm', 'KRM'))
  def test_type_not_yet_supported_raises_resource_type_not_found_error(
      self, output_format
  ):
    self._run_test_asserting_exception_raised(
        resource_reader.get_testdata_dir()
        / pathlib.Path(
            'invalid_inputs/resource_type_not_yet_supported/'
            'deployment_containing_unsupported_resource_type.yaml'
        ),
        output_format,
        errors.UnsupportedResourceTypeError,
    )

  @parameterized.named_parameters(('krm', 'KRM'))
  def test_action_raises_contains_action_error_krm(self, output_format):
    self._run_test_asserting_exception_raised(
        resource_reader.get_testdata_dir()
        / pathlib.Path('invalid_inputs/contains_action.yaml'),
        output_format,
        errors.ContainsActionError,
    )

  def _run_test_asserting_exception_raised(
      self, test_file_path, output_format, expected_exception
  ):
    converter = dm_convert.get_converter(
        output_format,
        skip_unsupported_fields=False,
        templates_dir=resource_reader.get_templates_dir(output_format.lower()),
    )
    output_file = self.create_tempfile('output-file')
    runner = dm_convert.ConverterRunner(
        config_file=test_file_path,
        output_file=pathlib.Path(output_file.full_path),
        converter=converter,
        namespace='',
        project_id='',
        project_number=0,
        deployment_name='',
    )

    with self.assertRaises(expected_exception):
      runner.run()
      with open(output_file, 'r') as f:
        for line in f:
          print(line, end='')

  def test_type_not_yet_supported(self):
    self._run_test_asserting_unsupported_resource(
        resource_reader.get_testdata_dir()
        / pathlib.Path(
            'invalid_inputs/resource_type_not_yet_supported/'
            'deployment_containing_unsupported_resource_type.yaml'
        ),
        'TF',
    )

  def _run_test_asserting_unsupported_resource(
      self, test_file_path, output_format
  ):
    output_dir = self.create_tempdir('output_dir')
    unsupported_resources_file = output_dir.create_file(
        'unsupported_resources.txt'
    )
    tf_import_file = output_dir.create_file('output_import_file')
    output_file = output_dir.create_file('output_file.tf')

    converter = dm_convert.get_converter(
        output_format,
        skip_unsupported_fields=False,
        tf_import_file=pathlib.Path(tf_import_file.full_path),
        templates_dir=resource_reader.get_templates_dir(output_format.lower()),
    )

    runner = dm_convert.ConverterRunner(
        config_file=test_file_path,
        output_file=pathlib.Path(output_file.full_path),
        converter=converter,
        namespace='',
        project_id='',
        project_number=0,
        deployment_name='',
    )
    try:
      runner.run()
    except errors.UnsupportedResourceTypeError:
      pass
    else:
      resource_file_path = resource_reader.get_testdata_dir() / pathlib.Path(
          'invalid_inputs/resource_type_not_yet_supported/resources_supported.tf'
      )
      with open(resource_file_path) as from_file:
        expected = from_file.read()
      with open(output_file) as output_resource_file:
        self.assertEqual(expected, output_resource_file.read())

      unsupported_resource_file_path = resource_reader.get_testdata_dir() / pathlib.Path(
          'invalid_inputs/resource_type_not_yet_supported/'
          'unsupported_resources.txt'
      )
      with open(unsupported_resource_file_path) as expected_unsupported_file:
        expected = expected_unsupported_file.read()

      with open(unsupported_resources_file) as output_unsupported_file:
        self.assertEqual(expected, output_unsupported_file.read())
    finally:
      # Ensure that the output file is always closed,
      # even if an exception is raised.
      if isinstance(output_file, io.FileIO):
        output_file.close()

  def _write_to_temp_file(self, fake_template_map, content=_FAKE_KIND_MAP):
    with open(self.create_tempfile(str(fake_template_map)).full_path, 'w') as f:
      f.writelines(content)


class ErrorsTest(absltest.TestCase):

  def test_excepthook(self):
    err = io.StringIO()
    try:
      raise errors.UnsupportedReferenceError('Custom message')
    except errors.UnsupportedReferenceError:
      except_hook_args = sys.exc_info()

    sys.excepthook = dm_convert.except_hook
    with contextlib.redirect_stderr(err):
      sys.excepthook(*except_hook_args)
    self.assertRegex(
        err.getvalue(),
        r'^E.*dm_convert.py:\d+] '
        r'UnsupportedReferenceError: Custom message\n$',
    )


if __name__ == '__main__':
  absltest.main()
