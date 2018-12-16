#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os

from sqlint.parser.token import Token
from sqlint.parser import pattern


def parse(stmt):
    """

    :param stmt:
    :return:
    """

    # split per new line (\r\n, \r, \n)
    stmt_list = []
    for lines in stmt.split('\r\n'):
        for line in lines.split('\n'):
            stmt_list.extend(line.split('\r'))

    result = []
    is_comment_line = False
    for line in stmt_list:
        tokens, is_comment_line = _tokenize(line.rstrip('\r\n'), is_comment_line)
        result.append(tokens)

    return result


def _tokenize(text, is_comment_line=False):
    """

    :param text:
    :param is_comment_line:
    :return:
    """
    tokens = []

    # check multi-line comment : /* comment */
    while len(text) > 0:
        # comment end (*/)
        if is_comment_line:
            match = re.search(pattern.COMMENT_END, text)
            if match:
                if len(match.group(1)) > 0:
                    tokens.append(Token(match.group(1), Token.COMMENT))
                tokens.append(Token(match.group(2), Token.COMMENT))
                text = text[match.end():]
                is_comment_line = False
                continue
            else:
                tokens.append(Token(text, Token.COMMENT))
                break

        # comment begin (/*)
        match = re.match(pattern.COMMENT_BEGIN, text)
        if match:
            if len(match.group(1)) > 0:
                tokens.append(Token(match.group(1), Token.WHITESPACE))
            tokens.append(Token(match.group(2), Token.COMMENT))
            text = text[match.end():]
            is_comment_line = True
            continue

        # comment single(#)
        match = re.match(pattern.COMMENT_SINGLE, text)
        if match:
            if len(match.group(1)) > 0:
                tokens.append(Token(match.group(1), Token.WHITESPACE))
            tokens.append(Token(match.group(2), Token.COMMENT))
            text = text[match.end():]
            continue

        # comma
        match = re.match(pattern.COMMA, text)
        if match:
            if len(match.group(1)) > 0:
                tokens.append(Token(match.group(1), Token.WHITESPACE))
            tokens.append(Token(match.group(2), Token.COMMA))
            if len(match.group(3)) > 0:
                tokens.append(Token(match.group(3), Token.WHITESPACE))
            text = text[match.end():]
            continue

        # bracket_left
        match = re.match(pattern.BRACKET_LEFT, text)
        if match:
            if len(match.group(1)) > 0:
                tokens.append(Token(match.group(1), Token.WHITESPACE))
            tokens.append(Token(match.group(2), Token.BRACKET))
            if len(match.group(3)) > 0:
                tokens.append(Token(match.group(3), Token.WHITESPACE))
            text = text[match.end():]
            continue

        # bracket_right
        match = re.match(pattern.BRACKET_RIGHT, text)
        if match:
            if len(match.group(1)) > 0:
                tokens.append(Token(match.group(1), Token.WHITESPACE))
            tokens.append(Token(match.group(2), Token.BRACKET))
            if len(match.group(3)) > 0:
                tokens.append(Token(match.group(3), Token.WHITESPACE))
            text = text[match.end():]
            continue

        # keywords
        for regex in pattern.KEYWORDS:
            match = re.match(regex, text)
            if match:
                break
        if match:
            if len(match.group(1)) > 0:
                tokens.append(Token(match.group(1), Token.WHITESPACE))
            tokens.append(Token(match.group(2), Token.KEYWORD))
            if match.group(3) == '(':
                tokens.append(Token(match.group(3), Token.BRACKET))
            elif len(match.group(3)) > 0:
                tokens.append(Token(match.group(3), Token.WHITESPACE))
            text = text[match.end():]
            continue

        # operator
        match = re.match(pattern.OPERATOR, text)
        if match:
            if len(match.group(1)) > 0:
                tokens.append(Token(match.group(1), Token.WHITESPACE))
            tokens.append(Token(match.group(2), Token.OPERATOR))
            if len(match.group(3)) > 0:
                tokens.append(Token(match.group(3), Token.WHITESPACE))
            text = text[match.end():]
            continue

        # quotes (as identifier )
        match = re.match(pattern.QUOTES, text)
        if match:
            if len(match.group(1)) > 0:
                tokens.append(Token(match.group(1), Token.WHITESPACE))
            tokens.append(Token(match.group(2), Token.IDENTIFIER))
            if len(match.group(3)) > 0:
                tokens.append(Token(match.group(3), Token.WHITESPACE))
            text = text[match.end():]
            continue

        # identifier
        match = re.match(pattern.IDENTIFIER, text)
        if match:
            if len(match.group(1)) > 0:
                tokens.append(Token(match.group(1), Token.WHITESPACE))
            tokens.append(Token(match.group(2), Token.IDENTIFIER))
            if len(match.group(3)) > 0:
                tokens.append(Token(match.group(3), Token.WHITESPACE))
            text = text[match.end():]
            continue

        # blank
        match = re.match(pattern.WHITESPACE, text)
        if match:
            if len(match.group(1)) > 0:
                tokens.append(Token(match.group(1), Token.WHITESPACE))
            text = text[match.end():]
            continue

    return tokens, is_comment_line
