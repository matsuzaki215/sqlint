import logging
from typing import List, Optional

from .token import Token
from .parser import parse

logger = logging.getLogger(__name__)


class Node:
    def __init__(self, depth: int, parent: Optional['Node'], contents: List[Token], line_num: int):
        self.depth: int = depth
        self.parent: Optional['Node'] = parent
        self.leaves: List[Node] = list()
        self.contents: List[Token] = contents
        self.line_num = line_num

    @property
    def depth(self) -> int:
        return self._depth

    @depth.setter
    def depth(self, value: int):
        if value < 0:
            raise ValueError(f'depth must be ≧ 0, but {value}')
        self._depth = value

    @property
    def line_num(self) -> int:
        return self._line_num

    @line_num.setter
    def line_num(self, value: int):
        if value < 0:
            raise ValueError(f'line_num must be ≧ 0, but {value}')
        self._line_num = value

    @property
    def parent(self) -> Optional['Node']:
        return self._parent

    @parent.setter
    def parent(self, value: Optional['Node']):
        self._parent = value

    @property
    def leaves(self) -> List['Node']:
        return self._leaves

    @leaves.setter
    def leaves(self, value):
        self._leaves = value

    @property
    def contents(self) -> List[Token]:
        return self._contents

    @contents.setter
    def contents(self, value):
        self._contents = value

    def add_leaf(self, leaf: 'Node'):
        self.leaves.append(leaf)

    def add_content(self, token: Token):
        self.contents.append(token)

    @property
    def text(self):
        return ''.join([x.word for x in self.contents])

    @property
    def indent(self):
        """Returns indent size

        If this is a blank line or whitespaces does not exist at head of line, returns 0.

        Returns:
            indent size
        """
        if len(self.contents) == 0:
            return 0

        head = self.contents[0]
        if head.kind == Token.WHITESPACE:
            return len(head)

        return 0

    def get_position(self, index: int):
        """Returns length of texts before Nth token.

        Args:
            index: the number of tokens

        Returns:
            length of texts
        """
        index = max(index, 0)
        return sum([len(token) for token in self.contents[0: index]])+1

    def trip_kind(self, *args) -> 'Node':
        return self.ltrip_kind(*args).rtrip_kind(*args)

    def ltrip_kind(self, *args) -> 'Node':
        """

        Args:
            *args:

        Returns:

        """

        cut = -1
        for i in range(len(self.contents)):
            for token_kind in args:
                if self.contents[i].kind == token_kind:
                    cut = i
                    break
            if cut != i:
                break

        return Node(
            depth=self.depth,
            parent=self.parent,
            contents=self.contents[cut+1:],
            line_num=self.line_num)

    def rtrip_kind(self, *args) -> 'Node':
        """

        Args:
            *args:

        Returns:

        """

        cut = len(self.contents)
        for i in reversed(range(len(self.contents))):
            for token_kind in args:
                if self.contents[i].kind == token_kind:
                    cut = i
                    break
            if cut != i:
                break

        return Node(
            depth=self.depth,
            parent=self.parent,
            contents=self.contents[0: cut],
            line_num=self.line_num)


class SyntaxTree:
    def __init__(self, stmt: str):
        """

        Args:
            stmt:
        """

        self.root: Node = Node(0, None, [], 0)
        self._parse(stmt)

    @property
    def root(self) -> Node:
        return self._root

    @root.setter
    def root(self, value: Node):
        self._root = value

    def _parse(self, stmt: str):
        """Parses sql statement

        Args:
            stmt:

        Returns:

        """

        token_list: List[List[Token]] = parse(stmt)

        # creates syntax tree
        parent_node: Node = self.root
        for line_num, tokens in enumerate(token_list):
            # DEBUG
            # print(tokens)

            indent = 0

            # if line is not blank, get indent size
            if len(tokens) > 0:
                head = tokens[0]
                if head.kind == Token.WHITESPACE:
                    indent = len(head.word)

            while indent <= parent_node.indent:
                # check whether parent_node is root node
                if parent_node.depth == 0:
                    break
                parent_node = parent_node.parent

            node = Node(
                depth=parent_node.depth+1,
                parent=parent_node,
                contents=tokens,
                line_num=line_num+1)
            parent_node.add_leaf(node)
            parent_node = node

    def stmtftree(self) -> str:
        """Returns SyntaxTree parsing sql statement

        Returns:

        """

        return self._stmtftree(self.root)

    def _stmtftree(self, node: Node) -> str:
        result = ''

        for leaf in node.leaves:
            token_str = ''.join([t.word for t in leaf.contents])
            # TODO: get default indent from config file
            text = f'{"    "*(leaf.depth-1)}{token_str}'

            if len(result) == 0:
                result = text
            else:
                result = f'{result}\n{text}'

            appendix = self._stmtftree(leaf)
            if len(appendix) > 0:
                result = f'{result}\n{appendix}'

        return result

    @staticmethod
    def stmtptree(stmt: str) -> 'SyntaxTree':
        """Returns sql statement re-structured SyntaxTree


        Args:
            stmt:

        Returns:

        """

        return SyntaxTree(stmt)
