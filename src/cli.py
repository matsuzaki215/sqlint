import click
import logging
import os
from typing import Dict, List

from .checker import check as check_tree
from .checker import Violation
from .config import (
    DEFAULT_INI,
    ConfigLoader
)
from .formatter import format as format_tree
from .syntax_tree import SyntaxTree

# setting logger
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@click.command(context_settings={'ignore_unknown_options': True})
@click.argument('files', nargs=-1, type=click.Path())
@click.option('--config', '-c',
              default=DEFAULT_INI,
              type=click.Path(),
              help='Path to the config file that will be the authoritative config source.')
@click.option('--format', '-f', 'is_format', is_flag=True, help='Prints formatted sql and exist')
def main(files, config, is_format):
    """

    Args:
        files:
        config: path to the user config file.
        is_format: the flage whether outputs formatted sql

    Returns:

    """

    if len(files) == 0:
        # Todo: search *.sql file in current directory recursively.
        return

    cl = ConfigLoader(config)
    violations: Dict[str, List[Violation]] = {}
    trees: Dict[str, SyntaxTree] = {}
    # Checks violations in each files
    for f in files:
        if not os.path.exists(f):
            logger.warning(FileNotFoundError(f))

        if os.path.isdir(f):
            logger.warning(IsADirectoryError(f))

        with open(f, 'r') as fp:
            # constructs syntax tree
            trees[f] = SyntaxTree.stmtptree(fp.read())

            logger.debug(trees[f])

            # check violations
            violations[f] = check_tree(trees[f], cl)

    for file, v_list in violations.items():
        if is_format:
            format_tree(trees[file], cl, v_list)
            logger.info(trees[file].stmtftree())
        else:
            for v in v_list:
                logger.info('{} {}'.format(file, v.get_message()))


if __name__ == '__main__':
    main()
