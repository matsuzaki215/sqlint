from typing import List

from . import formatter as fmt
from src.checker import Violation
from src.syntax_tree import SyntaxTree
from src.config import ConfigLoader


def format(tree: SyntaxTree, config: ConfigLoader, violations: List[Violation]) -> SyntaxTree:
    """Formats syntax tree by checking violations

    Args:
        tree:
        config:
        violations:

    Returns:

    """

    for v in violations:
        try:
            fmt.get_formmater(v).format(config=config)
        except NotImplementedError as e:
            pass
    return tree
