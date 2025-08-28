"""A simple fuzzer for yaml loader with FullLoader."""

import sys

import atheris
import yaml


def TestOneInput(input_bytes: bytes) -> int:
  try:
    context = yaml.load(input_bytes, Loader=yaml.FullLoader)
  except yaml.YAMLError:
    return 0
  return 0


atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
