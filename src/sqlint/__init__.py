import logging

from .syntax_tree import SyntaxTree
from .config import Config
from .parser import parse as parse_sql
from .checker import check as check_sql
from .formatter import format as format_sql

__version__ = '0.2.0'

__all__ = [
    'parse',
    'check',
    'format'
]

# setting logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def parse(sql: str):
    tokens_list = parse_sql(sql)
    logger.info(tokens_list)


def check(sql: str):
    tree = SyntaxTree.sqlptree(sql)
    for v in check_sql(tree, Config()):
        logger.info(v)


def format(sql: str):
    tree = SyntaxTree.sqlptree(sql, is_abstract=True)
    formatted_tree = format_sql(tree, Config())
    logger.info(formatted_tree.sqlftree())
