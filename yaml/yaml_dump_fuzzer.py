"""A simple fuzzer for yaml dump and load."""

import sys

import atheris
import yaml


def TestOneInput(data: bytes) -> int:
  try:
    yaml.dump(yaml.load(data, Loader=yaml.CLoader), Dumper=yaml.CDumper)
  except yaml.YAMLError:
    return 0
  return 0


atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
