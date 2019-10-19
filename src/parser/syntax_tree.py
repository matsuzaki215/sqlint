import logging
from typing import List, Optional

from .token import Token
from .parser import parse as parse_sql

logger = logging.getLogger(__name__)


class Node:
    def __init__(self, line_num: int, tokens: List[Token] = None):
        if tokens is None:
            tokens = []

        self.line_num = line_num
        self.tokens = tokens

    @property
    def line_num(self) -> int:
        return self._line_num

    @line_num.setter
    def line_num(self, value: int):
        if value < 0:
            raise ValueError(f'line_num must be ≧ 0, but {value}')
        self._line_num = value

    @property
    def tokens(self) -> List[Token]:
        return self._tokens

    @ tokens.setter
    def tokens(self, value):
        self._tokens = value

    @property
    def text(self):
        return ''.join([x.word for x in self.tokens])

    @property
    def indent(self):
        """Returns indent size

        If this is a blank line or whitespaces does not exist at head of line, returns 0.

        Returns:
            indent size
        """
        if len(self.tokens) == 0:
            return 0

        head = self.tokens[0]
        if head.kind == Token.WHITESPACE:
            return len(head)

        return 0

    def __len__(self):
        return len(self.tokens)

    def get_position(self, index: int):
        """Returns length of texts before Nth token.

        Args:
            index: the number of tokens

        Returns:
            length of texts
        """
        index = max(index, 0)
        return sum([len(token) for token in self.tokens[0: index]])+1

    def trip_kind(self, *args) -> 'Node':
        return self.ltrip_kind(*args).rtrip_kind(*args)

    def ltrip_kind(self, *args) -> 'Node':
        """

        Args:
            *args:

        Returns:

        """

        cut = -1
        for i in range(len(self.tokens)):
            for token_kind in args:
                if self.tokens[i].kind == token_kind:
                    cut = i
                    break
            if cut != i:
                break

        return Node(line_num=self.line_num, tokens=self.tokens[cut+1:])

    def rtrip_kind(self, *args) -> 'Node':
        """

        Args:
            *args:

        Returns:

        """

        cut = len(self.tokens)
        for i in reversed(range(len(self.tokens))):
            for token_kind in args:
                if self.tokens[i].kind == token_kind:
                    cut = i
                    break
            if cut != i:
                break

        return Node(line_num=self.line_num, tokens=self.tokens[0: cut])


class SyntaxTree:
    def __init__(self,
                 depth: int,
                 line_num: int,
                 tokens: List[Token] = None,
                 parent: Optional['SyntaxTree'] = None):
        """

        Args:
            depth: tree depth
            parent: parent tree node
            line_num: the number of line in source sql this tokens belongs to.
            tokens: a list of tokens which is tokenized sql statemnt.

        Returns:

        """

        self.depth: int = depth
        self.leaves: List[SyntaxTree] = list()
        self.parent: Optional['SyntaxTree'] = parent
        self.node: Node = Node(line_num=line_num, tokens=tokens)

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def parent(self) -> Optional['SyntaxTree']:
        return self._parent

    @property
    def leaves(self) -> List['SyntaxTree']:
        return self._leaves

    @property
    def node(self) -> Node:
        return self._node

    @property
    def tokens(self) -> List[Token]:
        return self._node.tokens

    @depth.setter
    def depth(self, value: int):
        if value < 0:
            raise ValueError(f'depth must be ≧ 0, but {value}')
        self._depth = value

    @parent.setter
    def parent(self, value: Optional['SyntaxTree']):
        self._parent = value

    @leaves.setter
    def leaves(self, value):
        self._leaves = value

    @node.setter
    def node(self, value: Node):
        self._node = value

    @property
    def text(self):
        return self.node.text

    @property
    def indent(self):
        """Returns indent size

        If this is a blank line or whitespaces does not exist at head of line, returns 0.

        Returns:
            indent size
        """

        return self.node.indent

    @classmethod
    def stmtptree(cls, stmt: str, sql_type: str = 'StandardSQL') -> 'SyntaxTree':
        """Returns SyntaxTree by parsing sql statement.

        Args:
            stmt: sql statemtnt
            sql_type: target sql type (StandardSQL only now)

        Returns:
            SyntaxTree instance
        """

        # TODO: deals with other sql type.
        if sql_type != 'StandardSQL':
            raise NotImplementedError(f'this linter can parses only "StandardSQL" right now, but {sql_type}')

        token_list: List[List[Token]] = parse_sql(stmt)

        # creates empty syntax tree as guard
        parent_vertex = SyntaxTree(depth=0, line_num=0)
        result = parent_vertex

        for line_num, tokens in enumerate(token_list):
            # DEBUG
            # print(tokens)
            indent = 0

            # if line is not blank, get indent size
            if len(tokens) > 0:
                head = tokens[0]
                if head.kind == Token.WHITESPACE:
                    indent = len(head.word)

            # check whether parent_node is root node
            while indent <= parent_vertex.indent and 0 < parent_vertex.depth:
                parent_vertex = parent_vertex.parent

            _tree = SyntaxTree(
                depth=parent_vertex.depth + 1,
                line_num=line_num + 1,
                tokens=tokens,
                parent=parent_vertex)
            parent_vertex.add_leaf(_tree)
            parent_vertex = _tree

        return result

    def stmtftree(self) -> str:
        """Returns sql statement

        Returns:
            sql stetement
        """
        return SyntaxTree._stmtftree(self)

    @staticmethod
    def _stmtftree(tree: 'SyntaxTree') -> str:
        """Returns sql statement

        Returns:
            sql statement
        """
        result = ''

        for leaf in tree.leaves:
            # TODO: get default indent from config file
            indent = '    '
            text = f'{indent * (leaf.depth - 1)}{leaf.text.lstrip()}'

            if len(result) == 0:
                result = text
            else:
                result = f'{result}\n{text}'

            appendix = SyntaxTree._stmtftree(leaf)
            if len(appendix) > 0:
                result = f'{result}\n{appendix}'

        return result

    def add_leaf(self, leaf: 'SyntaxTree'):
        self.leaves.append(leaf)

    def get_position(self, index: int):
        """Returns length of texts at head of Nth token.

        Args:
            index: the number of tokens

        Returns:
            length of texts
        """
        return self.node.get_position(index)
