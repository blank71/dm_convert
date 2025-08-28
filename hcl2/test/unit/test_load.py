"""Test parsing a variety of hcl files."""

import json
import os

from hcl2 import api
from absl.testing import absltest

HCL2_DIR = 'terraform-config'
JSON_DIR = 'terraform-config-json'


class TestLoad(absltest.TestCase):
    """Test parsing a variety of hcl files."""

    def setUp(self):
        super().setUp()
        self.prev_dir = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(__file__), '../helpers'))

    def test_load_terraform_files(self):
        """Recursively parse all files in a directory."""
        # pylint: disable=unused-variable
        for current_dir, dirs, files in os.walk('terraform-config'):
            dir_prefix = os.path.commonpath([HCL2_DIR, current_dir])
            relative_current_dir = current_dir.replace(dir_prefix, '')
            current_out_dir = os.path.join(JSON_DIR, relative_current_dir)
            for file_name in files:
                file_path = os.path.join(current_dir, file_name)
                json_file_path = os.path.join(current_out_dir, file_name)
                json_file_path = os.path.splitext(json_file_path)[0] + '.json'

                with self.subTest(msg=file_path):
                    with open(file_path, 'r') as hcl2_file, open(json_file_path, 'r') as json_file:
                        try:
                            hcl2_dict = api.load(hcl2_file)
                        except Exception as ex:
                            raise RuntimeError(f'failed to tokenize terraform in `{file_path}`') from ex

                        json_dict = json.load(json_file)
                        self.assertDictEqual(hcl2_dict, json_dict)


if __name__ == '__main__':
    absltest.main()
