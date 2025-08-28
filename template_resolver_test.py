from absl.testing import absltest

import conversion_logger_setting
import errors
import resource_reader
import template_resolver
from absl.testing import absltest
from absl.testing import parameterized


class BaseTemplateResolverTest(parameterized.TestCase, absltest.TestCase):

  @parameterized.named_parameters(
      {
          'testcase_name': 'krm_instance',
          'resolve_target': 'krm',
          'expected_type': template_resolver.KrmTemplateResolver
      }, {
          'testcase_name': 'terraform_instance',
          'resolve_target': 'tf',
          'expected_type': template_resolver.TerraformTemplateResolver
      }, {
          'testcase_name': 'action_instance',
          'resolve_target': 'actions',
          'expected_type': template_resolver.ActionTemplateResolver
      })
  def test_should_return_requested_instance(self, resolve_target: str,
                                            expected_type):
    templates_dir = resource_reader.get_templates_dir(resolve_target)
    result = template_resolver.get_instance(resolve_target, templates_dir)
    self.assertIsNotNone(result)
    self.assertIsInstance(result, expected_type)

  def test_should_raise_on_invalid_input(self):
    templates_dir = resource_reader.get_templates_dir('tf')
    with self.assertRaises(errors.InvalidTemplateResolverTypeError):
      template_resolver.get_instance('invalid', templates_dir)


class TerraformTemplateResolverTest(absltest.TestCase):

  def setUp(self):
    super().setUp()

    self.templates = {
        'compute.v1.networks':
            'google_compute_network',
        'compute.v1.regionDisk':
            'google_compute_disk',
        'gcp-types/logging-v2':
            'google_logging_metric',
        'compute.v1.globalForwardingRule':
            'google_compute_global_forwarding_rule'
    }

    self.template_resolver = template_resolver.TerraformTemplateResolver(
        templates=self.templates)

  def test_tf_get_mappings_should_include_overrides(self):
    overrides = self.template_resolver._override_rules.keys()
    expected = self.template_resolver.list_dm_types()
    for override in overrides:
      self.assertIn(override, expected)

  def test_tf_resolve(self):
    actual = self.template_resolver.resolve('compute.v1.globalForwardingRule',
                                            None)
    self.assertEqual(actual, 'google_compute_global_forwarding_rule')

  def test_tf_resolve_using_override_rule(self):
    resource = {'type': 'compute.v1.instance', 'properties': {}}
    actual = self.template_resolver.resolve(resource['type'], resource)
    self.assertEqual(actual, 'google_compute_instance')

  def test_tf_resolve_compute_instance_from_template(self):
    context = {
        'type': 'compute.v1.instance',
        'properties': {
            'sourceInstanceTemplate': 'test'
        }
    }
    actual = self.template_resolver.resolve(context['type'], context)
    self.assertEqual(actual, 'google_compute_instance_from_template')

  def test_tf_should_raise_with_invalid_context(self):
    with self.assertRaises(errors.TemplateResolverMissingContextError):
      self.template_resolver.resolve('compute.v1.instance', None)

  def test_tf_should_raise_with_duplicate_override_rule(self):
    with self.assertRaises(errors.AmbiguousOverrideRuleError):
      self.template_resolver.add_override_rule('compute.v1.instance', 'a' + 'b')

  def test_should_raise_on_invalid_override_rule(self):
    with self.assertRaises(errors.InvalidOverrideRuleError):
      self.template_resolver.add_override_rule(None, 'a' + 'b')
    with self.assertRaises(errors.InvalidOverrideRuleError):
      self.template_resolver.add_override_rule('rule_1', None)


class KrmTemplateResolverTest(absltest.TestCase):

  def setUp(self):
    super().setUp()

    self.templates = {
        'compute.v1.instance': 'compute_instance',
        'compute.v1.networks': 'compute_network',
        'compute.v1.regionDisk': 'compute_disk'
    }

    self.template_resolver = template_resolver.KrmTemplateResolver(
        templates=self.templates)

  def test_krm_list_dm_types(self):
    actual = sorted(self.template_resolver.list_dm_types())
    expected = sorted(self.templates.keys())
    self.assertEqual(actual, expected)

  def test_krm_resolve(self):
    actual = self.template_resolver.resolve('compute.v1.instance', 'a' + 'b')
    self.assertEqual(actual, 'compute_instance')

  def test_should_raise_on_invalid_override_rule(self):
    with self.assertRaises(errors.InvalidOverrideRuleError):
      self.template_resolver.add_override_rule(None, 'a' + 'b')
    with self.assertRaises(errors.InvalidOverrideRuleError):
      self.template_resolver.add_override_rule('rule_1', None)


class ActionsTemplateResolverTest(absltest.TestCase):

  def setUp(self):
    super().setUp()

    self.templates = {
        'gcp-types/pubsub-v1:pubsub.projects.topics.create': 'pubsub-v1_topics',
        'gcp-types/storage-v1:storage.buckets.insert': 'storage-v1_buckets',
        'gcp-types/dns-v1:dns.changes.create': 'dns-v1_resourceRecordSets'
    }

    self.template_resolver = template_resolver.ActionTemplateResolver(
        templates=self.templates)

    self._ignored_type = 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy'

    conversion_logger_setting.init('test_run_id', None, 'dev')

  def test_actions_list_dm_types(self):
    actual = sorted(self.template_resolver.list_dm_types())
    expected = sorted(self.templates.keys())
    self.assertEqual(actual, expected)

  def test_actions_resolve(self):
    actual = self.template_resolver.resolve(
        'gcp-types/dns-v1:dns.changes.create', None)
    self.assertEqual(actual, 'dns-v1_resourceRecordSets')

  def test_actions_verify_is_ignored(self):
    actual = self.template_resolver.is_ignored(self._ignored_type)
    self.assertTrue(actual)

  def test_actions_verify_is_supported(self):
    actual = self.template_resolver.is_supported(self._ignored_type)
    self.assertFalse(actual)

  def test_tf_should_raise_with_ignored_type(self):
    actual = self.template_resolver.resolve(self._ignored_type, None)
    self.assertEqual(actual, 'unsupported_resource')


if __name__ == '__main__':
  absltest.main()
