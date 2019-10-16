import click
import os
import logging

from .config.config_loader import (
    DEFAULT_INI,
    ConfigLoader
)

from typing import Dict, List

from .checker.violation import Violation
from .parser.syntax_tree import SyntaxTree
from .checker.tree import check as check_tree

# setting logger
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument('files', nargs=-1, type=click.Path())
@click.option('--config', '-c', default=DEFAULT_INI, type=click.Path())
def main(files, config):
    """

    Args:
        files:
        config:

    Returns:

    """

    if len(files) == 0:
        # Todo: print Usage
        return

    cl = ConfigLoader(config)

    violations: Dict[str, List[Violation]] = {}

    for f in files:
        if not os.path.exists(f):
            logger.warning(FileNotFoundError(f))

        if os.path.isdir(f):
            logger.warning(IsADirectoryError(f))

        # with open(f, 'r') as fp:
        #     for message in check(fp.read(), cl):
        #         logger.info('{}:{}'.format(f, message))

        with open(f, 'r') as fp:
            # constructs syntax tree
            tree = SyntaxTree(fp.read())
            # check violations
            violations[f] = check_tree(tree, cl)

    # TODO: branches result: (no option) print violations, (-f option) print formatted sql
    for file, v_list in violations.items():
        for v in v_list:
            logger.info('{} {}'.format(file, v.get_message()))


if __name__ == '__main__':
    main()
