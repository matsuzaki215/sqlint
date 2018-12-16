sqlint
=============

https://github.com/shigeru0215/sqlint'

Install
-------

.. code::

    $ pip install sqlint

Usage
-----

Command line

.. code::

    $ sqlint query/*sql

Python module

.. code::

    $ python
    >>> from sqlint import parse, check
    >>> stmt = 'SELECT id From user_table  where user_table.age >10'
    >>>
    >>> parse(stmt)
    [[<Keyword: 'SELECT'>, <Whitespace: ' '>, <Identifier: 'id'>, <Whitespace: ' '>, <Keyword: 'From'>, <Whitespace: ' '>, <Identifier: 'user_table'>, <Whitespace: '  '>, <Keyword: 'where'>, <Whitespace: ' '>, <Identifier: 'user_table.age'>, <Whitespace: ' '>, <Operator: '>'>, <Identifier: '10'>]]
    >>>
    >>> check(stmt)
    ['(L1, 1): reserved keywords must be lower case: SELECT -> select', '(L1, 11): reserved keywords must be lower case: From -> from', '(L1, 26): too many spaces', '(L1, 49): whitespace must be after binary operator: >10']
