"""Loader for loading modules from a user provided dictionary of imports.

The main goal is supporting Python imports when running user provided Python
code in a sandbox that restricts access to files. User simply needs to provide
a dictionary with the content of the imported modules.

The mechanism is intended primarily for user's custom imports, since system and
other well known modules can be "whitelisted" and made available by the sandbox.

The mechanism implemented in this file is NOT a security boundary (security
restrictions are provided by the sandbox). Rather, it allows running - without
modifications - Python code that would otherwise fail trying to import custom
modules from files that are not available when running in a sandbox.

It also allow running - without modifications - Python code that uses 'open' to
access "files", as long as the content of the "file" is included
in the dictionary provided by the user.

All the above is accomplished by using sys.meta_path hook and redefining
the 'open' builtin.

The hook is set to an instance of AllowedImportsHandler class. When Python
framework attempts to load a module, it calls find_module() method from
AllowedImportsHandler. If the request is for one of user provided imports then
the method returns an instance of AllowedImportsLoader to handle loading.
AllowedImportsLoader checks if it already loaded a given module and if so
it returns the module. Otherwise it loads the module from the user provided
dictionary of imports using the redefined 'open' builtin. Then it initializes
the module.

To invoke this mechanism, FileAccessRedirector.redirect needs to be called with
the user provided dictionary of imports.
"""

import builtins
from collections import defaultdict
import importlib
import io
import os
from os import environ
from os import sep
import os.path
import sys
from absl import logging as log




_composite_type_url = None
_user_modules_registered = []
SEPARATOR = '.'


def set_composite_type_url(url):
  """Sets the main composite type url and clears previous imports."""
  global _composite_type_url
  # Clear any modules registered since the last composite url context switch
  for module_name in _user_modules_registered:
    if module_name in sys.modules:
      del sys.modules[module_name]
  _composite_type_url = url


def open(name, mode=None, buffering=None):  # pylint: disable=unused-argument, redefined-builtin
  """Override default open to restrict the imports."""
  if (_composite_type_url and
      _composite_type_url in FileAccessRedirector.composite_allowed_imports):
    import_dict = FileAccessRedirector.composite_allowed_imports[
        _composite_type_url]
  else:
    import_dict = FileAccessRedirector.allowed_imports
  if name in import_dict:
    if mode is not None and 'w' in mode:
      raise IOError('file \'%s\' is read-only' % name)
    else:
      return io.StringIO(import_dict[name])
  else:
    raise IOError('file \'%s\' is not available' % name)


class LazyModule(dict):
  """A module that loads modules on the fly given a loader."""

  def __init__(self, loader, name):
    """Creates a module given a loader and a name."""
    super(LazyModule, self).__init__()
    self.__loader__ = loader
    self.__path__ = name
    self.__name__ = self.__package__ = name
    self.__file__ = name
    self.__spec__ = None
    log.debug('Creating module %s' % (name))

  def __getattr__(self, child):
    """Overrides getattr to load modules on the fly."""
    log.debug('getattr %s child %s' % (self.__name__, child))
    if self.__loader__.is_package(self.__name__):
      log.debug('Delegating lazy load')
      return self.__loader__.load_module(self.__name__ + '.' + child)
    return self.__dict__[child]


class AllowedImportsLoader(object):
  """Custom loader that checks the imports from user and nothing else."""
  # Dictionary with modules loaded from user provided imports
  user_modules = {}
  # Dictionary with modules loaded from the current composite type
  composite_user_modules = defaultdict(dict)

  # Imported modules whose child modules have also been successfully loaded.
  imported = {}

  # Holds the imported modules for composite type.
  composite_imported = defaultdict(dict)

  @staticmethod
  def sanitize_windows_path(filepath):
    return filepath.replace('\\', '/')

  @staticmethod
  def get_filename(name):
    return '%s.py' % name.replace('.', '/')

  @staticmethod
  def get_parents(name):
    """Get the set of parent modules for the given module name."""
    parents = set()
    if SEPARATOR in name:
      parts = name.split(SEPARATOR)
      for i in range(1, len(parts)):
        path = SEPARATOR.join(parts[:i])
        parents.add(path)
    return parents

  def is_package(self, name):
    if (_composite_type_url and _composite_type_url in (
        FileAccessRedirector.composite_allowed_imports)):
      parent_dict = FileAccessRedirector.composite_parents[_composite_type_url]
    else:
      parent_dict = FileAccessRedirector.parents
    return name in parent_dict

  def load_module(self, name, etc=None):  # pylint: disable=unused-argument
    """Implements loader.load_module() for loading user provided imports."""
    if (_composite_type_url and _composite_type_url in (
        FileAccessRedirector.composite_allowed_imports)):
      import_dict = FileAccessRedirector.composite_allowed_imports[
          _composite_type_url]
    else:
      import_dict = FileAccessRedirector.allowed_imports
    if _composite_type_url:
      user_module_dict = AllowedImportsLoader.composite_user_modules[
          _composite_type_url]
      imported_module_dict = AllowedImportsLoader.composite_imported[
          _composite_type_url]
    else:
      user_module_dict = AllowedImportsLoader.user_modules
      imported_module_dict = AllowedImportsLoader.imported
    if name in imported_module_dict:
      return imported_module_dict[name]
    log.info('Loading %s' % (name))
    module = LazyModule(self, name)
    user_module_dict[name] = module
    imported_module_dict[name] = module
    # We need to register the module in module registry, since new_module
    # doesn't do this, but we need it for hierarchical references.
    sys.modules[name] = module
    if _composite_type_url:
      _user_modules_registered.append(name)
    if self.is_package(name):
      return module
    filename = self.get_filename(name)
    try:
      data = import_dict[filename]
    except IOError:
      raise ImportError('import \'%s\' not available' % name)
    # Run the module code.
    code = compile(data, filename, 'exec')
    exec(code, module.__dict__)  # pylint: disable=exec-used
    return module


class AllowedImportsHandler(object):
  """Whitelist which imports can be used."""

  def find_module(self, name, path=None):  # pylint: disable=unused-argument
    """Gets a module by name."""
    filename = AllowedImportsLoader.get_filename(name)

    if (_composite_type_url and
        _composite_type_url in FileAccessRedirector.composite_allowed_imports):
      import_dict = FileAccessRedirector.composite_allowed_imports[
          _composite_type_url]
    else:
      import_dict = FileAccessRedirector.allowed_imports
    if filename in import_dict:
      return AllowedImportsLoader()
    else:
      return None

  def find_spec(self, name, path=None, target=None):  # pylint: disable=unused-argument
    """Gets a module by name."""
    result = self.find_module(name, path)
    if result is None:
      return None
    return importlib.machinery.ModuleSpec(name, result)


def process_imports(imports):
  """Processes the imports by copying them and adding necessary parent packages.

    Copies the imports and then for all the hierarchical packages creates
    dummy entries for those parent packages, so that hierarchical imports
    can be resolved. In the process parent child relationship map is built.
    For example: helpers/extra/common.py will generate helpers, helpers.extra
    and helpers.extra.common packages along with related .py files.

  Args:
    imports: map of files to their relative paths.
  Returns:
    dictionary of imports to their contents and parent-child package
    relationship map.
  """
  # First clone all the existing ones.
  ret = {}
  parents = {}
  ret = imports.copy()

  # Now build the hierarchical modules.
  for k in list(ret):
    if k.endswith('.jinja'):
      continue
    # Normalize paths and trim .py extension, if any.
    normalized = os.path.splitext(os.path.normpath(k))[0]
    # If this is actually a path and not an absolute name, split it and process
    # the hierarchical packages.
    if sep in normalized:
      parts = normalized.split(sep)
      # Create dummy file entries for package levels and also retain
      # parent-child relationships.
      for i in range(0, len(parts) - 1):
        # Generate the partial package path.
        path = os.path.join(parts[0], *parts[1:i+1])
        # __init__.py file might have been provided and non-empty by the user.
        if path not in ret:
          # exec requires at least new line to be present to successfully
          # compile the file.
          ret[path + '.py'] = '\n'
        else:
          # To simplify our code, we'll store both versions in that case, since
          # loader code expects files with .py extension.
          ret[path + '.py'] = ret[path]
        # Generate fully qualified package name.
        fqpn = '.'.join(parts[0:i+1])
        if fqpn in parents:
          parents[fqpn].append(parts[i+1])
        else:
          parents[fqpn] = [parts[i+1]]
  return ret, parents


class FileAccessRedirector(object):
  """Class to redirect open based on parent/child relationship."""
  # Dictionary with user provided imports.
  allowed_imports = {}
  # Dictionary that shows parent child relationships, key is the parent, value
  # is the list of child packages.
  parents = {}

  # Dictionary with user provided imports keyed by importing composite type url.
  composite_allowed_imports = {}
  # Dictionary that shows parent child relationships, key is the parent, value
  # is the list of child packages keyed by importing composite type url.
  composite_parents = {}

  @staticmethod
  def redirect(imports, redirect_open, composite_type_imports=None):
    """Restricts imports and builtin 'open' to the set of user provided imports.

    Imports already available in sys.modules will continue to be available.

    Args:
      imports: map from string to string, the map of imported files names
          and contents.
      redirect_open: True to redirect builtin 'open' and restrict it to the set
          of user provided imports; False otherwise
      composite_type_imports: If it is a composite type, the list of imports
          restricted for this template.
    """
    if imports is not None:
      imps, parents = process_imports(imports)
      FileAccessRedirector.allowed_imports = imps
      FileAccessRedirector.parents = parents
      sys.meta_path = [AllowedImportsHandler()]
    if composite_type_imports is not None:
      for composite_url in composite_type_imports:
        imps, parents = process_imports(composite_type_imports[composite_url])
        FileAccessRedirector.composite_allowed_imports[composite_url] = imps
        FileAccessRedirector.composite_parents[composite_url] = parents

    if redirect_open and 'USE_SANDBOX' in environ:
      builtins.open = open
