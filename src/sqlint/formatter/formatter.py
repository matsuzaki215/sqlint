from abc import ABCMeta, abstractmethod
from typing import List

from sqlint.config import Config
from sqlint.parser import Token
from sqlint.parser.keywords import format as format_keyword
from sqlint.syntax_tree import SyntaxTree


class Formatter(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def format(cls, tree: SyntaxTree, config: Config):
        pass


class KeywordStyleFormatter(Formatter):
    @classmethod
    def format(cls, tree: SyntaxTree, config: Config):
        cls._format(tree, config.keyword_style)

    @classmethod
    def _format(cls, tree: SyntaxTree, keyword_style: str):
        for leaf in tree.leaves:
            for token in leaf.tokens:
                if token.kind in [Token.KEYWORD, Token.FUNCTION]:
                    token.word = format_keyword(token.word, keyword_style)
            cls._format(leaf, keyword_style)


class JoinFormatter(Formatter):
    join_token = Token(word='JOIN', kind=Token.KEYWORD)
    inner_token = Token(word='INNER', kind=Token.KEYWORD)
    outer_token = Token(word='OUTER', kind=Token.KEYWORD)
    left_token = Token(word='LEFT', kind=Token.KEYWORD)
    right_token = Token(word='RIGHT', kind=Token.KEYWORD)
    full_token = Token(word='FULL', kind=Token.KEYWORD)
    cross_token = Token(word='CROSS', kind=Token.KEYWORD)

    @classmethod
    def format(cls, tree: SyntaxTree, config: Config):
        cls._format(tree, config.keyword_style)

    @classmethod
    def _format(cls, tree: SyntaxTree, stlye: str):
        for leaf in tree.leaves:
            join_indexes = [i for i, tk in enumerate(leaf.tokens) if tk == cls.join_token]

            insert_count = 0
            for idx in join_indexes:
                adjusted_idx = idx + insert_count
                # checks previous 'JOIN'
                # When only 'JOIN' is exist, format as 'INNER JOIN'
                if adjusted_idx == 0:
                    leaf.tokens.insert(adjusted_idx, Token(word=format_keyword('INNER', stlye), kind=Token.KEYWORD))
                    insert_count += 1
                    continue

                prev_token = leaf.tokens[adjusted_idx-1]
                # valid case
                if prev_token in [cls.inner_token, cls.cross_token, cls.outer_token]:
                    # When prev_token is 'OUTER' and previous it is not LEFT, RIGHT or FULL,
                    # I can't determined to insert which of these, so I ignore this illegal case.
                    continue
                elif prev_token in [cls.left_token, cls.right_token, cls.full_token]:
                    # When 'LEFT JOIN', 'RIGHT JOIN' or 'FULL JOIN', format as 'XXX OUTER JOIN'
                    leaf.tokens.insert(adjusted_idx, Token(word=format_keyword('OUTER', stlye), kind=Token.KEYWORD))
                    insert_count += 1
                    continue

                # When only 'JOIN' is exist, format like 'INNER JOIN'
                leaf.tokens.insert(adjusted_idx, Token(word=format_keyword('INNER', stlye), kind=Token.KEYWORD))
                insert_count += 1

            cls._format(leaf, stlye)


class CommaPositionFormatter(Formatter):
    @classmethod
    def format(cls, tree: SyntaxTree, config: Config):
        if config.comma_position == 'head':
            cls._format_head(tree)
        else:  # comma_position == 'end':
            cls._format_end(tree)

    @classmethod
    def _format_head(cls, tree: SyntaxTree):
        for idx, leaf in enumerate(tree.leaves):
            if leaf.tokens[-1].kind != Token.COMMA:
                cls._format_head(leaf)
                continue

            # only comma in a line
            if len(leaf.tokens) == 1:
                continue

            if idx < len(tree.leaves)-1:
                tree.leaves[idx+1].tokens.insert(0, leaf.tokens.pop(-1))
            # elif leaf.leaves:
            #     leaf.leaves[0].tokens.insert(0, leaf.tokens.pop(-1))

            cls._format_head(leaf)

    @classmethod
    def _format_end(cls, tree: SyntaxTree):
        for idx, leaf in enumerate(tree.leaves):
            # ignores comma at zero indent because it may be with-comma
            if leaf.depth <= 1 or leaf.tokens[0].kind != Token.COMMA:
                cls._format_end(leaf)
                continue

            # only comma in a line
            if len(leaf.tokens) == 1:
                continue

            poped_token = leaf.tokens.pop(0)
            if idx > 0:
                tree.leaves[idx-1].tokens.insert(len(tree.leaves), poped_token)
            # elif leaf.parent and leaf.parent.depth > 0:
            #     leaf.parent.tokens.insert(len(tree.leaves), poped_token)

            cls._format_end(leaf)


class IndentStepsFormatter(Formatter):
    @classmethod
    def format(cls, tree: SyntaxTree, config: Config):
        cls._format(tree, config.indent_steps)

    @classmethod
    def _format(cls, tree: SyntaxTree, indent_steps: int):
        indent = ' ' * indent_steps

        for leaf in tree.leaves:
            tokens = leaf.tokens

            if tokens[0].kind == Token.WHITESPACE:
                leaf.tokens[0].word = indent*(leaf.depth-1)
            elif leaf.depth > 1:
                leaf.node.insert(0, Token(word=indent*(leaf.depth-1), kind=Token.WHITESPACE))

            cls._format(leaf, indent_steps)


class WhiteSpacesFormatter(Formatter):
    @classmethod
    def format(cls, tree: SyntaxTree, config: Config):
        cls._format(tree)

    @classmethod
    def _format(cls, tree: SyntaxTree):
        # ignores head of tokens because it is indent
        for leaf in tree.leaves:
            leaf.node.tokens = WhiteSpacesFormatter.format_tokens(leaf.tokens)

            cls._format(leaf)

    @staticmethod
    def format_tokens(tokens: List[Token]):
        result: List[Token] = []

        for idx, token in enumerate(tokens):
            result.append(token)

            # next of (, functions, or whitespaces must not be WHITESPACE
            if (token.kind in [Token.DOT, Token.BRACKET_LEFT, Token.WHITESPACE, Token.FUNCTION]) or \
               (idx >= len(tokens) - 1):
                continue

            next_tokens = tokens[idx + 1]
            # previoues of comma or ) must not be WHITESPACE
            # user function maybe
            if (next_tokens.kind in [Token.COMMA, Token.DOT, Token.BRACKET_RIGHT]) or \
               (token.kind == Token.IDENTIFIER and next_tokens.kind == Token.BRACKET_LEFT):
                continue

            whitespace = '  ' if next_tokens.kind == Token.COMMENT else ' '
            result.append(Token(word=whitespace, kind=Token.WHITESPACE))

        return result


# TODO: keep Idempotency
class BlankLineFormatter(Formatter):
    """"""
    @classmethod
    def format(cls, tree: SyntaxTree, config: Config):
        cls._format(tree)

    @classmethod
    def _format(cls, tree: SyntaxTree):
        """Inserts a blank line after specified leaf """

        # insert blank at only root depth
        if tree.depth != 0:
            return

        with_token = Token(word='WITH', kind=Token.KEYWORD)
        comma_token = Token(word=',', kind=Token.COMMA)
        index = 0

        while True:
            # if reaches to end of leaves
            if len(tree.leaves)-1 <= index:
                tree.insert_leaf(index + 1, SyntaxTree(depth=1, line_num=0))
                break

            leaf = tree.leaves[index]
            tokens = leaf.tokens

            try:
                if (tokens[0].kind == Token.BRACKET_RIGHT) or \
                   (tokens[0].kind == Token.IDENTIFIER) or \
                   (tokens[0] in [with_token, comma_token] and len(tokens) == 2):
                    tree.insert_leaf(index+1, SyntaxTree(depth=1, line_num=0))

            except IndexError:
                # tokens index out of range
                pass
            index += 1
