from absl.testing import absltest

import base_converter
from absl.testing import absltest
from absl.testing import parameterized


class BaseConverterTest(parameterized.TestCase, absltest.TestCase):

  @parameterized.parameters({
      'project_name': 'rll-10000000-2-project',
      'billing_account_name': 'billingAccounts/0000EA-C00000-700000t',
      'billing_name': 'rll-10000000-2-billing'
  })
  def test_removed_depends_on_billing(self, project_name: str,
                                      billing_account_name: str,
                                      billing_name: str):
    dm_resources = [{
        'name': project_name,
        'properties': {
            'labels': [],
            'name': 'rll-10000000-2',
            'parent': {
                'id': '9999999999999',
                'type': 'folder',
                'projectId': 'rll-10000000-2'
            }
        },
        'type': 'gcp-types/cloudresourcemanager-v1:projects'
    }, {
        'metadata': {
            'dependsOn': [project_name]
        },
        'name': billing_name,
        'properties': {
            'billingAccountName': billing_account_name,
            'name': 'projects/$(ref.' + project_name + '.projectId)'
        },
        'type':
            'deploymentmanager.v2.virtual.projectBillingInfo'
    }, {
        'metadata': {
            'dependsOn': [project_name, billing_name]
        },
        'name': 'rll-10000000-2-api-cloudresourcemanager.googleapis.com',
        'properties': {
            'consumerId': 'project:$(ref.' + project_name + '.projectId)',
            'serviceName': 'cloudresourcemanager.googleapis.com'
        },
        'type':
            'gcp-types/servicemanagement-v1:servicemanagement.services.enable'
    }]

    base_converter.pre_process_billing(dm_resources)
    # Billing resource is removed
    self.assertNotIn(billing_account_name, dm_resources)
    self.assertLen(dm_resources, 2)
    # Depends on billing is removed from the resources
    self.assertLen(dm_resources[1]['metadata']['dependsOn'], 1)
    self.assertNotIn(billing_name,
                     dm_resources[1]['metadata']['dependsOn'])

  def test_get_tf_import_statements(self):

    # None resource
    tf_import = base_converter.get_tf_import_statements(None, 'my-test-project')
    self.assertIsNone(tf_import)

    # No tf import statement in the resource
    tf_import = base_converter.get_tf_import_statements(
        'some converted resource', 'my-test-project')
    self.assertEmpty(tf_import)

    # Tf import statement is found, but there is no project placeholder
    expanded = (
        '#tfimport-terraform import google_compute_address.compute_address  '
        'us-west1/compute-address\nresource "google_compute_address" '
        '"compute_address" {'
    )
    tf_import = base_converter.get_tf_import_statements(
        expanded, 'my-test-project'
    )
    self.assertEqual(
        tf_import,
        [
            (
                'terraform import google_compute_address.compute_address  '
                'us-west1/compute-address'
            )
        ],
    )

    # Multiple import statements are found, but there is no project placeholder
    expanded = (
        '#tfimport-terraform import google_compute_address.compute_address  '
        'us-west1/compute-address\nresource "google_compute_address" '
        '"compute_address" {}'
        '#tfimport-terraform import foo.bar  '
        'us-west1/foo\nresource "foo" '
        '"bar" {}'
        '#tfimport-terraform import foo.baz  '
        'us-west1/baz\nresource "foo" '
        '"baz" {}'
    )
    tf_import = base_converter.get_tf_import_statements(
        expanded, 'my-test-project'
    )
    self.assertEqual(
        tf_import,
        [
            (
                'terraform import google_compute_address.compute_address '
                ' us-west1/compute-address'
            ),
            'terraform import foo.bar  us-west1/foo',
            'terraform import foo.baz  us-west1/baz',
        ],
    )

    # Tf import statement is found, and there is a project placeholder
    # and project id is not passed.
    expanded = (
        '#tfimport-terraform import google_compute_address.compute_address  '
        '__project__/us-west1/compute-address\nresource '
        '"google_compute_address" "compute_address" {')
    tf_import = base_converter.get_tf_import_statements(expanded, None)
    self.assertEqual(
        tf_import,
        [('#WARNING: This import statement was generated without '
          'explicit project id\n'
          'terraform import google_compute_address.compute_address  '
          'us-west1/compute-address')])

    # Tf import statement is found, and there is a project placeholder
    # and project id is passed.
    expanded = (
        '#tfimport-terraform import google_compute_address.compute_address  '
        '__project__/us-west1/compute-address\nresource '
        '"google_compute_address" "compute_address" {')
    tf_import = base_converter.get_tf_import_statements(expanded, 'my-project')
    self.assertEqual(
        tf_import,
        [
            (
                'terraform import google_compute_address.compute_address  '
                'my-project/us-west1/compute-address'
            )
        ],
    )

    # Multiple import statements are found, and there is a project placeholder
    # and project id is passed.
    expanded = (
        '#tfimport-terraform import google_compute_address.compute_address  '
        '__project__/us-west1/compute-address\nresource '
        '"google_compute_address" "compute_address" {'
        '#tfimport-terraform import foo.bar  '
        '__project__/us-west1/foo\nresource '
        '"foo" "bar" {')
    tf_import = base_converter.get_tf_import_statements(expanded, 'my-project')
    self.assertEqual(
        tf_import,
        [
            (
                'terraform import google_compute_address.compute_address  '
                'my-project/us-west1/compute-address'
            ),
            'terraform import foo.bar  my-project/us-west1/foo',
        ],
    )

  def test_pre_process_service_enable_type(self):
    dm_resources = [{
        'metadata': {
            'dependsOn': ['rll-10000000-2-project']
        },
        'name': 'rll-10000000-2-api-deploymentmanager.googleapis.com',
        'properties': {
            'serviceName': 'deploymentmanager.googleapis.com',
            'consumerId': 'project:$(ref.rll-10000000-2-project.projectId)'
        },
        'type':
            'gcp-types/servicemanagement-v1:servicemanagement.services.enable'
    }]

    base_converter.pre_process_service_enable_type(dm_resources)

    self.assertNotIn(
        'gcp-types/servicemanagement-v1:servicemanagement.services.enable',
        dm_resources)
    self.assertEqual('deploymentmanager.v2.virtual.enableService',
                     dm_resources[0]['type'])

  @parameterized.parameters(
      {
          'billing_info_project_name': 'projects/my-test-project',
          'project_resource_type': 'cloudresourcemanager.v1.project'
      }, {
          'billing_info_project_name': 'projects/my-test-project',
          'project_resource_type': 'gcp-types/cloudresourcemanager-v1:projects'
      }, {
          'billing_info_project_name':
              'projects/$(ref.my_test_project_resource.projectId)',
          'project_resource_type':
              'cloudresourcemanager.v1.project'
      }, {
          'billing_info_project_name':
              'projects/$(ref.my_test_project_resource.projectId)',
          'project_resource_type':
              'gcp-types/cloudresourcemanager-v1:projects'
      })
  def test_pre_process_billing(self, billing_info_project_name: str,
                               project_resource_type: str):
    dm_resources = [{
        'name': 'my_test_project_resource',
        'properties': {
            'name': 'my-test-project',
            'parent': {
                'id': '119612413569',
                'type': 'organization'
            },
            'projectId': 'my-test-project'
        },
        'type': project_resource_type
    }, {
        'metadata': {
            'dependsOn': ['my_test_project']
        },
        'name': 'billing_my_test_project',
        'properties': {
            'billingAccountName': 'billingAccounts/000000-AAAAFF-123456',
            'name': billing_info_project_name
        },
        'type': 'deploymentmanager.v2.virtual.projectBillingInfo'
    }]

    base_converter.pre_process_billing(dm_resources)

    self.assertNotIn('billing_my_test_project', dm_resources)
    self.assertIn('billingAccountName', dm_resources[0]['properties'])
    self.assertEqual('billingAccounts/000000-AAAAFF-123456',
                     dm_resources[0]['properties']['billingAccountName'])

if __name__ == '__main__':
  absltest.main()
