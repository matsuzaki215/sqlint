from typing import List, Tuple

from . import grouper as grp
from . import formatter as fmt
from src.syntax_tree import SyntaxTree
from src.parser import Token
from src.config import Config


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
    _reshape_tree(leaf)

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


def _reshape_tree(tree: SyntaxTree):
    parent, children, sibling = _split_tokens(tree)

    if len(parent) and parent[0].word.lower() == 'when':
        print('-'*10)
        print(f'parent = {parent}')
        print(f'children = {children}')
        print(f'sibling = {sibling}')
        print('-'*10)

    tree.tokens = parent

    if children:
        children_tree: SyntaxTree = SyntaxTree(
            depth=tree.depth+1,
            line_num=0,
            tokens=children,
            parent=tree,
            is_abstract=True)
        tree.add_leaf(children_tree)
        _reshape_tree(children_tree)

    if sibling:
        sibling_tree: SyntaxTree = SyntaxTree(
            depth=tree.depth,
            line_num=0,
            tokens=sibling,
            parent=tree.parent,
            is_abstract=True)
        tree.parent.add_leaf(sibling_tree)
        _reshape_tree(sibling_tree)

    return


def _split_tokens(tree: SyntaxTree) -> Tuple[List[Token], List[Token], List[Token]]:
    """

    Args:
        tree:

    Returns:

    """
    tokens = tree.tokens

    if not tokens:
        return [], [], []

    if tokens[0].kind == Token.KEYWORD:
        return grp.KeywordGrouper.group(tokens, tree)
    elif tokens[0].kind == Token.COMMA:
        return grp.CommaGrouper.group(tokens, tree)
    elif tokens[0].kind == Token.COMMENT:
        return tokens[0:1], [], tokens[1:]
    elif tokens[0].kind == Token.IDENTIFIER:
        return grp.IdentifierGrouper.group(tokens, tree)
    elif tokens[0].kind in [Token.BRACKET_LEFT, Token.OPERATOR]:
        return grp.Grouper.group_other(tokens)
    elif tokens[0].kind == Token.BRACKET_RIGHT:
        return grp.RightBrackerGrouper.group(tokens, tree)
    # ignores this case because this format method applies to abstract tree excluding whitespaces.
    # elif token.WHITESPACE:

    return tokens[0:1], [], tokens[1:]


def _format_tree(tree: SyntaxTree, config: Config):
    # formetter order is important
    formatter_list = [
        fmt.KeywordStyleFormatter,
        fmt.CommaPositionFormatter,
        fmt.IndentStepsFormatter,
        fmt.BlankLineFormatter,
        fmt.WhiteSpacesFormatter,
    ]

    for formatter in formatter_list:
        formatter.format(tree, config)
