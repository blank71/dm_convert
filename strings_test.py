import strings
from absl.testing import absltest


class StringsTest(absltest.TestCase):

  def test_build_patter(self):
    plural = 'copies'
    self.assertEqual(strings.depluralize(plural), 'copy')
    plural = 'losses'
    self.assertEqual(strings.depluralize(plural), 'loss')
    plural = 'items'
    self.assertEqual(strings.depluralize(plural), 'item')

  def test_recapitalize(self):
    raw = 'httpHealthCheck'
    self.assertEqual(strings.recapitalize(raw), 'httpHealthCheck')
    raw = 'an sqlserver'
    self.assertEqual(strings.recapitalize(raw), 'an SQLserver')

  def test_pascal_to_snake(self):
    pascal = 'helloXXX'
    self.assertEqual(strings.pascal_to_snake(pascal), 'hello_x_x_x')

  def test_uppercase_first(self):
    s = 'a string'
    self.assertEqual(strings.uppercase_first(s), 'A string')

  def test_tf_id_replace_invalid_char(self):
    invalid = 'invalid.resource-1:name@here'
    self.assertEqual(
        strings.tf_id_replace_invalid_char(invalid),
        'invalid_resource_1_name_here')

  def test_tf_resource_name_fix_starting(self):
    invalid = '123invalid'
    self.assertEqual(
        strings.tf_resource_name_fix_starting(invalid),
        '_123invalid')

  def test_type_is_gcp_type(self):
    gcp_type = 'gcp-types/cloudkms-v1:projects.locations.keyRings.cryptoKeys'
    self.assertTrue(strings.is_gcp_types_actions(gcp_type))

  def test_type_is_gcp_action(self):
    gcp_action = 'gcp-types/compute-v1:compute.subnetworks.get'
    self.assertTrue(strings.is_gcp_types_actions(gcp_action))

  def test_type_is_customized_type(self):
    customized_type = 'my-types/some-collection'
    self.assertFalse(strings.is_gcp_types_actions(customized_type))

  def test_type_is_legacy_type(self):
    legacy_type = 'compute.v1.targetPool'
    self.assertTrue(strings.is_legacy_types(legacy_type))

  def test_type_is_not_legacy_type(self):
    customized_type = 'my-types.my-collection'
    self.assertFalse(strings.is_legacy_types(customized_type))


if __name__ == '__main__':
  absltest.main()
