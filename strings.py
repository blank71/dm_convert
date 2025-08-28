"""Helper string functions and classes."""

import re


class Pattern:
  """Contains constant re expressions."""
  UPPERCASE = re.compile(r'(?<!^)(?=[A-Z])')
  ASSET_TYPE = re.compile(r'(.*?)\..*\/(.*)')
  PLURALS = re.compile(r'(ie)?(sse)?(?<!s)s$')
  RECAPITALIZE = re.compile(
      r'(?<!^)(DNS|GCP|HTTPS|HTTP|IAM|KMS|SQL|SSL|TCP|URL|VPN)', re.IGNORECASE)
  # Ignore these words in asset types.
  TYPE_IGNORE = re.compile(r'(global|region|admin|cloud(?!=build))',
                           re.IGNORECASE)
  # Consider these one word for pascal to snake case purposes.
  SINGLE_WORDS = re.compile(
      r'(BigQuery|CloudBuild|DNS|GCP|HTTPS|HTTP|IAM|KMS|'
      r'PubSub|SQL|SSL|TCP|URL|VPN)', re.IGNORECASE)
  TYPED_REFERENCE_GROUPS = r'\$\(ref\.(?P<name>.+?)\.(?P<path>.+)\)'
  ARBITRARY_REFERENCE = ''.join(
      [r'(?P<prefix>.*)', TYPED_REFERENCE_GROUPS, r'(?P<suffix>.*)'])
  FIELD = r'(?P<field>.+)\[(?P<item_idx>\d+)\]'
  TERRAFORM_IDENTIFIER = re.compile(r'[^0-9A-Za-z_]')
  GCP_TYPES_ACTIONS = re.compile(
      r'gcp-types\/[A-Za-z]+\-[0-9A-Za-z]+\:[A-Za-z\.]+')
  LEGACY_TYPES = re.compile(r'[A-Za-z]+\.[0-9A-Za-z]+\.[A-Za-z\.]+')


def depluralize(noun: str) -> str:
  """Naive implementation of the singular version of the given plural noun."""

  # Examples:
  # copies -> copy
  # losses -> loss
  # items -> item
  def plural_repl(matchobj):
    if matchobj.group(1):
      return 'y'
    elif matchobj.group(2):
      return 'ss'
    return ''

  return re.sub(Pattern.PLURALS, plural_repl, noun)


def recapitalize(string: str) -> str:
  """Return the given string with abbreviations fully capitalized, unless they are at beginning of string."""
  upper_repl = lambda match: match.group().upper()
  return re.sub(Pattern.RECAPITALIZE, upper_repl, string)


def pascal_to_snake(string: str) -> str:
  """Convert the given pascal or camel case string to snake case."""
  capitalize_repl = lambda match: match.group().capitalize()
  single_words = re.sub(Pattern.SINGLE_WORDS, capitalize_repl, string)
  return re.sub(Pattern.UPPERCASE, '_', single_words).lower()


def uppercase_first(string: str) -> str:
  """Return the given string with first character set to uppercase."""
  return string[0].upper() + string[1:]


def tf_id_replace_invalid_char(string: str) -> str:
  """Verifies given string against Terrafrom identifier rules and replaces invalid characters with '_' if any."""
  return re.sub(Pattern.TERRAFORM_IDENTIFIER, '_', string)


def tf_resource_name_fix_starting(string: str) -> str:
  """Prepends an underscore to any invalid Terraform resource name not starting with letters or underscores."""
  return string if string[:1].isalpha() or string[:1] == '_' else f'_{string}'


def is_gcp_types_actions(string: str) -> bool:
  """Check if string is a DM GCP types/actions."""
  return bool(Pattern.GCP_TYPES_ACTIONS.match(string))


def is_legacy_types(string: str) -> bool:
  """Check if string is a DM legacy types."""
  return bool(Pattern.LEGACY_TYPES.match(string))
