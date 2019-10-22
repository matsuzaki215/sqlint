import click
import logging
import os
from typing import Dict

from .checker import check as check_tree
from .config import Config
from .formatter import format as format_tree
from .syntax_tree import SyntaxTree

# setting logger
logger = logging.getLogger(__name__)


@click.command(context_settings={'ignore_unknown_options': True})
@click.argument('files', nargs=-1, type=click.Path())
@click.option('--config', '-c', 'config_file',
              type=click.Path(),
              help='Path to the config file that will be the authoritative config source.')
@click.option('--format', '-f', 'is_format', is_flag=True, help='Prints formatted sql and exist')
def main(files, config_file, is_format):
    """

    Args:
        files:
        config_file: path to the user config file.
        is_format: the flage whether outputs formatted sql

    Returns:

    """

    if len(files) == 0:
        # Todo: search *.sql file in current directory recursively.
        return

    config = Config(config_file)
    trees: Dict[str, SyntaxTree] = {}
    # constructs syntax tree in each files
    for f in files:
        if not os.path.exists(f):
            logger.warning(f'file is not found: {f}')
            continue

        if os.path.isdir(f):
            logger.warning(f'{f} is a directory')
            continue

        with open(f, 'r') as fp:
            if is_format:
                # constructs syntax tree
                trees[f] = SyntaxTree.sqlptree(fp.read(), is_abstract=True)
            else:
                trees[f] = SyntaxTree.sqlptree(fp.read())

    for file, tree in trees.items():
        if is_format:
            formatted_tree = format_tree(tree, config)
            logger.info(formatted_tree.sqlftree())
        else:
            tree.sqlftree()
            for v in check_tree(tree, config):
                logger.info('{} {}'.format(file, v))


if __name__ == '__main__':
    main()
