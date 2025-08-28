import pathlib
import shutil

import yaml

import dm_action_converter
import errors
import resource_reader
import template_resolver
from absl.testing import absltest
from absl.testing import parameterized

DEFAULT_TEMPLATE = """{%- import 'action_macros.jinja' as macros %}
{%- set properties = resource.get('properties', {}) -%}
- name: {{ resource.get('name') }}
  type: dest_type
  properties:
  {{- macros.fields(properties, {
  'field1': 'field1',
  'field2': 'field2',
  'field3': 'field3',
  }, ' ' * 4) -}}
        """

TEMPLATE_RENAMING_KEYS = """{%- import 'action_macros.jinja' as macros %}
{%- set properties = resource.get('properties', {}) -%}
- name: {{ resource.get('name') }}
  type: dest_type
  properties:
  {{- macros.fields(properties, {
    'field1': 'field1-new-name',
    'field2': 'field2-new-name',
    'field3': 'field3-new-name',
    'list-name': {
      'list_name': 'list-name-new-name',
      'list-item': 'list-item-new-name'
    },
    'map-name': {
      'map_name': 'map-name-new-name',
      'map-field1': 'map-field1-new-name',
      'map-field2': 'map-field2-new-name',
      'map-field3': 'map-field3-new-name'
    }
  }, ' ' * 4) -}}
        """
TEMPLATE_WITH_ONLY_TOP_LEVEL_MAPPINGS = """{%- import 'action_macros.jinja' as macros %}
{%- set properties = resource.get('properties', {}) -%}
- name: {{ resource.get('name') }}
  type: dest_type
  properties:
  {{- macros.fields(properties, {
    'field1': 'field1',
    'field2': 'field2',
    'field3': 'field3',
    'list-name': 'list-name',
    'map-name': 'map-name'
  }, ' ' * 4) -}}
        """

DEFAULT_ACTION = {
    'name': 'test-resource',
    'action': 'gcp-types/test:dm.action',
    'properties': {
        'field1': 'field1-val',
        'field2': 1234,
        'field3': True,
    }
}

ACTION_CONTAINING_UNMAPPED_FIELD = {
    'name': 'test-resource',
    'action': 'gcp-types/test:dm.action',
    'properties': {
        'field1': 'field1-val',
        'field2': 1234,
        'field3': True,
        'some-other-field': 'some-other-field-val',
    }
}

ACTION_WITH_LIST_AND_MAP = {
    'name': 'test-resource',
    'action': 'gcp-types/test:dm.action',
    'properties': {
        'field1': 'field1-val',
        'field2': 1234,
        'field3': True,
        'list-name': [{
            'list-item': 'list-item-val-1'
        }, {
            'list-item': 'list-item-val-2'
        }],
        'map-name': {
            'map-field1': 'map-field1',
            'map-field2': 5678,
            'map-field3': False,
        }
    }
}
DEFAULT_RESOURCE = {
    'name': 'test-resource',
    'type': 'dest_type',
    'properties': {
        'field1': 'field1-val',
        'field2': 1234,
        'field3': True
    }
}

RESOURCE_WITH_RENAMED_KEYS = {
    'name': 'test-resource',
    'type': 'dest_type',
    'properties': {
        'field1-new-name': 'field1-val',
        'field2-new-name': 1234,
        'field3-new-name': True,
        'list-name-new-name': [{
            'list-item-new-name': 'list-item-val-1'
        }, {
            'list-item-new-name': 'list-item-val-2'
        }],
        'map-name-new-name': {
            'map-field1-new-name': 'map-field1',
            'map-field2-new-name': 5678,
            'map-field3-new-name': False,
        }
    }
}

RESOURCE_WITH_LIST_AND_MAP = {
    'name': 'test-resource',
    'type': 'dest_type',
    'properties': {
        'field1': 'field1-val',
        'field2': 1234,
        'field3': True,
        'list-name': [{
            'list-item': 'list-item-val-1'
        }, {
            'list-item': 'list-item-val-2'
        }],
        'map-name': {
            'map-field1': 'map-field1',
            'map-field2': 5678,
            'map-field3': False,
        }
    }
}


class DmActionConverterTest(parameterized.TestCase, absltest.TestCase):

  def setUp(self):
    super().setUp()
    templates_dir = resource_reader.get_templates_dir('actions')
    self.converter = dm_action_converter.DmActionConverter(
        templates_dir=templates_dir,
        template_resolver=template_resolver.get_instance(
            'actions', templates_dir))

  def test_convert_success(self):
    resource = {
        'name': 'insert-new-bucket',
        'action': 'gcp-types/storage-v1:storage.buckets.insert',
        'properties': {
            'name': 'new-bucket',
            'project': 'test-project',
            'location': 'test-region',
            'labels': {
                'label-1': 'label-1-val',
                'label-2': 'label-2-val',
            },
            'iamConfiguration': {
                'uniformBucketLevelAccess': {
                    'enabled': True
                }
            },
            'encryption': {
                'defaultKmsKeyName': 'key-name'
            },
        }
    }
    unconvertible_actions, converted_resources = self.converter.convert(
        [resource], '')
    actual = yaml.safe_load(converted_resources)
    expected = resource.copy()
    # Name is moved from ['properties']['name'] to ['name'].
    del expected['properties']['name']
    expected['name'] = 'new-bucket'
    del expected['action']
    expected['type'] = 'gcp-types/storage-v1:buckets'

    self.assertEmpty(unconvertible_actions)
    self.assertLen(actual, 1)
    self.assertDictEqual(actual[0], expected)

  def test_unsupported_action_returns_as_unconvertible_action(self):
    resource = {
        'name': 'resource-name',
        'action': 'some-type-that-will-never-be-supported',
        'properties': {
            'foo': 'bar',
        }
    }

    unconvertible_actions, converted_resources = self.converter.convert(
        [resource], '')

    self.assertEqual(unconvertible_actions, [resource])
    self.assertEmpty(converted_resources)

  def test_convert_action_with_ref_success(self):
    resource = {
        'name': 'insert-new-bucket',
        'action': 'gcp-types/storage-v1:storage.buckets.insert',
        'properties': {
            'name': 'new-bucket',
            'project': '$(ref.some-project.name)',
            'location': 'test-region',
            'labels': {
                'label-1': 'label-1-val',
                'label-2': 'label-2-val',
            },
            'iamConfiguration': {
                'uniformBucketLevelAccess': {
                    'enabled': True
                }
            },
            'encryption': {
                'defaultKmsKeyName': 'key-name'
            },
        }
    }
    unconvertible_actions, converted_resources = self.converter.convert(
        [resource], '')
    actual = yaml.safe_load(converted_resources)
    expected = resource.copy()
    # Name is moved from ['properties']['name'] to ['name'].
    del expected['properties']['name']
    expected['name'] = 'new-bucket'
    del expected['action']
    expected['type'] = 'gcp-types/storage-v1:buckets'

    self.assertEmpty(unconvertible_actions)
    self.assertLen(actual, 1)
    self.assertDictEqual(actual[0], expected)

  def test_unsupported_action_state(self):
    resource = {
        'name': 'test-unsupported-action-state-exception',
        'action': 'gcp-types/dns-v1:dns.changes.create',
        'properties': {
            'deletions': {
                'name': 'del-1',
            },
        }
    }
    with self.assertRaises(errors.UnsupportedActionStateError):
      self.converter.convert([resource], '')

  def test_project_set_iam_policy_policy_replacement_should_be_skipped(self):
    action_replacing_policy_entirely = {
        'name':
            'resource-name',
        'action':
            'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy',
        'properties': {
            'policy': {
                'bindings': [{
                    'members': [],
                    'role': 'roles/compute.admin',
                }]
            },
            'resource': 'project-id',
        }
    }

    unconvertible_actions, converted_resources = self.converter.convert(
        [action_replacing_policy_entirely], '')

    self.assertEqual(unconvertible_actions, [action_replacing_policy_entirely])
    self.assertEmpty(converted_resources)

  @parameterized.parameters([
      'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy'
  ])
  def test_ignored_actions_should_output_nothing(self, ignored_action_type):
    resource = {
        'name': 'resource-name',
        'action': ignored_action_type,
        'properties': {},
    }

    unconvertible_actions, converted_resources = self.converter.convert(
        [resource], '')

    self.assertEmpty(unconvertible_actions)
    self.assertEmpty(converted_resources)


class DmActionConverterJinjaMacroTest(parameterized.TestCase,
                                      absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.base_dir = self.create_tempdir()
    self.templates_dir = self.base_dir.mkdir('actions/templates')
    self.copy_jinja_macros()
    self.write_action_to_dm_resource_type_mapping(
        'gcp-types/test:dm.action: dest_type')

  @parameterized.named_parameters(
      {
          'testcase_name': 'no_field_name_substitutions',
          'jinja_template': DEFAULT_TEMPLATE,
          'action_input': DEFAULT_ACTION,
          'expected_resource': DEFAULT_RESOURCE
      },
      {
          'testcase_name':
              'fields_in_mapping_not_in_resource_should_be_ignored',
          'jinja_template':
              DEFAULT_TEMPLATE,
          'action_input':
              ACTION_CONTAINING_UNMAPPED_FIELD,
          'expected_resource':
              DEFAULT_RESOURCE
      },
      {
          'testcase_name': 'field_name_substitutions',
          'jinja_template': TEMPLATE_RENAMING_KEYS,
          'action_input': ACTION_WITH_LIST_AND_MAP,
          'expected_resource': RESOURCE_WITH_RENAMED_KEYS
      },
      {
          'testcase_name': 'only_top_level_mappings_should_preserve_subfields',
          'jinja_template': TEMPLATE_WITH_ONLY_TOP_LEVEL_MAPPINGS,
          'action_input': ACTION_WITH_LIST_AND_MAP,
          'expected_resource': RESOURCE_WITH_LIST_AND_MAP
      },
  )
  def test_jinja_macros(self, jinja_template, action_input, expected_resource):
    self.write_action_to_resource_template(jinja_template)

    templates_dir = pathlib.Path(self.templates_dir)
    self.converter = dm_action_converter.DmActionConverter(
        templates_dir=templates_dir,
        template_resolver=template_resolver.get_instance(
            'actions', templates_dir))

    unconvertible_actions, converted_resources = self.converter.convert(
        [action_input], '')
    actual = yaml.safe_load(converted_resources)

    self.assertEmpty(unconvertible_actions)
    self.assertLen(actual, 1)
    self.assertDictEqual(actual[0], expected_resource)

  def write_action_to_resource_template(self, content):
    pathlib.Path().joinpath(self.templates_dir.full_path,
                            'dest_type.jinja').write_text(
                                content, encoding='utf-8')

  def copy_jinja_macros(self):
    shutil.copyfile(
        pathlib.Path().joinpath(
            resource_reader.get_templates_dir('actions'),
            'action_macros.jinja'),
        pathlib.Path().joinpath(self.templates_dir, 'action_macros.jinja'))

  def write_action_to_dm_resource_type_mapping(self, content):
    pathlib.Path().joinpath(self.base_dir.full_path, 'actions',
                            'templates.yaml').write_text(
                                content, encoding='utf-8')


if __name__ == '__main__':
  absltest.main()
