import re
from sre_parse import Pattern
from typing import List, Tuple

from . import pattern
from .token import Token


# TODO: Parses sql to Tree directory
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


def _tokenize_multi(text: str, kinds: List[str], ptn: Pattern) -> Tuple[str, List[Token]]:
    """TODO: Describes doc string """

    tokens: List[Token] = []

    match = re.match(ptn, text)
    if match:
        for idx, token_kind in enumerate(kinds):
            if len(match.group(idx+1)) > 0:
                tokens.append(Token(match.group(idx+1), token_kind))
            # tokens.append(Token(match.group(2), token))
            # if len(match.group(3)) > 0:
            #    tokens.append(Token(match.group(3), Token.WHITESPACE))

        return text[match.end():], tokens

    return text, []


def _tokenize_keyword(text: str, token: str, ptn: Pattern) -> Tuple[str, List[Token]]:
    """TODO: Describes doc string """

    tokens: List[Token] = []

    match = re.match(ptn, text)
    if match:
        if len(match.group(1)) > 0:
            tokens.append(Token(match.group(1), Token.WHITESPACE))
        tokens.append(Token(match.group(2), token))

        # spilit this pattern -> (\s+|\s*\(?\s*\*?|$)
        _, tks = _tokenize_multi(
            text=match.group(3),
            kinds=[Token.WHITESPACE, Token.BRACKET_LEFT, Token.WHITESPACE, Token.KEYWORD],
            ptn=re.compile(r'(\s*)(\(?)(\s*)(\*?)'))
        tokens.extend(tks)

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

    tokneizer_list_before_keyword = {
        pattern.COMMA: [Token.WHITESPACE, Token.COMMA, Token.WHITESPACE],
        pattern.DOT: [Token.WHITESPACE, Token.DOT, Token.KEYWORD, Token.WHITESPACE],
        pattern.BRACKET_LEFT: [Token.WHITESPACE, Token.BRACKET_LEFT, Token.WHITESPACE],
        pattern.BRACKET_RIGHT: [Token.WHITESPACE, Token.BRACKET_RIGHT, Token.WHITESPACE],
    }
    tokneizer_list_after_keyword = {
        pattern.OPERATOR: [Token.WHITESPACE, Token.OPERATOR, Token.WHITESPACE],
        pattern.QUOTES: [Token.WHITESPACE, Token.IDENTIFIER, Token.WHITESPACE],
        pattern.IDENTIFIER: [Token.WHITESPACE, Token.IDENTIFIER, Token.WHITESPACE]
    }

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

        # comma, dot, brackets
        is_matched = False
        for ptn, kinds in tokneizer_list_before_keyword.items():
            text, matches = _tokenize_multi(text, kinds=kinds, ptn=ptn)
            tokens.extend(matches)
            if matches:
                is_matched = True
                break
        if is_matched:
            continue

        # keywords
        text, matches = _tokenize_keyword(text, token=Token.KEYWORD, ptn=pattern.KEYWORDS)
        tokens.extend(matches)
        if matches:
            continue

        # functions
        # Some functions duplicated with keywords are recognized as "KEYWORD"
        text, matches = _tokenize_keyword(text, token=Token.FUNCTION, ptn=pattern.FUNCTIONS)
        tokens.extend(matches)
        if matches:
            continue

        # operators, quotes, identifier
        is_matched = False
        for ptn, kinds in tokneizer_list_after_keyword.items():
            text, matches = _tokenize_multi(text, kinds=kinds, ptn=ptn)
            tokens.extend(matches)
            if matches:
                is_matched = True
                break
        if is_matched:
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
