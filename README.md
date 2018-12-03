# bqlint
This is a SQL parser and linter for Standard SQL(BigQuery).

## Install

```
$ python setup.py install
```

if you use pyenv.

```
pyenv rehash
```

## Usage

Command line

```
$ bqlint query/*sql
```

Python module

```
$ python
>>> from bqlint import parse, check
>>> stmt = 'SELECT id From user_table  where user_table.age >10'
>>>
>>> parse(stmt)
[[<Keyword: 'SELECT'>, <Whitespace: ' '>, <Identifier: 'id'>, <Whitespace: ' '>, <Keyword: 'From'>, <Whitespace: ' '>, <Identifier: 'user_table'>, <Whitespace: '  '>, <Keyword: 'where'>, <Whitespace: ' '>, <Identifier: 'user_table.age'>, <Whitespace: ' '>, <Operator: '>'>, <Identifier: '10'>]]
>>>
>>> check(stmt)
['(L1, 1): reserved keywords in BQ must be lower case: SELECT -> select', '(L1, 11): reserved keywords in BQ must be lower case: From -> from', '(L1, 26): too many spaces', '(L1, 49): whitespace must be after binary operator: >10']
```

## Checking variations

check all following variations in default

- indent steps are N multiples.(default: N = 4)

- duplicated spaces.

- duplicated blank lines.

- reserved keywords in BigQuery is capital or not (default: not capital).

- comma is head(end) of the line which connect some columns or conditions. (default: head)


- white-spaces are not before ) or after (

- a whitespace is before and after binary operators
  - (e.g.) =, <, >, <=. >=. <>, !=, +, -, *, /, %

- the table name is at the same line as join context

- join context is [left outer join], [inner join] or [cross join]

- indent before 'on', 'or', 'and' (except between a and b)

## Futures
- table_name alias doesn't equal reserved functions for BigQuery.
- indent appropriately in reserved keywords for BigQuery.
- the order of conditions(x, y) at 'join on x = y'
- Optional: do not use sub-query
- Optional: do use hard-coding constant

## Sample

```
$ bqlint bqlint/tests/data/*
bqlint/tests/data/query001.sql:(L2, 6): comma must be head of line
bqlint/tests/data/query001.sql:(L7, 6): comma must be head of line
bqlint/tests/data/query002.sql:(L1, 1): reserved keywords in BQ must be lower case: SELECT -> select
bqlint/tests/data/query002.sql:(L3, 7): reserved keywords in BQ must be lower case: COUNT -> count
bqlint/tests/data/query003.sql:(L2, 1): indent steps must be 4 multiples (5)
bqlint/tests/data/query004.sql:(L5, 18): too many spaces
bqlint/tests/data/query005.sql:(L2, 7): whitespace must not be after bracket: (
bqlint/tests/data/query005.sql:(L2, 22): whitespace must not be before bracket: )
bqlint/tests/data/query006.sql:(L3, 8): whitespace must be after binary operator: +c
bqlint/tests/data/query006.sql:(L3, 8): whitespace must be after binary operator: b+
bqlint/tests/data/query007.sql:(L8, 16): table_name must be at the same line as join context
bqlint/tests/data/query008.sql:(L6, 5): join context must be [left outer join], [inner join] or [cross join]: join
bqlint/tests/data/query008.sql:(L10, 10): join context must be [left outer join], [inner join] or [cross join]: left join
bqlint/tests/data/query008.sql:(L14, 11): join context must be [left outer join], [inner join] or [cross join]: right join
bqlint/tests/data/query008.sql:(L16, 17): join context must be [left outer join], [inner join] or [cross join]: right outer join
bqlint/tests/data/query009.sql:(L6, 0): too many blank lines (2)
bqlint/tests/data/query009.sql:(L10, 0): too many blank lines (2)
bqlint/tests/data/query010.sql:(L6, 35): break line at 'and', 'or', 'on': on
bqlint/tests/data/query010.sql:(L11, 29): break line at 'and', 'or', 'on': and
bqlint/tests/data/query010.sql:(L12, 14): break line at 'and', 'or', 'on': or
```
