import pathlib
import re
from unittest import mock

from absl import logging
import yaml

import conversion_logger
import errors
import resource_reader
import template_resolver
import tf_converter
import convert_usage_pb2
from absl.testing import absltest
from absl.testing import parameterized

_EXPECTED_TF_CONFIG = """provider "custom-google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_subscription.pubsub  __project__/my-pubsub-subscription
resource "google_pubsub_subscription" "pubsub" {
  provider = custom-google-beta

  name = "my-pubsub-subscription"
  topic = "my-pubsub-topic"
  message_retention_duration = "1200s"
  retain_acked_messages = true
  ack_deadline_seconds = 60
  expiration_policy {
    ttl = "86400s"
  }
}
"""

_EXPECTED_TF_CONFIG_PROCESSED = """provider "custom-google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_subscription._123pubsub  __project__/my-pubsub-subscription
resource "google_pubsub_subscription" "_123pubsub" {
  provider = custom-google-beta

  name = "my-pubsub-subscription"
  topic = "my-pubsub-topic"
  message_retention_duration = "1200s"
  retain_acked_messages = true
  ack_deadline_seconds = 60
  expiration_policy {
    ttl = "86400s"
  }
}
"""


class TfConverterTest(parameterized.TestCase, absltest.TestCase):
  _PROVIDER_VALUE = 'custom-google-beta'

  dm_resources = [{
      'name': 'pubsub',
      'properties': {
          'topic': 'my-pubsub-topic',
          'subscription': 'my-pubsub-subscription',
          'messageRetentionDuration': '1200s',
          'retainAckedMessages': True,
          'ackDeadlineSeconds': 60,
          'expirationPolicy': {'ttl': '86400s'},
      },
      'type': 'gcp-types/pubsub-v1:projects.subscriptions',
  }]

  dm_resource_with_deps_template = {
      'name': 'resource_name',
      'properties': {},
      'type': 'a_type',
  }

  def setUp(self):
    super().setUp()
    templates_dir = resource_reader.get_templates_dir('tf')
    self.converter = tf_converter.TerraformConverter(
        templates_dir=templates_dir,
        template_resolver=template_resolver.get_instance('tf', templates_dir),
        provider=self._PROVIDER_VALUE,
    )
    self._templates_map = {
        'gcp-types/pubsub-v1:projects.subscriptions': (
            'google_pubsub_subscription'
        ),
        'gcp-types/pubsub-v1:projects.topics': 'google_pubsub_topic',
        'gcp-types/compute-v1:networks': 'google_compute_network',
        'gcp-types/cloudkms-v1:projects.locations.keyRings': (
            'google_kms_key_ring'
        ),
        'gcp-types/cloudkms-v1:projects.locations.keyRings.cryptoKeys': (
            'google_kms_crypto_key'
        ),
        'gcp-types/storage-v1:storage.buckets.insert': 'google_storage_bucket',
    }

  def test_both_type_and_action_specified_should_raise_unsupported_type_error(
      self,
  ):
    resource = {
        'name': 'some-resource-name',
        'type': 'gcp-types/pubsub-v1:projects.subscriptions',
        'action': 'gcp-types/storage-v1:storage.buckets.insert',
    }
    with self.assertRaisesRegex(
        errors.UnsupportedResourceTypeError,
        'either a type or an action, but not both',
    ):
      self.converter.convert([resource], '')

  def test_convert_success(self):
    resource = {
        'name': 'pubsub',
        'properties': {
            'topic': 'my-pubsub-topic',
            'subscription': 'my-pubsub-subscription',
            'messageRetentionDuration': '1200s',
            'retainAckedMessages': True,
            'ackDeadlineSeconds': 60,
            'expirationPolicy': {'ttl': '86400s'},
        },
        'type': 'gcp-types/pubsub-v1:projects.subscriptions',
    }
    actual = self.converter.convert([resource], '')
    self.assertEqual(actual, _EXPECTED_TF_CONFIG)

  def test_convert_success_preprocess_tf_name(self):
    resource = {
        'name': '123pubsub',
        'properties': {
            'topic': 'my-pubsub-topic',
            'subscription': 'my-pubsub-subscription',
            'messageRetentionDuration': '1200s',
            'retainAckedMessages': True,
            'ackDeadlineSeconds': 60,
            'expirationPolicy': {'ttl': '86400s'},
        },
        'type': 'gcp-types/pubsub-v1:projects.subscriptions',
    }
    actual = self.converter.convert([resource], '')
    self.assertEqual(actual, _EXPECTED_TF_CONFIG_PROCESSED)

  def test_ref_hydration(self):
    dm_ref_resource = [{
        'name': 'sample-project',
        'properties': {
            'name': 'sample-project',
            'parent': {
                'id': '123',
                'type': 'folder',
            },
            'projectId': 'sample-project',
        },
        'type': 'gcp-types/cloudresourcemanager-v1:projects',
    }]

    dm_ref = '$(ref.sample-project.projectId)'
    actual = tf_converter.hydrate_ref_field(dm_ref, dm_ref_resource, None)
    self.assertEqual(actual, 'sample-project')

    dm_ref = '$(ref.sample-project.parent.type)'
    actual = tf_converter.hydrate_ref_field(dm_ref, dm_ref_resource, None)
    self.assertEqual(actual, 'folder')

    dm_ref = '$(ref.sample-project.name)'
    actual = tf_converter.hydrate_ref_field(dm_ref, dm_ref_resource, None)
    self.assertEqual(actual, 'sample-project')

  def test_ref_hydration_with_arg_project_id(self):
    dm_ref_resource = [{
        'name': 'does-not-matter',
        'properties': {
            'projectId': 'can-be-whatever',
        },
    }]

    dm_ref = '$(ref.does-not-matter.projectId)'
    actual = tf_converter.hydrate_ref_field(
        dm_ref, dm_ref_resource, 'test_project_id'
    )
    self.assertEqual(actual, 'test_project_id')

  def test_ref_hydration_for_another_field_with_arg_project_id(self):
    dm_ref_resource = [{
        'name': 'sample-project',
        'properties': {
            'name': 'sample-project',
            'parent': {
                'id': '123',
                'type': 'folder',
            },
            'projectId': 'sample-project',
        },
        'type': 'gcp-types/cloudresourcemanager-v1:projects',
    }]

    dm_ref = '$(ref.sample-project.parent.type)'
    actual = tf_converter.hydrate_ref_field(
        dm_ref, dm_ref_resource, 'test_project_id'
    )
    self.assertEqual(actual, 'folder')

  def test_reference_filter_success(self):
    dm_resources = [
        {
            'name': 'pubsub-topic',
            'properties': {'name': 'pubsub-topic', 'topic': 'event-topic'},
            'type': 'gcp-types/pubsub-v1:projects.topics',
        },
        {
            'metadata': {'dependsOn': ['pubsub-topic']},
            'name': 'pubsub-subscription',
            'properties': {
                'name': 'pubsub-subscription',
                'subscription': 'pubsub-subscription',
                'topic': '$(ref.pubsub-topic.name)',
            },
            'type': 'gcp-types/pubsub-v1:projects.subscriptions',
        },
    ]

    dm_reference = '$(ref.pubsub-topic.name)'
    actual = tf_converter.make_reference(
        dm_reference, dm_resources, self.converter.template_resolver
    )
    self.assertEqual(actual, 'google_pubsub_topic.pubsub_topic.name')

    dm_reference = '$(ref.pubsub-topic.selfLink)'
    actual_reference = tf_converter.make_reference(
        dm_reference, dm_resources, self.converter.template_resolver
    )
    self.assertEqual(actual_reference, 'google_pubsub_topic.pubsub_topic.id')

  def test_reference_with_overwritten_field_name(self):
    dm_resources = [
        {
            'name': 'kms-keyring',
            'properties': {
                'keyRingId': 'kms-keyring',
                'parent': 'projects/tjr-dm-test-1/locations/us-central1',
            },
            'type': 'gcp-types/cloudkms-v1:projects.locations.keyRings',
        },
        {
            'metadata': {'dependsOn': ['kms-keyring']},
            'name': 'kms-cryptokey',
            'properties': {
                'cryptoKeyId': 'kms-cryptokey',
                'parent': '$(ref.kms-keyring.name)',
            },
            'type': (
                'gcp-types/cloudkms-v1:projects.locations.keyRings.cryptoKeys'
            ),
        },
    ]

    dm_reference = '$(ref.kms-keyring.name)'
    actual_reference = tf_converter.make_reference(
        dm_reference, dm_resources, self.converter.template_resolver
    )
    self.assertEqual(actual_reference, 'google_kms_key_ring.kms_keyring.id')

  def test_reference_filter_return_non_str_value(self):
    actual = tf_converter.make_reference(True, None, None)
    self.assertTrue(actual)

  def test_make_dependencies_with_deps(self):
    dm_resource_with_deps = {'metadata': {'dependsOn': ['pubsub']}}
    dm_resource_with_deps.update(self.dm_resource_with_deps_template)
    actual_deps = tf_converter.make_dependencies(
        dm_resource_with_deps,
        self.dm_resources,
        self.converter.template_resolver,
    )
    self.assertListEqual(['google_pubsub_subscription.pubsub'], actual_deps)

  def test_make_dependencies_no_deps(self):
    dm_resource_with_deps = self.dm_resource_with_deps_template
    actual_deps = tf_converter.make_dependencies(
        dm_resource_with_deps,
        self.dm_resources,
        self.converter.template_resolver,
    )
    self.assertEmpty(actual_deps)

  @parameterized.parameters(
      ('bigquery.dataset', 'bigquery_dataset'),
      ('123bigquery.dataset', '_123bigquery_dataset'),
      ('bigquery.dataset123', 'bigquery_dataset123'),
      ('!foo', '_foo'),
      ('!foo-bar', '_foo_bar'),
  )
  def test_normalize_resource_name(self, name: str, expected: str):
    self.assertEqual(tf_converter.normalize_resource_name(name), expected)

  def test_pre_process_target_pool_logic(self):
    dm_resources = [
        {
            'metadata': {
                'dependsOn': ['compute-instance-1', 'compute-instance-2']
            },
            'name': 'target_pool',
            'properties': {
                'region': 'us-west1',
                'instances': [
                    '$(ref.compute-instance-1.selfLink)',
                    '$(ref.compute-instance-2.selfLink)',
                    'https://www.googleapis.com/compute/v1/projects/PROJECT_ID/zones/asia-east1-a/instances/compute-instance-3',
                ],
            },
            'type': 'gcp-types/compute-v1:targetPools',
        },
        {
            'name': 'compute-instance-1',
            'properties': {
                'zone': 'us-west1-a',
            },
            'type': 'gcp-types/compute-v1:instances',
        },
        {
            'name': 'compute-instance-2',
            'properties': {
                'zone': 'us-central1-a',
            },
            'type': 'gcp-types/compute-v1:instances',
        },
    ]

    tf_converter._pre_process_target_pool(dm_resources[0], dm_resources)

    target_pool_instances = dm_resources[0]['properties']['instances']

    self.assertEqual('us-west1-a/compute-instance-1', target_pool_instances[0])
    self.assertEqual(
        'us-central1-a/compute-instance-2', target_pool_instances[1]
    )
    self.assertEqual(
        'https://www.googleapis.com/compute/v1/projects/PROJECT_ID/zones/asia-east1-a/instances/compute-instance-3',
        target_pool_instances[2],
    )

  def test_pre_process_action_add_instance(self):
    foo_instance = 'https://compute.googleapis.com/compute/v1/projects/PROJECT_ID/zones/asia-east1-a/instances/foo'
    bar_instance = 'https://compute.googleapis.com/compute/v1/projects/PROJECT_ID/zones/asia-east1-a/instances/bar'
    dm_resources = [
        {
            'name': 'instancegroup',
            'properties': {
                'zone': 'us-central1-f',
            },
            'type': 'compute.v1.instanceGroup',
        },
        {
            'action': (
                'gcp-types/compute-v1:compute.instanceGroups.addInstances'
            ),
            'name': 'action-addinstances',
            'properties': {
                'instanceGroup': 'instancegroup',
                'instances': [
                    {'instance': foo_instance},
                    {'instance': bar_instance},
                ],
                'zone': 'us-central1-f',
            },
        },
    ]

    action_instance = dm_resources[1]
    instance_group_instance = dm_resources[0]

    tf_converter._pre_process_action_add_instance(action_instance, dm_resources)

    self.assertEqual(
        [foo_instance, bar_instance],
        instance_group_instance['properties']['instances'],
    )

  def test_if_null_filter(self):
    value = tf_converter.filter_if_null(
        'name',
        ({'value': 'value-1'}, None, {'name': 'value-1'}, {'name': 'invalid'}),
    )

    self.assertEqual('value-1', value)

  def test_provider_value(self):
    self.assertEqual(
        self.converter.jinja_env.globals['get_tf_provider'],
        self._PROVIDER_VALUE,
    )

  def test_match_missing_fields(self):
    resource = {
        'name': 'resource-name',
        'properties': {
            'prop1': 'value1',
            'prop2': {'subprop1': 'subvalue1', 'subprop2': 'subvalue2'},
        },
    }
    missing_fields = [
        'properties.prop1',
        'properties.prop2.subprop2',
        'properties.prop3',
    ]
    tf_converter.global_unsupported_fields_map = {}
    with self.assertLogs(level='WARNING') as log_output:
      logging.set_verbosity(logging.WARNING)
      tf_converter.match_missing_fields(
          resource, missing_fields, tf_converter.global_unsupported_fields_map
      )
      expected_log_message_1 = (
          'Field properties.prop1 is unsupported in conversion for resource'
          ' resource-name. Value: value1'
      )
      expected_log_message_2 = (
          'Field properties.prop2.subprop2 is unsupported in conversion for'
          ' resource resource-name. Value: subvalue2'
      )
      self.assertTrue(re.search
                      (expected_log_message_1, log_output[0][0].message))
      self.assertTrue(re.search
                      (expected_log_message_2, log_output[0][1].message))

    self.assertEqual(
        tf_converter.global_unsupported_fields_map,
        {
            'resource-name': [
                {'properties.prop1': 'value1'},
                {'properties.prop2.subprop2': 'subvalue2'},
            ]
        },
    )

    tf_converter.global_unsupported_fields_map = {'resource-name': []}
    tf_converter.match_missing_fields(
        resource, missing_fields, tf_converter.global_unsupported_fields_map
    )
    self.assertEqual(
        tf_converter.global_unsupported_fields_map,
        {
            'resource-name': [
                {'properties.prop1': 'value1'},
                {'properties.prop2.subprop2': 'subvalue2'},
            ]
        },
    )

  def test_get_field_value(self):
    value = {
        'prop1': 'value1',
        'prop2': {
            'subprop1': 'subvalue1',
            'subprop2': 'subvalue2',
            'subprop3': [{'item1': 'item1value', 'item2': 'item2value'}],
        },
    }
    self.assertEqual(
        tf_converter._get_field_value(value, ['prop1']), 'value1'
    )
    self.assertEqual(
        tf_converter._get_field_value(value, ['prop2', 'subprop1']),
        'subvalue1',
    )
    self.assertEqual(
        tf_converter._get_field_value(value, ['prop2', 'subprop2']),
        'subvalue2',
    )
    self.assertEqual(
        tf_converter._get_field_value(
            value, ['prop2', 'subprop3', 'item1']
        ),
        ['item1value'],
    )
    self.assertEqual(
        tf_converter._get_field_value(
            value, ['prop2', 'subprop3', 'item2']
        ),
        ['item2value'],
    )
    self.assertIsNone(
        tf_converter._get_field_value(value, ['prop3'])
    )
    self.assertIsNone(
        tf_converter._get_field_value(value, ['prop2', 'subprop4'])
    )

  def test_compute_instance_empty_service_account(self):
    resource = {
        'name': 'test-instance',
        'properties': {
            'zone': 'us-central1-a',
            'machineType': 'n1-standard-1',
            'disks': [{
                'boot': True,
                'initializeParams': {
                    'sourceImage': 'debian-cloud/debian-9'
                }
            }],
            'networkInterfaces': [{
                'network': 'default'
            }],
            'serviceAccounts': []
        },
        'type': 'compute.v1.instance'
    }
    actual = self.converter.convert([resource], '')
    self.assertNotIn('service_account', actual)


class TfConverterTemplateTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    templates_dir = resource_reader.get_templates_dir('tf')
    self.testdata_dir = resource_reader.get_testdata_dir()
    self.layout_path = self.testdata_dir / pathlib.Path(
        'property_parser_test/variables_test/layout_file.yaml'
    )
    output_dir = self.create_tempdir('output_dir')
    self.tf_import_file_path = pathlib.Path(
        output_dir.create_file('output_import_file').full_path
    )
    self.converter = tf_converter.TerraformConverter(
        templates_dir=templates_dir,
        template_resolver=template_resolver.get_instance('tf', templates_dir),
        layout_file=self.layout_path,
        tf_import_file=self.tf_import_file_path,
        provider='google-beta',
        project_id='some-project',
    )
    self.config_path = resource_reader.get_testdata_dir() / pathlib.Path(
        'property_parser_test/variables_test/config_file.yaml'
    )
    self.config = None
    with open(self.config_path, 'r') as opened_config_file:
      self.config = yaml.safe_load(opened_config_file.read())
    opened_config_file.close()

  def test_template_conversion_with_unsupported_fields(self):
    self.converter.convert(self.config['resources'], namespace='')
    template_directory = self.tf_import_file_path.parent / 'template_conversion'
    module_directory = template_directory / 'modules'
    with open(
        self.testdata_dir
        / pathlib.Path(
            'property_parser_test/variables_test/vm_template/variables.tf'
        ),
        'r',
    ) as actual_file:
      actual = actual_file.read()
    actual_file.close()
    with open(module_directory / 'vm_template/variables.tf', 'r') as file:
      self.assertEqual(actual, file.read())

    with open(
        self.testdata_dir
        / pathlib.Path(
            'property_parser_test/variables_test/network_template/outputs.tf'
        ),
        'r',
    ) as actual_file:
      actual = actual_file.read()
    with open(module_directory / 'network_template/outputs.tf', 'r') as file:
      self.assertEqual(actual, file.read())

    # Calling convert again to validate that the unsupported_map is cleared.
    self.converter.convert(self.config['resources'], namespace='')
    with open(module_directory / 'network_template/outputs.tf', 'r') as file:
      self.assertEqual(actual, file.read())
    self.assertEmpty(self.converter.unsupported_fields_map)

  def test_template_conversion_imports(self):
    self.converter.convert(self.config['resources'], namespace='')
    template_directory = self.tf_import_file_path.parent / 'template_conversion'
    with open(self.testdata_dir / 'module_test/imports_test1.txt', 'r') as file:
      actual = file.read()

    with open(template_directory / 'imports.txt', 'r') as import_file:
      self.assertEqual(actual, import_file.read())

    self.converter.layout_parser.template['vm-3'] = 'main'
    with open(self.testdata_dir / 'module_test/imports_test2.txt', 'r') as file:
      actual = file.read()

    self.assertEqual(
        actual,
        self.converter.get_module_import_statements(
            self.testdata_dir / 'module_test/imports_input.txt',
            self.converter.layout_parser,
        ),
    )

  def test_template_conversion_warnings(self):
    with self.assertLogs(level='WARNING') as log_output:
      logging.set_verbosity(logging.WARNING)
      expected_log_message = (
          'Template conversion requires all resources to be supported'
      )
      self.converter.convert(self.config['unsupported_resource'], namespace='')
      self.assertTrue(re.search(expected_log_message, log_output[0][0].message))
    with self.assertLogs(level='WARNING') as log_output:
      logging.set_verbosity(logging.WARNING)
      expected_log_message = 'Template Conversion requires tf import file'
      self.converter.tf_import_file = None
      self.converter.convert(self.config['unsupported_resource'], namespace='')
      self.assertTrue(re.search(expected_log_message, log_output[0][0].message))


class TfConverterTemplateTestWithoutDeployment(absltest.TestCase):

  def setUp(self):
    super().setUp()
    templates_dir = resource_reader.get_templates_dir('tf')
    self.testdata_dir = resource_reader.get_testdata_dir()
    self.layout_path = self.testdata_dir / pathlib.Path(
        'property_parser_test/variables_test/layout_file.yaml'
    )
    output_dir = self.create_tempdir('output_dir')
    self.tf_import_file_path = pathlib.Path(
        output_dir.create_file('output_import_file').full_path
    )
    self.converter = tf_converter.TerraformConverter(
        templates_dir=templates_dir,
        template_resolver=template_resolver.get_instance('tf', templates_dir),
        layout_file=self.layout_path,
        tf_import_file=self.tf_import_file_path,
        provider='google-beta',
        project_id='some-project',
        without_deployment_flag=True,
    )
    self.config_path = resource_reader.get_testdata_dir() / pathlib.Path(
        'property_parser_test/variables_test/config_file.yaml'
    )
    self.config = None
    with open(self.config_path, 'r') as opened_config_file:
      self.config = yaml.safe_load(opened_config_file.read())

  def test_template_conversion(self):
    self.converter.convert(self.config['resources'], namespace='')
    template_directory = self.tf_import_file_path.parent / 'template_conversion'
    module_directory = template_directory / 'modules'
    with open(
        self.testdata_dir
        / pathlib.Path(
            'property_parser_test/variables_test/vm_template/variables.tf'
        ),
        'r',
    ) as actual_file:
      actual = actual_file.read()
    actual_file.close()
    with open(module_directory / 'vm_template/variables.tf', 'r') as file:
      self.assertEqual(actual, file.read())
    file.close()

    with open(
        self.testdata_dir
        / pathlib.Path(
            'property_parser_test/variables_test/network_template/outputs.tf'
        ),
        'r',
    ) as actual_file:
      actual = actual_file.read()
    actual_file.close()
    with open(module_directory / 'network_template/outputs.tf', 'r') as file:
      self.assertEqual(actual, file.read())
    file.close()

  def test_template_conversion_imports(self):
    self.converter.convert(self.config['resources'], namespace='')
    template_directory = self.tf_import_file_path.parent / 'template_conversion'
    with open(self.testdata_dir / 'module_test/imports_test1.txt', 'r') as file:
      actual = file.read()

    with open(template_directory / 'imports.txt', 'r') as import_file:
      self.assertEqual(actual, import_file.read())

    self.converter.layout_parser.template['vm-3'] = 'main'
    with open(self.testdata_dir / 'module_test/imports_test2.txt', 'r') as file:
      actual = file.read()

    self.assertEqual(
        actual,
        self.converter.get_module_import_statements(
            self.testdata_dir / 'module_test/imports_input.txt',
            self.converter.layout_parser,
        ),
    )

  def test_template_conversion_warnings(self):
    with self.assertLogs(level='WARNING') as log_output:
      logging.set_verbosity(logging.WARNING)
      expected_log_message = (
          'Template conversion requires all resources to be supported'
      )
      self.converter.convert(self.config['unsupported_resource'], namespace='')
      self.assertTrue(re.search(expected_log_message, log_output[0][0].message))
    with self.assertLogs(level='WARNING') as log_output:
      logging.set_verbosity(logging.WARNING)
      expected_log_message = 'Template Conversion requires tf import file'
      self.converter.tf_import_file = None
      self.converter.convert(self.config['unsupported_resource'], namespace='')
      self.assertTrue(re.search(expected_log_message, log_output[0][0].message))


class TfConverterExpectedErrorsTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.mock_logger = mock.patch.object(
        conversion_logger, 'log', return_value=None
    ).start()

    templates_dir = resource_reader.get_templates_dir('tf')
    self.template_resolver = template_resolver.get_instance('tf', templates_dir)

  def tearDown(self):
    super().tearDown()
    mock.patch.stopall()

  dm_resources = [
      {
          'name': 'pubsub-topic',
          'properties': {'name': 'pubsub-topic', 'topic': 'event-topic'},
          'type': 'gcp-types/pubsub-v1:projects.topics',
      },
      {
          'metadata': {'dependsOn': ['pubsub-topic']},
          'name': 'pubsub-subscription',
          'properties': {
              'name': 'pubsub-subscription',
              'subscription': 'pubsub-subscription',
              'topic': '$(ref.pubsub-topic.name)',
          },
          'type': 'gcp-types/pubsub-v1:projects.subscriptions',
      },
      {
          'name': 'pubsub-topic-invalid-missing-type',
          'properties': {'name': 'pubsub-topic', 'topic': 'event-topic'},
      },
  ]

  templates_map = {
      'gcp-types/pubsub-v1:projects.subscriptions': (
          'google_pubsub_subscription'
      ),
      'gcp-types/pubsub-v1:projects.topics': 'google_pubsub_topic',
      'gcp-types/compute-v1:networks': 'google_compute_network',
  }

  dm_resource_with_deps_template = {
      'name': 'resource_name',
      'properties': {},
      'type': 'a_type',
  }

  def test_referenced_resource_not_found(self):
    reference_to_notarget = '$(ref.pubsub-topic-notarget.name)'
    with self.assertRaises(errors.UnsupportedReferenceError):
      tf_converter.make_reference(
          reference_to_notarget, self.dm_resources, self.template_resolver
      )

    logged_usage = self.mock_logger.call_args[0]
    actual_result = logged_usage[0].conversion_result

    self.assertIsNotNone(actual_result)
    self.assertEqual(
        actual_result.status, convert_usage_pb2.ConversionResult.Status.FAILURE
    )
    self.assertEqual(
        actual_result.conversion_message[0].error_code,
        convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_UNSUPPORTED_REFERENCE,
    )

  def test_unsupported_dependencies(self):
    depended_resource_name = 'pubsub-not-exist'
    dm_resource_with_deps = {
        'metadata': {'dependsOn': [depended_resource_name]}
    }
    dm_resource_with_deps.update(self.dm_resource_with_deps_template)
    expected_error_msg = (
        f'Cannot resolve dependency - {depended_resource_name!r}.'
    )
    with self.assertRaisesWithLiteralMatch(
        errors.UnsupportedDependencyError, expected_error_msg
    ):
      tf_converter.make_dependencies(
          dm_resource_with_deps, self.dm_resources, self.template_resolver
      )

    logged_usage = self.mock_logger.call_args[0]
    actual_result = logged_usage[0].conversion_result
    self.assertIsNotNone(actual_result)
    self.assertEqual(
        actual_result.status, convert_usage_pb2.ConversionResult.Status.FAILURE
    )
    self.assertEqual(
        actual_result.conversion_message[0].error_code,
        convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_UNSUPPORTED_DEPENDENCY,
    )


if __name__ == '__main__':
  absltest.main()
