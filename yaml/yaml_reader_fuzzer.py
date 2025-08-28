"""A simple fuzzer for yaml Reader."""

import sys

import atheris
import yaml


def TestOneInput(data: bytes) -> int:
  if len(data) < 1:
    return 0
  try:
    stream = yaml.reader.Reader(data)
    while stream.peek() != u'\0':
      stream.forward()
  except yaml.reader.ReaderError:
    return 0
  return 0

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
