import re
from sre_parse import Pattern
from typing import List, Tuple

from . import pattern
from .token import Token


def parse(stmt: str) -> List[List[Token]]:
    """ Parses full sql statement to list of some tokens.

    Examples:
        sql :
    ----
    Select
        x
    from
        table_a
        join table_b
            on table_a.id = table_b.id
    ----

    parsed tokens:
    ----
    [
        [{Select}],
        [{    },{x}],
        [{from}],
        [{    },{table_a}],
        [{    },{join},{ },{table_b}],
        [{        },{on},{ },{table_a.id},{ },{=},{ },{table_b.id}]
    ]
    ----

    Args:
        stmt: sql statement

    Returns:
        parsed list of tokens list
    """

    # split per new line (\r\n, \r, \n)
    stmt_list: List[str] = []
    for lines in stmt.split('\r\n'):
        for line in lines.split('\n'):
            stmt_list.extend(line.split('\r'))

    result: List[List[Token]] = []
    is_comment_line = False
    for line in stmt_list:
        tokens, is_comment_line = _tokenize(line.rstrip('\r\n'), is_comment_line)
        result.append(tokens)

    return result


def _tokenize_comment_end(text: str) -> Tuple[str, List[Token], bool]:
    """TODO: Describes doc string """
    tokens: List[Token] = []

    match = re.search(pattern.COMMENT_END, text)
    if match:
        if len(match.group(1)) > 0:
            tokens.append(Token(match.group(1), Token.COMMENT))
        tokens.append(Token(match.group(2), Token.COMMENT))

        return text[match.end():], tokens, False

    return '', [Token(text, Token.COMMENT)], True


def _tokenize_comment_begin(text: str) -> Tuple[str, List[Token]]:
    """TODO: Describes doc string """

    tokens: List[Token] = []

    match = re.match(pattern.COMMENT_BEGIN, text)
    if match:
        if len(match.group(1)) > 0:
            tokens.append(Token(match.group(1), Token.WHITESPACE))
        tokens.append(Token(match.group(2), Token.COMMENT))

        return text[match.end():], tokens

    return text, []


def _tokenize_comment_single(text: str) -> Tuple[str, List[Token]]:
    """TODO: Describes doc string """

    tokens: List[Token] = []

    match = re.match(pattern.COMMENT_SINGLE, text)
    if match:
        if len(match.group(1)) > 0:
            tokens.append(Token(match.group(1), Token.WHITESPACE))
        tokens.append(Token(match.group(2), Token.COMMENT))

        return text[match.end():], tokens

    return text, []


def _tokenize_bilateral(text: str, token: str, ptn: Pattern) -> Tuple[str, List[Token]]:
    """TODO: Describes doc string """

    tokens: List[Token] = []

    match = re.match(ptn, text)
    if match:
        if len(match.group(1)) > 0:
            tokens.append(Token(match.group(1), Token.WHITESPACE))
        tokens.append(Token(match.group(2), token))
        if len(match.group(3)) > 0:
            tokens.append(Token(match.group(3), Token.WHITESPACE))

        return text[match.end():], tokens

    return text, []


def _tokenize_keyword(text: str, ptn: Pattern) -> Tuple[str, List[Token]]:
    """TODO: Describes doc string """

    tokens: List[Token] = []

    match = re.match(ptn, text)
    if match:
        if len(match.group(1)) > 0:
            tokens.append(Token(match.group(1), Token.WHITESPACE))
        tokens.append(Token(match.group(2), Token.KEYWORD))
        if match.group(3) == '(':
            tokens.append(Token(match.group(3), Token.BRACKET_LEFT))
        elif len(match.group(3)) > 0:
            tokens.append(Token(match.group(3), Token.WHITESPACE))

        return text[match.end():], tokens

    return text, []


def _tokenize(text: str, is_comment_line: bool = False) -> Tuple[List[Token], bool]:
    """Tokenizes one line of sql statement to some tokens.

    Args:
        text: sql statement
        is_comment_line: flag which this text is in multiline comments(/* */).

    Returns:
        tokens list
    """
    tokens: List[Token] = []

    # check multi-line comment : /* comment */
    while len(text) > 0:
        # comment end (*/)
        if is_comment_line:
            text, matches, is_comment_line = _tokenize_comment_end(text)
            tokens.extend(matches)
            continue

        # comment begin (/*)
        text, matches = _tokenize_comment_begin(text)
        tokens.extend(matches)
        if matches:
            is_comment_line = True
            continue

        # comment single(#, --)
        text, matches = _tokenize_comment_single(text)
        tokens.extend(matches)
        if matches:
            continue

        # comma
        text, matches = _tokenize_bilateral(text, token=Token.COMMA, ptn=pattern.COMMA)
        tokens.extend(matches)
        if matches:
            continue

        # bracket_left
        text, matches = _tokenize_bilateral(text, token=Token.BRACKET_LEFT, ptn=pattern.BRACKET_LEFT)
        tokens.extend(matches)
        if matches:
            continue

        # bracket_right
        text, matches = _tokenize_bilateral(text, token=Token.BRACKET_RIGHT, ptn=pattern.BRACKET_RIGHT)
        tokens.extend(matches)
        if matches:
            continue

        # keywords
        text, matches = _tokenize_keyword(text, ptn=pattern.KEYWORDS)
        tokens.extend(matches)
        if matches:
            continue

        # operator
        text, matches = _tokenize_bilateral(text, token=Token.OPERATOR, ptn=pattern.OPERATOR)
        tokens.extend(matches)
        if matches:
            continue

        # quotes: "hoge", 'fuga', `piyo`
        text, matches = _tokenize_bilateral(text, token=Token.IDENTIFIER, ptn=pattern.QUOTES)
        tokens.extend(matches)
        if matches:
            continue

        # identifier
        text, matches = _tokenize_bilateral(text, token=Token.IDENTIFIER, ptn=pattern.IDENTIFIER)
        tokens.extend(matches)
        if matches:
            continue

        # blank
        match = re.match(pattern.WHITESPACE, text)
        if match:
            if len(match.group(1)) > 0:
                tokens.append(Token(match.group(1), Token.WHITESPACE))
            text = text[match.end():]
            continue

        # TODO: raise parse Warning
        tokens.append(Token(text, Token.UNKNOWN))
        break

    return tokens, is_comment_line
