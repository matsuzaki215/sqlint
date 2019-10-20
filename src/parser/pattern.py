import re

from .keywords import (
    RESERVED_KEYWORDS,
    RESERVED_FUNCTIONS,
    RESERVED_USER_FUNCTIONS,
    BINARY_OPERATORS_ESCAPED,
)

# regex patterns
REGEX_COMMA = r'(\s*)(,)(\s*)'
REGEX_BRACKET_LEFT = r'(\s*)(\()(\s*)'
REGEX_BRACKET_RIGHT = r'(\s*)(\))(\s*)'
REGEX_KEYWORD = r'(\s*)({})(\(|\s+|$)'
REGEX_OPERATOR = r'(\s*)([{}]+)(\s*)'
REGEX_COMMENT_SINGLE = r'(\s*)(#.*|--.*)'
REGEX_COMMENT_BEGIN = r'(\s*)(/\*)'
REGEX_COMMENT_END = r'(.*?)(\*/)'
REGEX_QUOTES = r'(\s*)("\S*"|\'\S*\'|`\S*`)(\s*)'
REGEX_IDENTIFIER = r'(\s*)([^,\(\){}#\s]+)(\s*)'
REGEX_WHITESPACE = r'(\s*)'

# temporary variable
binary_operators = ''.join(BINARY_OPERATORS_ESCAPED)

# compiled matching patterns
COMMA = re.compile(REGEX_COMMA)
BRACKET_LEFT = re.compile(REGEX_BRACKET_LEFT)
BRACKET_RIGHT = re.compile(REGEX_BRACKET_RIGHT)
unique_keywords = (set(RESERVED_KEYWORDS) | set(RESERVED_FUNCTIONS) | set(RESERVED_USER_FUNCTIONS))
KEYWORDS = re.compile(REGEX_KEYWORD.format('|'.join(unique_keywords)), re.IGNORECASE)
OPERATOR = re.compile(REGEX_OPERATOR.format(binary_operators))
COMMENT_SINGLE = re.compile(REGEX_COMMENT_SINGLE)
COMMENT_BEGIN = re.compile(REGEX_COMMENT_BEGIN)
COMMENT_END = re.compile(REGEX_COMMENT_END)
QUOTES = re.compile(REGEX_QUOTES)
IDENTIFIER = re.compile(REGEX_IDENTIFIER.format(binary_operators))
WHITESPACE = re.compile(REGEX_WHITESPACE)
