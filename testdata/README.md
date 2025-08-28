# DM Convert Test Data

New files added here must respect the following patterns:

*   Each subfolder must contain a `deployment.yaml` file to be tested.
*   Each subfolder can contain a `krms.yaml` file and a `resources.tf` file. If
    either of these files are present, a `cmd_golden_rule` test will be
    generated for them, comparing the converted output of `deployment`yaml` with
    these files.

The logic which generates the cmd_golden_rules test targets can be found in
../testdata_golden_tests.bzl.

## Regenerating golden files

```shell
$ cd cloud/config/tools/dm_convert
$ scripts/regenerate_golden_files.sh --format=[KRM|TF]
```
