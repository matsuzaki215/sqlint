import logging
from typing import List, Tuple

from . import splitter as spt
from . import formatter as fmt
from sqlint.config import Config
from sqlint.parser import Token
from sqlint.syntax_tree import SyntaxTree

logger = logging.getLogger(__name__)


def format(tree: SyntaxTree, config: Config) -> SyntaxTree:
    """Formats syntax tree by checking violations

    Note: This is bang method.

    Args:
        tree: target SyntaxTree
        config:

    Returns:
        re-formatted tree
    """

    if not tree.is_abstract:
        raise ValueError('Failed to format, because target SyntaxTree is not Abstract')

    # create a tree having single leaf
    root: SyntaxTree = SyntaxTree(depth=0, line_num=0, is_abstract=True)
    leaf: SyntaxTree = SyntaxTree(
                        depth=1,
                        line_num=1,
                        tokens=_gather_tokens(tree),
                        parent=root,
                        is_abstract=True)
    root.add_leaf(leaf)

    # reshapes tree
    _reshape_tree(leaf, config)

    # for examples inserting indent or whitespaces, re-formating keyword and positioning comma, etc
    _format_tree(root, config)

    return root


def _gather_tokens(tree: SyntaxTree) -> List[Token]:
    """Gathers all tokens from all leaves

    Args:
        tree:

    Returns:
        list of tokens
    """

    tokens: List[Token] = tree.tokens
    for leaf in tree.leaves:
        children = _gather_tokens(leaf)
        tokens.extend(children)

    return tokens


def _reshape_tree(tree: SyntaxTree, config: Config):
    own, children, sibling = _split_tokens(tree)
    siblings = [sibling]

    # f own and own[0].word.lower() == 'date_diff':
    logger.debug(f'\033[32mown\033[0m = {own}')
    logger.debug(f'\033[32mchildren\033[0m = {children}')
    logger.debug(f'\033[32msibling\033[0m = {sibling}')

    tree.tokens = own

    # checks tokens(line) length
    tokens_and_spaces = fmt.WhiteSpacesFormatter.format_tokens(own)
    length = sum([len(tkn) for tkn in tokens_and_spaces]) + config.indent_steps*(tree.depth-1)
    max_length = config.max_line_length

    if length > max_length:
        _o, _c, _s = spt.LongLineSplitter.split(own, tree)
        """DEBUG
        if own and own[0].word.lower() == 'date_diff':
            logger.debug(f'    \033[92m_o\033[0m = {_o}')
            logger.debug(f'    \033[92m_c\033[0m = {_c}')
            logger.debug(f'    \033[92m_s\033[0m = {_s}')
        """
        tree.tokens = _o
        children = _c + children
        siblings.insert(0, _s)

    for chn in children:
        if chn:
            _tree: SyntaxTree = SyntaxTree(
                depth=tree.depth+1,
                line_num=0,
                tokens=chn,
                parent=tree,
                is_abstract=True)
            tree.add_leaf(_tree)
            _reshape_tree(_tree, config)

    for sbg in siblings:
        if sbg:
            _tree: SyntaxTree = SyntaxTree(
                depth=tree.depth,
                line_num=0,
                tokens=sbg,
                parent=tree.parent,
                is_abstract=True)
            tree.parent.add_leaf(_tree)
            _reshape_tree(_tree, config)


def _split_tokens(tree: SyntaxTree) -> Tuple[List[Token], List[List[Token]], List[Token]]:
    """

    Args:
        tree:

    Returns:

    """
    tokens = tree.tokens

    if not tokens:
        return [], [], []

    if tokens[0].kind in [Token.KEYWORD, Token.FUNCTION]:
        return spt.KeywordSplitter.split(tokens, tree)
    elif tokens[0].kind == Token.COMMA:
        return spt.CommaSplitter.split(tokens, tree)
    elif tokens[0].kind == Token.COMMENT:
        return tokens[0:1], [], tokens[1:]
    elif tokens[0].kind == Token.IDENTIFIER:
        return spt.IdentifierSplitter.split(tokens, tree)
    elif tokens[0].kind in [Token.BRACKET_LEFT, Token.OPERATOR]:
        return spt.Splitter.split_other(tokens)
    elif tokens[0].kind == Token.BRACKET_RIGHT:
        return spt.RightBrackerSplitter.split(tokens, tree)
    # ignores this case because this format method applies to abstract tree excluding whitespaces.
    # elif token.WHITESPACE:

    return tokens[0:1], [], tokens[1:]


def _format_tree(tree: SyntaxTree, config: Config):
    # formetter order is important
    formatter_list = [
        fmt.KeywordStyleFormatter,
        fmt.JoinFormatter,
        fmt.CommaPositionFormatter,
        fmt.IndentStepsFormatter,
        fmt.BlankLineFormatter,
        fmt.WhiteSpacesFormatter,
    ]

    for formatter in formatter_list:
        formatter.format(tree, config)
