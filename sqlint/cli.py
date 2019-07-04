#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import os
import logging

from sqlint.sqlint import check
from sqlint.config.config_loader import (
    DEFAULT_INI,
    ConfigLoader
)

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

    for f in files:
        if not os.path.exists(f):
            logger.warning(FileNotFoundError(f))

        if os.path.isdir(f):
            logger.warning(IsADirectoryError(f))

        with open(f, 'r') as fp:
            for message in check(fp.read(), cl):
                logger.info('{}:{}'.format(f, message))


if __name__ == '__main__':
    main()
