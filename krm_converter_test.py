from unittest import mock

import jinja2
import yaml

import conversion_logger
import errors
import krm_converter
import resource_reader
import template_resolver
import convert_usage_pb2
from absl.testing import absltest


_EXPECTED_KRM_CONFIG = """apiVersion: bigquery.cnrm.cloud.google.com/v1beta1
kind: BigQueryDataset
metadata:
  name: bigquerydataset
spec:
  access:
  - role: OWNER
    userByEmail: user@example.com
  defaultTableExpirationMs: 3600000
  location: us-west1
  resourceID: bigquerydataset
"""


class KrmConverterFuncTest(absltest.TestCase):

  def test_typed_reference_groups(self):
    ref = '$(ref.foo.bar.tar)'
    groups = krm_converter.typed_reference_groups(ref)
    self.assertDictEqual(groups, {'name': 'foo', 'path': 'bar.tar'})


class KrmConverterTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    templates_dir = resource_reader.get_templates_dir('krm')
    self.converter = krm_converter.KrmConverter(
        templates_dir=templates_dir,
        template_resolver=template_resolver.get_instance('krm', templates_dir),
    )
    self.mock_logger = mock.patch.object(
        conversion_logger, 'log', return_value=None
    ).start()

  def tearDown(self):
    super().tearDown()
    mock.patch.stopall()

  def test_template_filters_have_keys(self):
    env_templates_filters = self.converter.jinja_env.filters
    expected_template_filters = [
        'dump_json',
        'enumerate',
        'set_difference',
        'set_intersection',
        'typed_reference',
        'arbitrary_reference',
        'reference_type',
        'missing_fields',
    ]
    for expected in expected_template_filters:
      self.assertIn(expected, env_templates_filters)

  def test_both_type_and_action_specified_should_raise_unsupported_type_error(
      self,
  ):
    resource = {
        'type': 'gcp-types/accesscontextmanager-v1:accessPolicies',
        'action': 'gcp-types/accesscontextmanager-v1:accessPolicies',
    }
    with self.assertRaisesRegex(
        errors.UnsupportedResourceTypeError,
        'either a type or an action, but not both',
    ):
      self.converter.convert_resource(resource, None, 'krm')

  def test_get_unsupported_template(self):
    resource = {'type': 'Fake'}

    with self.assertRaisesRegex(
        errors.UnsupportedResourceTypeError, 'not supported'
    ):
      self.converter.convert_resource(resource, None, 'krm')

  def test_convert_failure_no_jinja_template(self):
    resource = {'type': 'gcp-types/accesscontextmanager-v1:accessPolicies'}
    with self.assertRaises(jinja2.exceptions.TemplateNotFound):
      self.converter.convert([resource], '')

  def test_action_specified_should_raise_contains_action_error(self):
    resource = {'action': 'gcp-types/accesscontextmanager-v1:accessPolicies'}
    self.assertRaises(
        errors.ContainsActionError, self.converter.convert, [resource], ''
    )
    logged_usage = self.mock_logger.call_args[0]
    actual_result = logged_usage[0].conversion_result

    self.assertIsNotNone(actual_result)
    self.assertEqual(
        actual_result.status, convert_usage_pb2.ConversionResult.Status.FAILURE
    )
    self.assertEqual(
        actual_result.conversion_message[0].error_code,
        convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_CONTAINS_ACTION,
    )
    self.assertEqual(
        actual_result.conversion_message[0].action_name,
        'gcp-types/accesscontextmanager-v1:accessPolicies',
    )

  def test_convert_success(self):
    resource = {
        'name': 'bigquerydataset',
        'properties': {
            'access': [{'role': 'OWNER', 'userByEmail': 'user@example.com'}],
            'datasetReference': {
                'datasetId': 'bigquerydataset',
                'projectId': 'tjr-dm-test-1',
            },
            'defaultTableExpirationMs': 3600000,
            'location': 'us-west1',
        },
        'type': 'gcp-types/bigquery-v2:datasets',
    }
    expected = _EXPECTED_KRM_CONFIG
    actual = self.converter.convert([resource], '')
    self.assertEqual(yaml.safe_load(actual), yaml.safe_load(expected))

  def test_unsupported_reference_error(self):
    resources = [
        {
            'name': 'myvm1-resource-name',
            'properties': {
                'disks': [{
                    'autoDelete': False,
                    'boot': True,
                    'deviceName': 'boot-disk',
                    'interface': 'SCSI',
                    'mode': 'READ_WRITE',
                    'source': '$(ref.boot-disk-vm1-resource-name.selfLink)',
                    'type': 'PERSISTENT',
                }],
                'machineType': (
                    'zones/europe-west2-b/machineTypes/n1-standard-8'
                ),
                'name': 'myvm1-deployment-name',
                'networkInterfaces': [{
                    'networkIP': '$(ref.compute-address-resource-name.address)',
                    'subnetwork': (
                        'projects/dm-convert-test/'
                        'regions/europe-west2/subnetworks/default'
                    ),
                }],
                'zone': 'europe-west2-b',
            },
            'type': 'compute.v1.instance',
        },
        {
            'name': 'boot-disk-vm1-resource-name',
            'properties': {
                'name': 'vm1-boot-disk-deployment-name',
                'sizeGb': '10',
                'sourceImage': (
                    'https://www.googleapis.com/compute/v1/projects'
                    '/debian-cloud/global/images/family/debian-10'
                ),
                'type': (
                    'projects/dm-convert-test/zones/'
                    'europe-west2-b/diskTypes/pd-ssd'
                ),
                'zone': 'europe-west2-b',
            },
            'type': 'compute.v1.disk',
        },
        {
            'name': 'compute-address-resource-name',
            'properties': {
                'addressType': 'INTERNAL',
                'name': 'compute-address-deployment-name',
                'purpose': 'GCE_ENDPOINT',
                'region': 'europe-west2',
                'subnetwork': (
                    'projects/dm-convert-test/regions'
                    '/europe-west2/subnetworks/default'
                ),
            },
            'type': 'compute.v1.address',
        },
    ]
    self.assertRaises(
        errors.UnsupportedReferenceError, self.converter.convert, resources, ''
    )

  def test_multiline_string(self):
    cert_value = (
        '-----BEGIN CERTIFICATE-----\n'
        'MIIDJTCCAg0CFHdD3ZGYMCmF3O4PvMwsP5i8d/V0MA'
        '0GCSqGSIb3DQEBCwUAME8x'
        '\n-----END CERTIFICATE-----'
    )
    resource = {
        'name': 'compute-sslcertificate',
        'properties': {'certificate': cert_value},
        'type': 'gcp-types/compute-v1:sslCertificates',
    }
    actual = self.converter.convert([resource], '')
    obj = yaml.safe_load(actual)
    self.assertIn('\n', obj['spec']['certificate']['value'])


class KRMConverterExpectedErrorsTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.mock_logger = mock.patch.object(
        conversion_logger, 'log', return_value=None
    ).start()

  def tearDown(self):
    super().tearDown()
    mock.patch.stopall()

  resources = [
      {
          'name': 'pubsub-topic',
          'properties': {
              'name': 'pubsub-topic',
              'topic': 'event-topic',
              'unsupported_field': 'field-value',
          },
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
          'name': 'pubsub-action',
          'properties': {
              'name': 'pubsub-action',
          },
          'action': 'gcp-types/pubsub-v1:projects.topics.get',
      },
  ]

  templates_map = {
      'gcp-types/pubsub-v1:projects.subscriptions': (
          'google_pubsub_subscription'
      ),
      'gcp-types/pubsub-v1:projects.topics': 'google_pubsub_topic',
  }

  def test_referenced_resource_not_found(self):
    referenced_resource_not_exist = '$(ref.pubsub-topic-notexist.name)'
    with self.assertRaises(errors.UnsupportedReferenceError):
      krm_converter.resolve_typed_reference(
          referenced_resource_not_exist, self.resources
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

  def test_referenced_property_not_defined(self):
    referenced_property_not_defined = '$(ref.pubsub-topic.property_not_defined)'
    with self.assertRaises(errors.UnsupportedReferenceError):
      krm_converter.resolve_arbitrary_reference(
          referenced_property_not_defined, self.resources
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

  def test_reference_to_action(self):
    reference_to_action = '$(ref.pubsub-action.name)'
    with self.assertRaises(errors.UnsupportedReferenceError):
      krm_converter.get_reference_type(reference_to_action, self.resources)

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

  def test_missing_fields(self):
    paths = ['unsupported_field']
    with self.assertRaises(errors.UnconvertableFieldError):
      krm_converter.missing_fields(
          self.resources[0].get('properties'), paths, False
      )

    logged_usage = self.mock_logger.call_args[0]
    actual_result = logged_usage[0].conversion_result

    self.assertIsNotNone(actual_result)
    self.assertEqual(
        actual_result.status, convert_usage_pb2.ConversionResult.Status.FAILURE
    )
    self.assertEqual(
        actual_result.conversion_message[0].error_code,
        convert_usage_pb2.ConversionMessage.ErrorCode.USER_ERROR_UNCONVERTIBLE_PROPERTY,
    )


if __name__ == '__main__':
  absltest.main()
