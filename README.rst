=============
sqlint
=============

This is a SQL parser and linter for Standard SQL(BigQuery).

https://github.com/shigeru0215/sqlint

Install
=======

.. code::

    $ pip install sqlint

Usage
========

linting
--------

.. code::

    $ cat example.sql
    >> select
    >>    a + b as x
    >>    , b+c as y
    >> from
    >>    test_table as t1
    $ sqlint example.sql
    >> example.sql (L3, 8): whitespace must be before binary operator: b+
    >> example.sql (L3, 8): whitespace must be after binary operator: +c

formatting
-----------

With -f option, this linter show formatted SQL.

.. code::

    $ sqlint -f query/example.sql
    >> select
    >>    a + b as x
    >>    , b + c as y
    >> from
    >>    test_table as t1

REPL

.. code::

    $ python
    >>> from sqlint import parse, check, format
    >>> sql = 'SELECT id From user_table  where user_table.age >10'
    >>>
    >>> parse(sql)
    [[<Keyword: 'SELECT'>, <Whitespace: ' '>, <Identifier: 'id'>, <Whitespace: ' '>, <Keyword: 'From'>, <Whitespace: ' '>, <Identifier: 'user_table'>, <Whitespace: '  '>, <Keyword: 'where'>, <Whitespace: ' '>, <Identifier: 'user_table.age'>, <Whitespace: ' '>, <Operator: '>'>, <Identifier: '10'>]]
    >>>
    >>> check(sql)
    ['(L1, 1): reserved keywords must be lower case: SELECT -> select', '(L1, 11): reserved keywords must be lower case: From -> from', '(L1, 26): too many spaces', '(L1, 49): whitespace must be after binary operator: >10']
    >>>
    >>> format(sql)
    >>> select
    >>>     id
    >>> from
    >>>     user_table
    >>> where
    >>>     user_table.age > 10

