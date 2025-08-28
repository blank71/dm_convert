"""A parser for HCL2 implemented using the Lark parser."""

from hcl2.transformer import DictTransformer
from lark import Lark


PARSER = Lark.open(
    'hcl2.lark',
    rel_to=__file__,
    parser='lalr',
    lexer='basic',
    transformer=DictTransformer())
