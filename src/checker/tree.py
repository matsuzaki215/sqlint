from typing import List

from . import base
from .violation import Violation
from src.parser.syntax_tree import SyntaxTree
from src.config.config_loader import ConfigLoader


def check(tree: SyntaxTree, config: ConfigLoader) -> List[Violation]:
    """Checks syntax tree and returns error messages

    Args:
        tree:
        config:

    Returns:

    """

    violation_list: List[Violation] = []

    checker_list = [
        # Check whether indent steps are N times.
        base.IndentStepsChecker,
        # Check whitespaces
        # 1. Check whether a whitespace exists after comma and not before .
        base.WhitespaceChecker,
        # Check whether reserved keywords is capital or not (default: not capital).
        base.KeywordStyleChecker,
        # Check whether comma, which connects some columns or conditions, is head(end) of line.
        base.CommaChecker,
        # Check about join context
        base.JoinChecker,
        # Check whether line-breaking before or after specified keywords.
        base.LineChecker
    ]

    for checker in checker_list:
        violation_list.extend(checker.check(tree, config))

    return violation_list
