from abc import ABCMeta, abstractmethod
from typing import Dict, List, Tuple

from src.checker import violation as vln
from src.checker.violation import Violation
from src.syntax_tree import SyntaxTree, Node
from src.parser import Token
from src.config import ConfigLoader


class Formatter(metaclass=ABCMeta):
    def __init__(self, violation: Violation):
        self.violation = violation

    @abstractmethod
    def format(self, config: ConfigLoader) -> SyntaxTree:
        pass


def get_formmater(violation: Violation) -> Formatter:
    if isinstance(violation, vln.IndentStepsViolation):
        return IndentStepsFormatter(violation)

    raise NotImplementedError(f'There is not Formmater class corresponding to {violation.__class__.__name__}')


class IndentStepsFormatter(Formatter):
    def __init__(self, violation: Violation):
        super().__init__(violation)

    def format(self, config: ConfigLoader):
        target = self.violation.tree
        token = target.node.tokens[0]

        if token.kind != Token.WHITESPACE:
            print(target.node)
            raise ValueError(f'fotmats indent steps to a token expected whitespace, but {token.kind }')

        indent = ' '*config.get('indent-steps')
        token.word = indent*(target.depth-1)
