# Copyright 2014 Google Inc. All Rights Reserved.
"""Template expansion utilities for deployment manager v2."""

# jinja2 re-encodes all the strings with unicode escape and this triggers
# loading of this module dynamically, which does not really work under gVisor.

import configparser  # @UnusedImport pylint: disable=unused-import
import encodings.unicode_escape  # @UnusedImport pylint: disable=unused-import
from http import server  # @UnusedImport pylint: disable=unused-import
import importlib
import io
import os.path
import pathlib
import re
import socketserver  # @UnusedImport pylint: disable=unused-import
import sys
import traceback
from typing import Any
import uuid
import zipfile  # @UnusedImport pylint: disable=unused-import
from absl import flags
import jinja2
# jinja2 attempts to import its debug module first time it is needed, but this
# doesn't work under gVisor, so let's preload it.
from jinja2 import debug  # @UnusedImport pylint: disable=unused-import
import six
import yaml
from expansion import multiple_sandbox_loader
from expansion import references
from expansion import sandbox_loader
from expansion import schema_validation
from absl import logging as log



_MODULE_PATH = flags.DEFINE_string(
    'module_path', './bin/modules',
    'The path to the "modules" file to load. If empty, runfiles directory '
    'will be used to load the file.')

EMPTY_MANIFEST = {
    'config': {},
    'layout': {},
}


def _NoOpConstructor(unused_loader, node):
  return node.value


# Create a SafeDumper that doesn't do aliases.
noalias_dumper = yaml.dumper.SafeDumper

# Allow unicode pass-through otherwise the yaml parser crashes trying to load
# unicode.
yaml.SafeLoader.add_constructor('tag:yaml.org,2002:python/unicode',
                                _NoOpConstructor)

noalias_dumper.ignore_aliases = lambda self, data: True

TAG_STR = 'tag:yaml.org,2002:str'


def StringRepresenter(dumper: yaml.dumper.Dumper, value: str) -> str:
  if value.startswith('0'):
    return dumper.represent_scalar(TAG_STR, value, style="'")

  return dumper.represent_scalar(TAG_STR, value)

noalias_dumper.add_representer(six.text_type, StringRepresenter)

# The template methods we'll invoke in python code.
TEMPLATE_METHODS = ['generate_config', 'GenerateConfig']

ADD_LAYOUT_ID_KEY = 'ADD_LAYOUT_ID'

# All the legal fields for a resource.
RESOURCE_SECTIONS = ['name', 'type', 'metadata', 'properties', 'action']


def _GetRunfilePath():
  return os.path.join(
                      pathlib.Path(__file__).parent.absolute(),
                      'modules')


def _LoadModule(module):
  """_LoadModule loads a given module into memory and sets up global variables.

     _LoadModule loads the module given in the input in the memory and sets up
     all the releveant global variables in memory, so that module can be used
     normally.

  Args:
    module: the name of the module to import, can be hierarchical name.

  Raises:
    importlib.ImportError if such module does not exist.
  """

  try:
    importlib.import_module(module)
    path = module.split('.')
    # If module was hierarchical, then setup global variable to point to the
    # topmost parent package, otherwise path[0] will point to the module itself.
    if path[0] not in globals():
      globals()[path[0]] = sys.modules[path[0]]
  except Exception:  # pylint: disable=broad-except
    log.info(traceback.format_exc())
    pass


def ToYaml(obj):
  """Converts an object to yaml format."""
  return yaml.dump(
      obj, allow_unicode=True, default_flow_style=False, Dumper=noalias_dumper)


def GetStandardModules():
  """Finds and reads the modules file that contains the standard modules.

  We preload these modules in LoadStandardModules() below.

  Returns:
    The list of modules in the modules file.
  """
  # The contents of the modules file
  modules_string = ''

  # First try the command line args
  if _MODULE_PATH.value:
    try:
      with open(_MODULE_PATH.value, 'r') as module_file:
        modules_string = module_file.read()
      log.info('Modules file loaded')
    except Exception:  # pylint: disable=broad-except
      # Couldn't find the file, move on
      log.debug(traceback.format_exc())

  # Couldn't load from the file above, let's try loading from resources,
  # since we include the modules file as a data dependency in BUILD
  if not modules_string:
    try:
      modules_string = resources.GetResource(
          'google3/cloud/config/expansion/modules', mode='r')
      log.info('Modules resource loaded')
    except Exception:  # pylint: disable=broad-except
      # Couldn't find the resource, can't do anything
      log.debug(traceback.format_exc())

  # Clean up the whitespaces and comments, just in case
  return [
      module.strip()
      for module in modules_string.splitlines()
      if module and module[0] != '#'
  ]


def LoadStandardModules():
  """Opens the modules file and loads all the modules listed in the file.

     When the expansion runs under gVisor, all imports that are needed during
     the expansions by either our code or user's code need to be declared before
     calling restrict.GvisorRestrict().
  """

  try:
    modules = GetStandardModules()
    for module in modules:
      # Load the module and create a global variable with the name of the module
      _LoadModule(module)
    log.info(msg='Standard modules loaded: ' + ' '.join(modules))
  except Exception:  # pylint: disable=broad-except
    # Failed to preload modules, still try to continue expansion
    log.info(traceback.format_exc())
    pass


def ReadFileToString(filename: pathlib.Path) -> str:
  """ReadFileToString read the contents of the provided file to a string.

     Opens the provided file, reading the entirety of that file into a string
     and returning it to the user. The primary intent here is to provide a
     user-friendly error to help describe what might be wrong

  Args:
    filename: The name of the file to be read

  Returns:
    The contents of the file
  Raises:
    IOError
  """
  try:
    with io.open(filename, 'r', encoding='utf-8') as tempfile:
      return tempfile.read()
  except IOError:
    error = (f'Error when opening "{filename}". Double-check the filename '
             'and make sure you set the working directory with --working_dir.')
    raise IOError(error)


def _ResolveImportPath(import_path: pathlib.Path, working_dir: pathlib.Path,
                       config_dir: pathlib.Path) -> pathlib.Path:
  """Resolves imports file absolute path."""
  resolved_path = working_dir.joinpath(import_path).resolve()
  if resolved_path.is_file():
    return resolved_path
  # If import path relative to the working dir doesn't exist, then try to
  # find it using relative to config dir path.
  relative_to_config_file_path = config_dir.joinpath(import_path).resolve()
  if relative_to_config_file_path != resolved_path:
    if relative_to_config_file_path.is_file():
      return relative_to_config_file_path
  raise IOError(f'Could not find import: "{import_path}"')


def BuildImports(
    imports: dict[str, str],
    config: dict[str, Any],
    working_dir: pathlib.Path,
    config_dir: pathlib.Path,
):
  """BuildImports searches for import files in configs, imports, schema files.

     Reads all found imports and their contents into imports dictionary.

  Args:
    imports: The dictionary of all imports with file name as key and file
      content as value. This dictionary is recursively populated by this method.
    config: The config file YAML.
    working_dir: The working directory where import files could be found.
    config_dir: The directory of the config file. It is used to look for imports
      in case their path is specified relative to config file.

  Raises:
    Exception: If it couldn't fine specified import.
  """

  if not ('imports' in config and config['imports']):
    return
  for import_from_yaml in config['imports']:
    if isinstance(import_from_yaml, dict):
      path = import_from_yaml.get('path', '')
    else:
      path = import_from_yaml
    file_path = _ResolveImportPath(path, working_dir, config_dir)
    import_name = import_from_yaml.get('name', path)
    if import_name in imports:
      continue
    imports[import_name] = ReadFileToString(file_path)
    schema_file_path = file_path.parent / '.'.join([file_path.name, 'schema'])
    if schema_file_path.is_file():
      schema_name = '.'.join([import_name, 'schema'])
      imports[schema_name] = ReadFileToString(schema_file_path)
      schema_contents = ReadFileToString(schema_file_path)
      schema_config = yaml.safe_load(schema_contents)
      if schema_config and 'imports' in schema_config:
        schema_file_dir = schema_file_path.parent
        BuildImports(imports, schema_config, working_dir, schema_file_dir)


def Expand(config,
           imports=None,
           composite_type_imports=None,
           composite_type_import_paths=None,
           env=None,
           restrict_open=True,
           validate_schema=False,
           outputs=False,
           previous_layout=None,
           path_overrides=None,
           experiments=None):
  """Expand the configuration with imports.

  Args:
    config: string, the raw config to be expanded.
    imports: map from string to string, the map of global imported files names
      and contents
    composite_type_imports: map from composite type url to map of imports for
      each composite type used in this deployment
    composite_type_import_paths: map from composite type url to map of path
      overrides for each composite type used in this deployment
    env: map from string to string, the map of environment variable names to
      their values
    restrict_open: True to restrict Python built-in open to the user provided
      imports; False otherwise. Note: Passing False is intended only for unit
        tests. When running under gVisor, restrict_open is ignored (and treated
        as True). Imports already available in sys.modules will continue to be
        available, regardless of the value of this argument.
    validate_schema: True to run schema validation; False otherwise
    outputs: True to process output values; False otherwise
    previous_layout: Optional layout from a previous partial expansion. Used for
      multi-trip expansion with external templates.
    path_overrides: Optional list of paths (ending in a template language
      extension) mapped to type names.
    experiments: Optional experiments that may affect expansion. If present will
      be a ExpansionExperiments proto.

  Returns:
    YAML string containing the expanded configuration and its layout,
    in the following format:

      config:
        ...
      layout:
        ...

  Raises:
    ExpansionError: if there is any error occurred during expansion
  """
  return ToYaml(
      ExpandToObject(
          config,
          imports=imports,
          composite_type_imports=composite_type_imports,
          composite_type_import_paths=composite_type_import_paths,
          env=env,
          restrict_open=restrict_open,
          validate_schema=validate_schema,
          outputs=outputs,
          previous_layout=previous_layout,
          path_overrides=path_overrides,
          experiments=experiments))


def ExpandToObject(config,
                   imports=None,
                   composite_type_imports=None,
                   composite_type_import_paths=None,
                   env=None,
                   restrict_open=True,
                   validate_schema=False,
                   outputs=False,
                   previous_layout=None,
                   path_overrides=None,
                   experiments=None):
  """Expand the configuration with imports.

  Args:
    config: string, the raw config to be expanded.
    imports: map from string to string, the map of global imported files names
      and contents
    composite_type_imports: map from composite type url to map of imports for
      each composite type used in this deployment
    composite_type_import_paths: map from composite type url to map of path
      overrides for each composite type used in this deployment
    env: map from string to string, the map of environment variable names to
      their values
    restrict_open: True to restrict Python built-in open to the user provided
      imports; False otherwise. Note: Passing False is intended only for unit
        tests. When running under gVisor, restrict_open is ignored (and treated
        as True). Imports already available in sys.modules will continue to be
        available, regardless of the value of this argument.
    validate_schema: True to run schema validation; False otherwise
    outputs: True to process output values; False otherwise
    previous_layout: Optional layout from a previous partial expansion. Used for
      multi-trip expansion with external templates.
    path_overrides: Optional list of paths (ending in a template language
      extension) mapped to type names.
    experiments: Optional experiments that may affect expansion. If present will
      be a ExpansionExperiments proto.

  Returns:
    Object containing the expanded configuration and its layout, in the
    following
    format:

      config:
        ...
      layout:
        ...

  Raises:
    ExpansionError: if there is any error occurred during expansion
  """
  try:
    # Preload standard modules in memory.
    LoadStandardModules()
    return _Expand(
        config,
        imports=imports,
        composite_type_imports=composite_type_imports,
        composite_type_import_paths=composite_type_import_paths,
        env=env,
        restrict_open=restrict_open,
        validate_schema=validate_schema,
        outputs=outputs,
        previous_layout=previous_layout,
        path_overrides=path_overrides,
        experiments=experiments)
  except MemoryError as e:
    # We want to relay MemoryError to the main.
    raise e
  except Exception as e:
    log.info(traceback.format_exc())
    raise ExpansionError('config', str(e))


def _LoadYaml(config, experiments):
  """Loads yaml without mashal or passthrough depending on experiment."""
  try:
    if experiments and experiments.enable_use_yamlin_without_marshal:
      try:
        # Only take the first yaml string
        return next((yaml.load_all(config, Loader=yaml.SafeLoader)))
      except StopIteration:
        return EMPTY_MANIFEST
    else:
      return yaml.safe_load(config)
  except yaml.scanner.ScannerError as e:
    # Here we know that YAML parser could not parse the template we've given it.
    # YAML raises a ScannerError that specifies which file had the problem, as
    # well as line and column, but since we're giving it the template from
    # string, error message contains <string>, which is not very helpful on the
    # user end, so replace it with word "template" and make it obvious that YAML
    # contains a syntactic error.
    msg = str(e).replace('"<string>"', 'template')
    raise Exception('Error parsing YAML: %s' % msg)


def _Expand(config,
            imports=None,
            composite_type_imports=None,
            composite_type_import_paths=None,
            env=None,
            restrict_open=True,
            validate_schema=False,
            outputs=False,
            previous_layout=None,
            path_overrides=None,
            experiments=None):
  """Expand the configuration with imports."""
  if (experiments and
      experiments.enable_composite_type_imports_in_separate_lists):
    multiple_sandbox_loader.FileAccessRedirector.redirect(
        imports, restrict_open, composite_type_imports)
  else:
    sandbox_loader.FileAccessRedirector.redirect(imports, restrict_open)
  yaml_config = _LoadYaml(config, experiments)
  # Handle empty file case.
  if yaml_config is None:
    return EMPTY_MANIFEST

  # For backward compatibility reasons we parse the yaml
  # from previous step, and if it is a string, we
  # return it to go server and will do double yaml parsing
  # after pass-through the result to expansion server
  # and we need to handle the double parsing case here
  if isinstance(yaml_config, str):
    yaml_config = _LoadYaml(yaml_config, experiments)
  if not isinstance(yaml_config, dict):
    raise Exception('Input config must be a map')

  if 'resources' not in yaml_config or yaml_config['resources'] is None:
    yaml_config['resources'] = []

  config = {'resources': []}

  if previous_layout and previous_layout != '{}':
    try:
      layout = yaml.safe_load(previous_layout)
    except yaml.scanner.ScannerError as e:
      msg = str(e).replace('"<string>"', 'layout')
      raise Exception('Error parsing layout: %s' % msg)
  else:
    layout = {'resources': []}

  # There is no parent resource here, so we just say 'yaml'.
  parent_name = 'yaml'
  all_names = _ValidateUniqueNames(yaml_config['resources'])

  # Iterate over all the resources to process.
  for resource in yaml_config['resources']:
    processed_resource = _ProcessResource(
        resource,
        imports,
        composite_type_imports,
        composite_type_import_paths,
        env,
        parent_name,
        all_names,
        experiments,
        validate_schema,
        outputs,
        path_overrides=path_overrides)

    config['resources'].extend(processed_resource['config']['resources'])

    # Merge child resource layout with previous layout, if provided.
    _MergeLayout(env, layout, processed_resource)

  _ProcessTargetConfig(yaml_config, outputs, config, layout, parent_name,
                       all_names, experiments)

  result = {'config': config, 'layout': layout}

  result = references.CleanBoundReferences(result)
  return result


def _MergeLayout(env, layout, processed_resource):
  if 'layout' in processed_resource:
    processed_resource = processed_resource['layout']
  layout_resource = _FindMatchingLayoutResource(
      layout, processed_resource['name'],
      (processed_resource.get('type') or processed_resource.get('action')))
  if layout and layout_resource:
    if 'properties' in processed_resource:
      layout_resource['properties'] = processed_resource['properties']
    if (env and (ADD_LAYOUT_ID_KEY in env) and ('id' in processed_resource) and
        ('id' not in layout_resource)):
      layout_resource['id'] = processed_resource['id']
    if 'resources' in processed_resource:
      for child_resource in processed_resource['resources']:
        _MergeLayout(env, layout_resource, child_resource)
  else:
    if 'resources' not in layout:
      layout['resources'] = []
    layout['resources'].append(processed_resource)


def _ProcessResource(resource,
                     imports,
                     composite_type_imports,
                     composite_type_import_paths,
                     env,
                     parent_name,
                     all_names,
                     experiments,
                     validate_schema=False,
                     outputs=False,
                     path_overrides=None,
                     composite_type_context=None):
  """Processes a resource and expands if template.

  Args:
    resource: the resource to be processed, as a map.
    imports: map from string to string, the map of imported files names and
      contents
    composite_type_imports: map from composite type url to map of imports for
      each composite type used in this deployment
    composite_type_import_paths: map from composite type url to map of path
      overrides for each composite type used in this deployment
    env: map from string to string, the map of environment variable names to
      their values
    parent_name: name of template resource that declared the resource being
      processed
    all_names: Names of all resources declared by the parent
    experiments: Experiments for this expansion run
    validate_schema: True to run schema validation; False otherwise
    outputs: True to process output values; False otherwise
    path_overrides: Optional list of paths (ending in a template language
      extension) mapped to type names.
    composite_type_context: The current composite type or catalog context, used
      to decide which set of imports to use.

  Returns:
    A map containing the layout and configuration of the expanded
    resource and any sub-resources, in the format:

    {'config': ..., 'layout': ...}
  Raises:
    ExpansionError: if there is any error occurred during expansion
  """
  # A resource has to have to a name.
  if 'name' not in resource:
    raise ExpansionError(resource, 'Resource does not have a name.')

  # Bind references found in the various sections of the resource.
  for resource_section in RESOURCE_SECTIONS:
    if resource_section in resource:
      resource[resource_section] = references.BindReferences(
          resource[resource_section], parent_name, all_names)

  config = {'resources': []}
  # Initialize layout with basic resource information.
  layout = {
      'name': resource['name'],
  }
  if env and ADD_LAYOUT_ID_KEY in env:
    layout['id'] = str(uuid.uuid4())
  # A resource has to have a type or action.
  type_or_action = None
  resource_type = resource.get('type')
  if 'type' in resource:
    type_or_action = layout['type'] = resource['type']
  elif 'action' in resource:
    type_or_action = layout['action'] = resource['action']
  else:
    raise ExpansionError(resource, 'Resource does not have type defined.')
  # Catalog types are considered types if present in the imports section.
  if ((composite_type_imports and resource_type in composite_type_imports) or
      (_IsTemplate(resource_type, path_overrides) and
       not _IsExternalTemplate(resource_type, imports, path_overrides))):
    # A template resource, which contains sub-resources.
    expanded_template = _ExpandTemplate(
        resource,
        imports,
        composite_type_imports,
        env,
        experiments,
        validate_schema,
        path_overrides=path_overrides,
        composite_type_context=composite_type_context)
    sub_names = []
    sub_parent_name = parent_name + resource['name']
    if expanded_template['resources']:
      sub_names = _ValidateUniqueNames(expanded_template['resources'],
                                       type_or_action)

      # If resource is a composite type, pass in a different set of imports
      # and path overrides.
      # Generate type URL from path or name
      scoped_imports = imports
      scoped_paths = path_overrides
      type_or_action = (resource.get('type') or resource.get('action'))
      composite_type_url = _TypeNameToUrl(type_or_action,
                                          composite_type_imports,
                                          path_overrides)
      if (experiments and
          experiments.enable_composite_type_imports_in_separate_lists and
          composite_type_url and composite_type_url in composite_type_imports):
        scoped_imports = composite_type_imports[composite_type_url]
        scoped_paths = composite_type_import_paths[composite_type_url]
        # Update our composite type context to point at the new url
        # This allows composite type and catalog entries to reference other
        # types in their config, and expansion will work
        composite_type_context = composite_type_url

      # Process all sub-resources of this template.
      for resource_to_process in expanded_template['resources']:
        processed_resource = _ProcessResource(
            resource_to_process,
            scoped_imports,
            composite_type_imports,
            composite_type_import_paths,
            env,
            sub_parent_name,
            sub_names,
            experiments,
            validate_schema,
            outputs,
            path_overrides=scoped_paths,
            composite_type_context=composite_type_context)

        # Append all sub-resources to the config resources, and the resulting
        # layout of sub-resources.
        config['resources'].extend(processed_resource['config']['resources'])

        # Lazy-initialize resources key here because it is not set for
        # non-template layouts.
        if 'resources' not in layout:
          layout['resources'] = []
        layout['resources'].append(processed_resource['layout'])

        if 'properties' in resource:
          layout['properties'] = resource['properties']

    # Process the expanded resources in the context of the template resource
    # that declared them.
    _ProcessTargetConfig(expanded_template, outputs, config, layout,
                         sub_parent_name, sub_names, experiments)

  else:
    if (_IsExternalTemplate(type_or_action, imports, path_overrides) and
        'properties' in resource):
      layout['properties'] = resource['properties']
    # A normal resource has only itself for config.
    config['resources'] = [resource]

  return {'config': config, 'layout': layout}


def _TypeNameToUrl(type_name, composite_type_imports, path_overrides):
  """Translates type name to a full DM URL if for a composite type.

  Args:
    type_name: the full type name as used in the template.
    composite_type_imports: separate imports map for each composite type, keyed
      by composite type URL.
    path_overrides: optional overrides from import name to path.

  Returns:
    The self link of the type if it is a composite type, else null.
  """
  # If it is already an URL from the packages available return this one
  if (type_name and composite_type_imports and
      type_name in composite_type_imports):
    return type_name
  if path_overrides and type_name in path_overrides:
    type_name = path_overrides[type_name]
  # Composite type overrides append .py or .jinja to indicate interpreter.
  # Remove that before constructing URL.
  if type_name.endswith('.py') or type_name.endswith('.jinja'):
    type_name = type_name.rsplit('.', 1)[0]
  composite_type_pattern = '^(.+)/composite:(.+)$'
  # Always use prod URL as identifier. Workflow does the same.
  full_url_pattern = (
      'https://deploymentmanager.googleapis.com/deploymentmanager/'
      'dogfood/projects/%s/global/compositeTypes/%s')
  composite_match = re.search(composite_type_pattern, type_name)
  if not composite_match:
    return None

  return full_url_pattern % (composite_match.group(1), composite_match.group(2))


def _ValidateUniqueNames(template_resources, template_name='config'):
  """Make sure that every resource name in the given template is unique."""
  names = set()
  for resource in template_resources:
    if 'name' in resource:
      if resource['name'] in names:
        raise ExpansionError(
            resource, 'Resource name \'%s\' is not unique in %s.' %
            (resource['name'], template_name))
      names.add(resource['name'])
    # If this resource doesn't have a name, we will report that error later.

    # Return the set of names for output/reference binding.
  return names


def _IsTemplate(resource_type, path_overrides):
  """Returns whether a given resource type is a Template."""
  if not resource_type:
    return False
  type_path = resource_type
  if path_overrides and resource_type in path_overrides:
    type_path = path_overrides[resource_type]
  return type_path.endswith('.py') or type_path.endswith('.jinja')


def _IsExternalTemplate(resource_type, imports, path_overrides):
  """Returns whether a resource type is an external template not in imports."""
  if not resource_type:
    return False
  return (((not imports) or (resource_type not in imports)) and
          _IsTemplate(resource_type, path_overrides))


def _BuildOutputMap(resource_objs, parent_name, all_names):
  """Given the layout of an expanded template, return map of its outputs.

  Args:
    resource_objs: List of resources, some of which might be templates and have
      outputs.
    parent_name: Name of the template whose outputs are being processed.
    all_names: Names of all resources declared by the parent.

  Returns:
    Map of template_name -> output_name -> output_value
  """
  output_map = {}

  for resource in resource_objs:
    if 'outputs' not in resource:
      continue
    output_value_map = {}
    for output_item in resource['outputs']:
      output_value_map[output_item['name']] = output_item['finalValue']
    # Bind references in outputs just like those in properties.
    bound_name = references.BindName(resource['name'], parent_name, all_names)
    output_map[bound_name] = output_value_map

  return output_map


def _ProcessTargetConfig(target, outputs, config, layout, parent_name,
                         all_names, experiments):
  """Resolves outputs in the output and properties section of the config.

  Args:
    target: Config that contains unprocessed output values
    outputs: Values to process
    config: Config object to update
    layout: Layout object to update
    parent_name: Name of the template resource that declared the target
    all_names: Names of all resources declared by that parent
    experiments: The experiments for this expansion run.
  """
  del experiments  # Unused
  output_map = None
  if 'resources' in layout:
    output_map = _BuildOutputMap(layout['resources'], parent_name, all_names)
  if outputs:
    if 'outputs' in target and target['outputs']:
      # Bind references in the outputs field before attempting to resolve them.
      target['outputs'] = references.BindReferences(target['outputs'],
                                                    parent_name, all_names)
      layout['outputs'] = _ResolveOutputs(target['outputs'], output_map)

    if 'resources' in config and config['resources']:
      config['resources'] = _ResolveResources(config['resources'], output_map)


def _ResolveOutputs(outputs, output_map):
  """Resolves references in the outputs.

  Args:
    outputs: List of name,value dicts.
    output_map: Result of _BuildOutputMap.

  Returns:
    Outputs with all references resolved and finalValue set.
  """
  for i in range(len(outputs)):
    # This is the initial case, the final value is identical to whatever value
    # the user put in their config.
    if 'finalValue' not in outputs[i]:
      outputs[i]['finalValue'] = outputs[i]['value']

    # Once we have the initial value, we resolve all references only in the
    # 'finalValue' field, but ignore the original 'value' field.
    if output_map:
      outputs[i]['finalValue'] = references.PopulateReferences(
          outputs[i]['finalValue'], output_map)

  return outputs


def _ResolveResources(resource_objs, output_map):
  """Resolves references in the name and properties block of a resource.

  Args:
    resource_objs: The properties block to resolve references in.
    output_map: Result of _BuildOutputMap.

  Returns:
    resource_objs with all of the references to outputs resolved.

  Raises:
    ExpansionReferenceError: if there were references to outputs that had bad
        paths.
  """
  if not output_map:
    return resource_objs

  for resource in resource_objs:
    for resource_section in RESOURCE_SECTIONS:
      if resource_section in resource:
        resource[resource_section] = references.PopulateReferences(
            resource[resource_section], output_map)

  return resource_objs


def _ExpandTemplate(resource,
                    imports,
                    composite_type_imports,
                    env,
                    experiments,
                    validate_schema=False,
                    path_overrides=None,
                    composite_type_context=None):
  """Expands a template, calling expansion mechanism based on type.

  Args:
    resource: resource object, the resource that contains parameters to the
      jinja file
    imports: map from string to string, the map of imported files names and
      contents
    composite_type_imports: separate imports map for each composite type, keyed
      by composite type URL.
    env: map from string to string, the map of environment variable names to
      their values
    experiments: Optional experiments that may affect expansion. If present will
      be a ExpansionExperiments proto.
    validate_schema: True to run schema validation; False otherwise
    path_overrides: Optional list of paths (ending in a template language
      extension) mapped to type names.
    composite_type_context: The current composite type or catalog context, used
      to decide which set of imports to use.

  Returns:
    The final expanded template

  Raises:
    ExpansionError: if there is any error occurred during expansion
  """
  source_file = resource['type']

  # Look for Template in imports.
  if source_file not in imports:
    raise ExpansionError(
        source_file,
        'Unable to find source file %s in imports.' % (source_file))

  resource['imports'] = imports

  # Populate the additional environment variables.
  if env is None:
    env = {}
  env['name'] = resource['name']
  env['type'] = resource['type']
  resource['env'] = env

  schema = source_file + '.schema'
  # If resource is a composite type, pass in a different set of imports
  # and path overrides.
  # Generate type URL from path or name
  composite_type_url = _TypeNameToUrl(resource['type'], composite_type_imports,
                                      path_overrides)
  if not composite_type_url:
    # If this resource itself isn't a composite type, we could still be in a
    # composite type import context, so set to provided type from upstream
    composite_type_url = composite_type_context
  scoped_imports = imports
  if (experiments and
      experiments.enable_composite_type_imports_in_separate_lists and
      composite_type_url and composite_type_url in composite_type_imports):
    # Redefine scoped imports as the source template and its local imports
    scoped_imports = composite_type_imports[composite_type_url]
    scoped_imports[source_file] = imports[source_file]
    if schema in imports:
      scoped_imports[schema] = imports[schema]

  if validate_schema and schema in scoped_imports:
    properties = resource['properties'] if 'properties' in resource else {}
    try:
      resource['properties'] = schema_validation.Validate(
          properties, schema, source_file, scoped_imports)
    except schema_validation.ValidationErrors as e:
      raise ExpansionError(resource['name'], e.message)

  type_path = source_file
  if path_overrides and source_file in path_overrides:
    type_path = path_overrides[source_file]
  if type_path.endswith('jinja'):
    expanded_template = _ExpandJinja(source_file, scoped_imports[source_file],
                                     resource, scoped_imports)
  elif type_path.endswith('py'):
    # This is a Python template.
    expanded_template = _ExpandPython(imports[source_file], source_file,
                                      resource, composite_type_url, experiments)
  else:
    # The source file is not a jinja file or a python file.
    # This in fact should never happen due to the _IsTemplate check above.
    raise ExpansionError(resource['source'],
                         'Unsupported source file: %s.' % (source_file))

  if isinstance(expanded_template, str):
    parsed_template = yaml.safe_load(expanded_template)
  elif isinstance(expanded_template, dict):
    parsed_template = expanded_template
  else:
    raise ExpansionError(
        resource['type'],
        'Python expansion must return dict, str or unicode type, '
        'but was \'%s\'' % (type(expanded_template).__name__))

  if not parsed_template or 'resources' not in parsed_template:
    raise ExpansionError(resource['type'],
                         'Template did not return a \'resources:\' field.')

  return parsed_template


def _FindMatchingLayoutResource(layout, resource_name, resource_type):
  """Find the matching leaf resource, if any, in the layout resource tree.

  Args:
    layout: yaml object with current layout
    resource_name: the resource name to match
    resource_type: the resource type to match

  Returns:
    The resource object from the layout, if a match is found, or None.
  """
  if 'resources' in layout:
    for layout_resource in layout['resources']:
      find_child_resource = _FindMatchingLayoutResourceHelper(
          layout_resource, resource_name, resource_type, 100)
      if find_child_resource:
        return find_child_resource
  return None


def _FindMatchingLayoutResourceHelper(layout_resource, resource_name,
                                      resource_type, remaining_depth):
  """Find the matching leaf resource, if any, in a layout resource subtree.

  Args:
    layout_resource: a yaml object with a resource from the layout resource list
    resource_name: the resource name to match
    resource_type: the resource type to match
    remaining_depth: the number of recursive calls allowed including this call

  Returns:
    The resource object from the layout, if a match is found, or None.
  """
  if not remaining_depth:  # Hit limit on recursion.
    return None
  if (layout_resource['name'] == resource_name and
      layout_resource['type'] == resource_type):
    return layout_resource
  if 'resources' not in layout_resource:
    return None
  for child_resource in layout_resource['resources']:
    child_match = _FindMatchingLayoutResourceHelper(child_resource,
                                                    resource_name,
                                                    resource_type,
                                                    remaining_depth - 1)
    if child_match:
      return child_match
  return None


def _ExpandJinja(file_name, source_template, resource, imports):
  """Render the jinja template using jinja libraries.

  Args:
    file_name: string, the file name.
    source_template: string, the content of jinja file to be render
    resource: resource object, the resource that contains parameters to the
      jinja file
    imports: map from string to string, the map of imported files names and
      contents

  Returns:
    The final expanded template
  Raises:
    ExpansionError in case we fail to expand the Jinja2 template.
  """

  try:
    # The standard jinja loader doesn't work in the sandbox as it calls
    # getmtime() and this system call is not supported.
    env = jinja2.Environment(loader=jinja2.DictLoader(imports))

    # pylint: disable=g-long-lambda
    env.filters['yaml'] = lambda x: yaml.dump(
        x, default_flow_style=False, Dumper=noalias_dumper)

    template = env.from_string(source_template)

    if ('properties' in resource or 'env' in resource or 'imports' in resource):
      return template.render(resource)
    else:
      return template.render()
  except Exception:
    st = 'Exception in %s\n%s' % (file_name, _FormatStacktrace())
    raise ExpansionError(file_name, st)


def _ExpandPython(python_source,
                  file_name,
                  params,
                  composite_type_url=None,
                  experiments=None):
  """Run python script to get the expanded template.

  Args:
    python_source: string, the python source file to run
    file_name: string, the name of the python source file
    params: object that contains 'imports' and 'params', the parameters to the
      python script
    composite_type_url: If the resource being expanded is a composite type, then
      the url that identifies that type. Else None.
    experiments: Optional experiments that may affect expansion. If present will
      be a ExpansionExperiments proto.

  Returns:
    The final expanded template. Return value can be either YAML string or
    the actual dictionary (latter preferred for performance reasons).
  """

  try:
    # Compile the python code to be run.
    constructor = {}
    if (experiments and
        experiments.enable_composite_type_imports_in_separate_lists):
      multiple_sandbox_loader.set_composite_type_url(composite_type_url)
    try:
      compiled_code = compile(python_source, file_name, 'exec')
      exec(compiled_code, constructor)  # pylint: disable=exec-used
    except Exception as e:  # pylint: disable=broad-except
      raise ExpansionError(file_name, 'Error compiling Python code: ' + str(e))

    # Construct the parameters to the python script.
    evaluation_context = PythonEvaluationContext(params)

    for m in TEMPLATE_METHODS:
      if m in constructor:
        return constructor[m](evaluation_context)
    raise ExpansionError(
        file_name,
        'Neither of template generation methods %s were found in the template.'
        % (', '.join(TEMPLATE_METHODS)))
  except (ExpansionError, MemoryError):
    # Re-raise memory and expansion exceptions.
    raise
  except IOError:
    # Convert IOError to ExpansionError with specific message.
    raise ExpansionError(file_name, 'I/O is not permitted in expansion')
  except ImportError as e:
    # The message itself is pretty explicit. No need to print stacktrace.
    raise ExpansionError(file_name, str(e))
  except Exception as e:  # pylint: disable=broad-except
    st = 'Exception in %s\n%s' % (file_name, _FormatStacktrace())
    raise ExpansionError(file_name, st)
  finally:
    if (experiments and
        experiments.enable_composite_type_imports_in_separate_lists):
      multiple_sandbox_loader.set_composite_type_url(None)


def _FormatStacktrace():
  """Formats stack trace by hiding Google3 code lines."""
  st = ''.join([
      i for i in traceback.format_exc().splitlines(True)  # pylint: disable=g-complex-comprehension
      if ('google3' not in i and 'compile(' not in i)
      # Skip the invocation of user code as well, even though there's no file
      # name involved.
      and ("constructor['GenerateConfig']" not in i)
  ])
  return st


class PythonEvaluationContext(object):
  """The python evaluation context.

  Attributes: params -- the parameters to be used in the expansion
  """

  def __init__(self, params):
    if 'properties' in params:
      self.properties = params['properties']
    else:
      self.properties = None

    if 'imports' in params:
      self.imports = params['imports']
    else:
      self.imports = None

    if 'env' in params:
      self.env = params['env']
    else:
      self.env = None


class ExpansionError(Exception):
  """Exception raised for errors during expansion process.

  Attributes:
    resource: the resource processed that results in the error
    message: the detailed message of the error
  """

  def __init__(self, resource, message):
    self.resource = resource
    self.message = message + ' Resource: ' + str(resource)
    super(ExpansionError, self).__init__(self.message)
