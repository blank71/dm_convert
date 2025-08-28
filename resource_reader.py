"""Provides read access to conversion templates for use in a GoB repository.

Avoids a dependency on google3.pyglib import resources.
This file is used as a replacement for ./resource_reader.py when copying to GoB.
"""

import os
import pathlib

_LICENSES_FILE_NAME = 'THIRD_PARTY_NOTICES'


def get_base_dir() -> pathlib.Path:
  return _get_root()


def get_templates_dir(output_format: str) -> pathlib.Path:
  return pathlib.Path().joinpath(_get_root(), output_format, 'templates')


def get_testdata_dir() -> pathlib.Path:
  return pathlib.Path().joinpath(_get_root(), 'testdata')


def read_resource_bytes(file: pathlib.Path):
  with open(file, 'rb') as f:
    return f.read()


def read_resource_utf8(file: pathlib.Path):
  return read_resource_bytes(file).decode('utf-8')


def walk_testdata_folder():
  return os.walk(get_testdata_dir())


def get_license_file() -> pathlib.Path:
  return pathlib.Path().joinpath(_get_root(), _LICENSES_FILE_NAME)


def _get_root():
  # Assumes that the current file is at root.
  return pathlib.Path(__file__).parent.absolute()
