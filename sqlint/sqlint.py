#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import logging
import os

# TODO: read setting file
from sqlint.config import (
    COMMA_POSITION_IS_END,
    KEYWORDS_IS_CAPITAL,
    INDENT_NUM
)
from sqlint.message import *
from sqlint.parser.parser import parse as parser_exec
from sqlint.parser.token import Token


def parse(stmt):
    """

    :param stmt:
    :return:
    """
    return parser_exec(stmt)


def check(stmt):
    """

    :param stmt:
    :return:
    """
    result = []

    # parse sql context
    parsed_tokens = parser_exec(stmt)

    blank_line_num = 0
    line_num = 1
    for tokens in parsed_tokens:
        # the position of a head of token in the line.
        position = 1
        # not suggest to break line as comma in bracket nest
        bracket_nest_count = 0

        # no tokens or only whitespace
        if (len(tokens) == 0 or
           (len(tokens) == 1 and tokens[0].kind == Token.WHITESPACE)):
            blank_line_num += 1
        else:
            if blank_line_num >= 2:
                result.append('(L{}, {}): {} ({})'.format(line_num, 0, 'too many blank lines', blank_line_num))
            blank_line_num = 0

        for i, token in enumerate(tokens):
            # debug
            # logger.debug('L{}:{}: {}'.format(line_num, position, token))

            if token.kind == Token.COMMENT:
                continue

            if token.word == '(':
                bracket_nest_count += 1
            if token.word == ')':
                bracket_nest_count -= 1

            # Check whether indent steps are N times.
            if i == 0:
                result.extend(_check_indent_spaces(line_num, position, token))
            # Check duplicated spaces except indents.
            if i != 0:
                result.extend(_check_duplicated_spaces(line_num, position, tokens, i))

            # Check whether reserved keywords is capital or not (default: not capital).
            result.extend(_check_capital_keyword(line_num, position, token))

            # Check whether comma, which connects some columns or conditions, is head(end) of line.
            if bracket_nest_count == 0:
                result.extend(_check_comma_position(line_num, position, tokens, i))

            # Check whether a whitespace exists after and not before comma.
            result.extend(_check_whitespace_comma(line_num, position, tokens, i))

            # Check whether a whitespace exists not before ) or after (
            result.extend(_check_whitespace_brackets(line_num, position, tokens, i))

            # Check whether a whitespace exist before and after binary operators
            # (e.g.) =, <, >, <=. >=. <>, !=, +, -, *, /, %
            result.extend(_check_whitespace_operators(line_num, position, tokens, i))

            # Check whether the table name is on the same line as join context
            result.extend(_check_join_table(line_num, position, tokens, i))

            # Check whether join context is [left outer join], [inner join] or [cross join]
            result.extend(_check_join_context(line_num, position, tokens, i))

            # Check whether break line at 'and', 'or', 'on' (except between A and B)
            if bracket_nest_count == 0:
                result.extend(_check_break_line(line_num, position, tokens, i))

            # TODO: Not Implemented yet.
            # join on での不等号の順番（親テーブル < 日付）
            # 予約語ごとに、適切なインデントがされているか
            # サブクエリは外に出す
            # エイリアスが予約語と一致していないか
            # Suggestion: 定数のハードコーディングをやめる

            position += len(token)

        line_num += 1

    if blank_line_num >= 2:
        result.append('(L{}, {}): {} ({})'.format(line_num, 0, 'too many blank lines', blank_line_num))

    return result


def _check_indent_spaces(line_num, pos, token):
    if token.kind != Token.WHITESPACE:
        return []

    if len(token) % INDENT_NUM != 0:
        return ['(L{}, {}): {} ({})'.format(line_num, pos, MESSAGE_INDENT_NUM.format(INDENT_NUM), len(token))]

    return []


def _check_duplicated_spaces(line_num, pos, tokens, token_index):
    """

    :param line_num:
    :param pos:
    :param tokens:
    :param token_index:
    :return:
    """

    token = tokens[token_index]

    if token.kind != Token.WHITESPACE or \
       (token_index+1 < len(tokens) and tokens[token_index+1].kind == Token.COMMENT):
        return []

    if len(token) >= 2:
        return ['(L{}, {}): {}'.format(line_num, pos, MESSAGE_DUPLICATED_SPACE)]

    return []


def _check_capital_keyword(line_num, pos, token):
    """

    :param line_num:
    :param pos:
    :param token:
    :return:
    """
    if token.kind != Token.KEYWORD:
        return []

    if KEYWORDS_IS_CAPITAL and token.word != token.word.upper():
        return ['(L{}, {}): {}: {} -> {}'.format(line_num, pos,
                                                 MESSAGE_KEYWORD_UPPER,
                                                 token.word,
                                                 token.word.upper())]
    if not KEYWORDS_IS_CAPITAL and token.word != token.word.lower():
        return ['(L{}, {}): {}: {} -> {}'.format(line_num, pos,
                                                 MESSAGE_KEYWORD_LOWER,
                                                 token.word,
                                                 token.word.lower())]

    return []


def _check_comma_position(line_num, pos, tokens, token_index):
    """

    :param line_num:
    :param pos:
    :param tokens:
    :param token_index:
    :return:
    """
    token = tokens[token_index]

    if token.kind != Token.COMMA:
        return []

    if COMMA_POSITION_IS_END and token_index <= len(token) - 2:
        for tk in tokens[token_index + 1:]:
            if tk.kind != Token.WHITESPACE and tk.kind != Token.COMMENT:
                return ['(L{}, {}): {}'.format(line_num, pos, MESSAGE_COMMA_END)]

    if not COMMA_POSITION_IS_END and not _is_first_token(tokens, token_index):
        return ['(L{}, {}): {}'.format(line_num, pos, MESSAGE_COMMA_HEAD)]

    return []


def _check_whitespace_comma(line_num, pos, tokens, token_index):
    """

    :param line_num:
    :param pos:
    :param tokens:
    :param token_index:
    :return:
    """
    token = tokens[token_index]

    if token.kind != Token.COMMA:
        return []

    result = []

    # after comma
    if token_index <= len(tokens) - 3 and tokens[token_index + 1].kind != Token.WHITESPACE:
        result.append('(L{}, {}): {}'.format(line_num, pos, MESSAGE_WHITESPACE_AFTER_COMMA))

    # before comma
    if token_index >= 2 and tokens[token_index - 1].kind == Token.WHITESPACE:
        result.append('(L{}, {}): {}'.format(line_num, pos, MESSAGE_WHITESPACE_BEFORE_COMMA))

    return result


def _check_whitespace_brackets(line_num, pos, tokens, token_index):
    """

    :param line_num:
    :param pos:
    :param tokens:
    :param token_index:
    :return:
    """
    token = tokens[token_index]

    if token.kind != Token.BRACKET:
        return []

    # after (
    if token.word == '(':
        if token_index <= len(tokens) - 3 and tokens[token_index + 1].kind == Token.WHITESPACE:
            return ['(L{}, {}): {}'.format(line_num, pos, MESSAGE_WHITESPACE_AFTER_BRACKET)]

    # before )
    if token.word == ')':
        if token_index >= 2 and tokens[token_index - 1].kind == Token.WHITESPACE:
            return ['(L{}, {}): {}'.format(line_num, pos, MESSAGE_WHITESPACE_BEFORE_BRACKET)]

    return []


def _check_whitespace_operators(line_num, pos, tokens, token_index):
    """
    :param line_num:
    :param pos:
    :param tokens:
    :param token_index:
    :return:
    """
    token = tokens[token_index]

    if token.kind != Token.OPERATOR:
        return []

    result = []

    # after ope
    if token_index <= len(tokens) - 2:
        next_token = tokens[token_index + 1]
        if next_token.kind != Token.WHITESPACE and next_token.kind != Token.COMMENT and next_token.word != ')':
            result.append('(L{}, {}): {}: {}'.format(line_num, pos, MESSAGE_WHITESPACE_AFTER_OPERATOR,
                                                     '{}{}'.format(token.word, next_token.word)))
    # before ope
    if token_index >= 1:
        pre_token = tokens[token_index - 1]
        if pre_token.kind != Token.WHITESPACE and pre_token.word != '(':
            result.append('(L{}, {}): {}: {}'.format(line_num, pos, MESSAGE_WHITESPACE_BEFORE_OPERATOR,
                                                     '{}{}'.format(pre_token.word, token.word)))

    return result


def _check_join_table(line_num, pos, tokens, token_index):
    """

    :param line_num:
    :param pos:
    :param tokens:
    :param token_index:
    :return:
    """
    token = tokens[token_index]

    if token.word.upper() != 'JOIN':
        return []

    if token_index <= len(tokens) - 2:
        for tk in tokens[token_index + 1:]:
            if tk.kind == Token.IDENTIFIER:
                return []

    return ['(L{}, {}): {}'.format(line_num, pos, MESSAGE_JOIN_TABLE)]


def _check_join_context(line_num, pos, tokens, token_index):
    """
    valid contexts
        [left outer join], [inner join] or [cross join]
    :param line_num:
    :param pos:
    :param tokens:
    :param token_index:
    :return:
    """
    token = tokens[token_index]

    if token.word.upper() != 'JOIN':
        return []

    # concat join contexts
    join_contexts = [token.word]
    for tk in reversed(tokens[:token_index]):
        if tk.kind == Token.WHITESPACE:
            continue

        if tk.word.upper() in ['INNER', 'OUTER', 'LEFT', 'RIGHT', 'CROSS']:
            join_contexts.insert(0, tk.word)
        else:
            break

    join_context_str = ' '.join(join_contexts)

    if join_context_str.upper() not in ['LEFT OUTER JOIN', 'INNER JOIN', 'CROSS JOIN']:
        return ['(L{}, {}): {}: {}'.format(line_num, pos, MESSAGE_JOIN_CONTEXT, join_context_str)]

    return []


def _check_break_line(line_num, pos, tokens, token_index):
    """
    break line at 'and', 'or', 'on' (except between A and B)
    :param line_num:
    :param pos:
    :param tokens:
    :param token_index:
    :return:
    """
    token = tokens[token_index]

    if token.word.upper() not in ['AND', 'OR', 'ON']:
        return []

    if _is_first_token(tokens, token_index):
        return []

    # if AND, search between context
    if token.word.upper() == 'AND':
        for tk in reversed(tokens[:token_index]):
            if tk.word.upper() == 'AND':
                break
            if tk.word.upper() == 'BETWEEN':
                return []

    return ['(L{}, {}): {}: {}'.format(line_num, pos, MESSAGE_BREAK_LINE, token.word)]


def _is_first_token(tokens, token_index):
    """

    :param tokens:
    :param token_index:
    :return:
    """

    if token_index == 0:
        return True

    for token in tokens[:token_index]:
        if token.kind != Token.WHITESPACE and token.kind != Token.COMMENT:
            return False

    return True
