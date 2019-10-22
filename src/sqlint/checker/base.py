from typing import List

from . import checker as chk
from .violation import Violation
from sqlint.syntax_tree import SyntaxTree
from sqlint.config import Config


def check(tree: SyntaxTree, config: Config) -> List[Violation]:
    """Checks syntax tree and returns error messages

    Args:
        tree:
        config:

    Returns:

    """

    violation_list: List[Violation] = []

    checker_list = [
        # Check whether indent steps are N times.
        chk.IndentStepsChecker,
        # Check whitespaces
        # 1. Check whether a whitespace exists after comma and not before .
        chk.WhitespaceChecker,
        # Check whether reserved keywords is capital or not (default: not capital).
        chk.KeywordStyleChecker,
        # Check whether comma, which connects some columns or conditions, is head(end) of line.
        chk.CommaChecker,
        # Check about join context
        chk.JoinChecker,
        # Check whether line-breaking before or after specified keywords.
        chk.LineChecker
    ]

    for checker in checker_list:
        violation_list.extend(checker.check(tree, config))

    return violation_list
