# -*- coding: utf-8 -*-

from sqlint import sqlint
from sqlint import cli
from sqlint import config
from sqlint import message

__version__ = '0.0.0'

__all__ = [
    'sqlint'
]


def parse(stmt):
    """

    :param stmt:
    :return:
    """

    return sqlint.parse(stmt)


def check(stmt):
    """

    :param stmt:
    :return:
    """

    return sqlint.check(stmt)
