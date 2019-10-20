from abc import ABCMeta, abstractmethod

from src.config import Config
from src.parser import Token
from src.parser.keywords import format as format_keyword
from src.syntax_tree import SyntaxTree


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
                if token.kind == Token.KEYWORD:
                    token.word = format_keyword(token.word, keyword_style)
            cls._format(leaf, keyword_style)


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
                continue

            if idx < len(tree.leaves)-1:
                tree.leaves[idx+1].tokens.insert(0, leaf.tokens.pop(-1))
            elif leaf.leaves:
                leaf.leaves[0].tokens.insert(0, leaf.tokens.pop(-1))

            cls._format_head(leaf)

    @classmethod
    def _format_end(cls, tree: SyntaxTree):
        for idx, leaf in enumerate(tree.leaves):
            # ignores comma at zero indent because it may be with-comma
            if leaf.depth <= 1 or leaf.tokens[0].kind != Token.COMMA:
                return

            if idx > 0:
                tree.leaves[idx-1].tokens.insert(-1, leaf.tokens.pop(0))
            elif leaf.parent and leaf.parent.depth > 0:
                leaf.parent.tokens.insert(-1, leaf.tokens.pop(0))

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
            for idx, token in enumerate(leaf.tokens):
                # next of ( must not be WHITESPACE
                if token.kind in [Token.BRACKET_LEFT, Token.WHITESPACE]:
                    continue

                if idx >= len(leaf.tokens)-1:
                    continue

                next_tokens = leaf.tokens[idx+1]
                # previoues of comma or ) must not be WHITESPACE
                # user function maybe
                if (next_tokens.kind in [Token.COMMA, Token.BRACKET_RIGHT]) or \
                   (token.kind == Token.IDENTIFIER and next_tokens.kind == Token.BRACKET_LEFT):
                    continue

                whitespace = '  ' if next_tokens.kind == Token.COMMENT else ' '

                leaf.node.insert(idx+1, Token(word=whitespace, kind=Token.WHITESPACE))

            cls._format(leaf)


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

        rb_token = Token(word=')', kind=Token.BRACKET_RIGHT)
        with_token = Token(word='WITH', kind=Token.KEYWORD)
        comma_token = Token(word=',', kind=Token.COMMA)
        index = 0

        while True:
            # if reaches to end of leaves
            if len(tree.leaves) <= index:
                break

            leaf = tree.leaves[index]
            tokens = leaf.tokens

            try:
                if (tokens[0] == rb_token) or \
                   (tokens[0].kind == Token.IDENTIFIER) or \
                   (tokens[0] in [with_token, comma_token] and len(tokens) == 2):
                    tree.insert_leaf(index+1, SyntaxTree(depth=1, line_num=0))  # line num will be re-Numbered

            except IndexError:
                # tokens index out of range
                pass
            index += 1


