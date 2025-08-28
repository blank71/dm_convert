"""Conversion errors definitions."""


class UnsupportedFormatError(Exception):
  """Output format is not supported."""
  pass


class ConverterError(Exception):
  """Base error class for DM converter errors."""


class TemplateResolverError(Exception):
  """Base error class for template resolver."""


class LayoutParserError(Exception):
  """Base error class for layout parser."""


class PropertyParserError(Exception):
  """::Base error class for property parser."""


class CorruptedInputError(ConverterError):
  """Corruption found in input file."""
  pass


class UnsupportedReferenceError(ConverterError):
  """DM config reference not supported."""
  pass


class UnsupportedDependencyError(ConverterError):
  """DM Dependency resource not supported."""
  pass


class UnconvertableFieldError(ConverterError):
  """DM field not present in KRM."""
  pass


class ResourceTypeNotFoundError(ConverterError):
  """DM or Terraform resource type not found."""
  pass


class NoResourcesFoundError(ConverterError):
  """No resources found in input file."""
  pass


class InputFileNotFoundError(ConverterError):
  """Unable to open input file."""
  pass


class ReferencedResourceNotFoundError(ConverterError):
  """Resource in reference not found."""
  pass


class UnsupportedResourceTypeError(ConverterError):
  """Resource type is not supported."""
  pass


class InvalidResourceError(ConverterError):
  """Resource fields validation error."""
  pass


class ContainsActionError(ConverterError):
  """Resource is DM action."""
  pass


class BillingConfigMissingParentError(ConverterError):
  """Billing configuration must have parent project configuration."""
  pass


class UnsupportedActionStateError(ConverterError):
  """Resource has unsupported/invalid state for action."""
  pass


class ActionMissingRequiredResourceError(ConverterError):
  """Action is missing required reference."""
  pass


class InvalidTemplateResolverTypeError(TemplateResolverError):
  """An invalid/unsupported template type resolver.

  Only krm and tf types are supported.
  """
  pass


class TemplateResolverMissingContextError(TemplateResolverError):
  """Unable to resolve template due missing context."""
  pass


class AmbiguousOverrideRuleError(TemplateResolverError):
  """An ambiguous rule registration, indicates that type is present in templates.yaml file."""
  pass


class InvalidOverrideRuleError(TemplateResolverError):
  """Override rule is missing either target dm type or rule condition."""
  pass


class ExpansionFailedError(ConverterError):
  """Expansion failed."""
  pass


class InvalidLayoutError(LayoutParserError):
  """Layout is invalid."""


class InvalidQueryError(LayoutParserError):
  """The key does not exist."""


class InvalidReferenceError(PropertyParserError):
  """Unable to resolve reference."""


class InvalidInputsError(PropertyParserError):
  """Invalid inputs to property parser functions."""
