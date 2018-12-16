#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from sqlint.parser.config import (
    RESERVED_KEYWORDS,
    RESERVED_FUNCTIONS,
    BINARY_OPERATORS_ESCAPED,
)

# regex patterns
REGEX_COMMA = '(\s*)(,)(\s*)'
REGEX_BRACKET_LEFT = '(\s*)(\()(\s*)'
REGEX_BRACKET_RIGHT = '(\s*)(\))(\s*)'
REGEX_KEYWORD = '(\s*)({})(\(|\s+|$)'
REGEX_OPERATOR = '(\s*)([{}]+)(\s*)'
REGEX_COMMENT_SINGLE = '(\s*)(#.*)'
REGEX_COMMENT_BEGIN = '(\s*)(/\*)'
REGEX_COMMENT_END = '(.*?)(\*/)'
REGEX_QUOTES = '(\s*)("\S*"|\'\S*\'|`\S*`)(\s*)'
REGEX_IDENTIFIER = '(\s*)([^,\(\){}#\s]+)(\s*)'
REGEX_WHITESPACE = '(\s*)'

# temporary variable
binary_operators = ''.join(BINARY_OPERATORS_ESCAPED)

# compiled matching patterns
COMMA = re.compile(REGEX_COMMA)
BRACKET_LEFT = re.compile(REGEX_BRACKET_LEFT)
BRACKET_RIGHT = re.compile(REGEX_BRACKET_RIGHT)
KEYWORDS = []
for word in (set(RESERVED_KEYWORDS) | set(RESERVED_FUNCTIONS)):
    KEYWORDS.append(re.compile(REGEX_KEYWORD.format(word), re.IGNORECASE))
OPERATOR = re.compile(REGEX_OPERATOR.format(binary_operators))
COMMENT_SINGLE = re.compile(REGEX_COMMENT_SINGLE)
COMMENT_BEGIN = re.compile(REGEX_COMMENT_BEGIN)
COMMENT_END = re.compile(REGEX_COMMENT_END)
QUOTES = re.compile(REGEX_QUOTES)
IDENTIFIER = re.compile(REGEX_IDENTIFIER.format(binary_operators))
WHITESPACE = re.compile(REGEX_WHITESPACE)
