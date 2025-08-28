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
import importlib
import importlib.util
import io
from os import sep
import os.path
import sys


def open(name, mode=None, buffering=None):  # pylint: disable=unused-argument, redefined-builtin
  if name in FileAccessRedirector.allowed_imports:
    if mode is not None and 'w' in mode:
      raise IOError('file \'%s\' is read-only' % name)
    else:
      return io.StringIO(FileAccessRedirector.allowed_imports[name])
  else:
    raise IOError('file \'%s\' is not available' % name)


class AllowedImportsLoader(object):
  # Dictionary with modules loaded from user provided imports
  user_modules = {}

  @staticmethod
  def get_filename(name):
    return '%s.py' % name.replace('.', '/')

  def load_module(self, name, etc=None):  # pylint: disable=unused-argument
    """Implements loader.load_module() for loading user provided imports."""

    if name in AllowedImportsLoader.user_modules:
      return AllowedImportsLoader.user_modules[name]

    spec = importlib.util.spec_from_loader(name, loader=None)
    module = importlib.util.module_from_spec(spec)

    try:
      data = FileAccessRedirector.allowed_imports[self.get_filename(name)]
    except IOError:
      raise ImportError('import \'%s\' not available' % name)

    # Run the module code.
    exec(data, module.__dict__)  # pylint: disable=exec-used

    AllowedImportsLoader.user_modules[name] = module

    # We need to register the module in module registry, since new_module
    # doesn't do this, but we need it for hierarchical references.
    sys.modules[name] = module

    # If this module has children load them recursively.
    if name in FileAccessRedirector.parents:
      # We don't know the order of children so we'll try to load them and if
      # something that they import hasn't yet been imported, we'll pass
      # over them and try to load that import during the next pass.
      children = FileAccessRedirector.parents[name]
      # If there are N children and they are somehow ordered in the reverse
      # order (linked list), then we'll have to do at most N iterations
      # in this worst case.
      loaded = 0
      num_iters = 0
      while loaded < len(children) and num_iters < len(children):
        num_iters += 1
        for child in children:
          try:
            full_name = name + '.' + child
            # Skip loading modules that have already been loaded.
            if full_name in AllowedImportsLoader.user_modules:
              continue
            self.load_module(full_name)
            # If we have helpers/common.py package, then for it to be
            # successfully resolved helpers.common name must resolvable,
            # hence, once we load child package we attach it to parent module
            # immediately.
            module.__dict__[child] = AllowedImportsLoader.user_modules[
                full_name
            ]
            loaded += 1
            # Loaded everything, no need to load anything anymore.
            if loaded >= len(children):
              break
          except ImportError:
            pass
    return module


class AllowedImportsHandler(object):
  """Allowlist which imports can be used."""

  def find_module(self, name, path=None):  # pylint: disable=unused-argument
    filename = AllowedImportsLoader.get_filename(name)

    if filename in FileAccessRedirector.allowed_imports:
      return AllowedImportsLoader()
    else:
      return None

  def find_spec(self, name, path=None, target=None):  # pylint: disable=unused-argument
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
    dictionary of imports to their contents and parent-child pacakge
    relationship map.
  """
  # First clone all the existing ones.
  ret = {}
  parents = {}
  for k in imports:
    ret[k] = imports[k]

  # Now build the hierarchical modules.
  for k in imports.keys():
    if imports[k].endswith('.jinja'):
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
  # Dictionary with user provided imports.
  allowed_imports = {}
  # Dictionary that shows parent child relationships, key is the parent, value
  # is the list of child packages.
  parents = {}

  @staticmethod
  def redirect(imports, redirect_open):
    """Restricts imports and builtin 'open' to the set of user provided imports.

    Imports already available in sys.modules will continue to be available.

    Args:
      imports: map from string to string, the map of imported files names
          and contents.
      redirect_open: True to redirect builtin 'open' and restrict it to the set
          of user provided imports; False otherwise
    """
    if imports is not None:
      imps, parents = process_imports(imports)
      FileAccessRedirector.allowed_imports = imps
      FileAccessRedirector.parents = parents

      sys.meta_path = [AllowedImportsHandler()]

    if redirect_open:
      builtins.open = open
