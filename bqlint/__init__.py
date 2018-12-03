# -*- coding: utf-8 -*-

from bqlint import bqlint
from bqlint import cli
from bqlint import config
from bqlint import message

__version__ = '0.0.0'

__all__ = [
    'bqlint'
]


def parse(stmt):
    """

    :param stmt:
    :return:
    """

    return bqlint.parse(stmt)


def check(stmt):
    """

    :param stmt:
    :return:
    """

    return bqlint.check(stmt)
