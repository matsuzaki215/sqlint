#!/usr/bin/env python
# -*- coding: utf-8 -*-

# BigQuery reserved keywords
# https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical?hl=ja#reserved-keywords
RESERVED_KEYWORDS = [
    'ALL', 'AND', 'ANY', 'ARRAY', 'AS', 'ASC', 'ASSERT_ROWS_MODIFIED',
    'AT', 'BETWEEN', 'BY', 'CASE', 'CAST', 'COLLATE', 'CONTAINS', 'CREATE',
    'CROSS', 'CUBE', 'CURRENT', 'DEFAULT', 'DEFINE', 'DESC', 'DISTINCT',
    'ELSE', 'END', 'ENUM', 'ESCAPE', 'EXCEPT', 'EXCLUDE', 'EXISTS',
    'EXTRACT', 'FALSE', 'FETCH', 'FOLLOWING', 'FOR', 'FROM', 'FULL', 'GROUP',
    'GROUPING', 'GROUPS', 'HASH', 'HAVING', 'IF', 'IGNORE', 'IN', 'INNER',
    'INTERSECT', 'INTERVAL', 'INTO', 'IN', 'IS', 'JOIN', 'LATERAL', 'LEFT',
    'LIKE', 'LIMIT', 'LOOKUP', 'MERGE', 'NATURAL', 'NEW', 'NO', 'NOT',
    'NULL', 'NULLS', 'OF', 'ON', 'OR', 'ORDER', 'OUTER', 'OVER', 'PARTITION',
    'PRECEDING', 'PROTO', 'RANGE', 'RECURSIVE', 'RESPECT', 'RIGHT', 'ROLLUP',
    'ROWS', 'SELECT', 'SET', 'SOME', 'STRUCT', 'TABLESAMPLE', 'THEN', 'TO',
    'TREAT', 'TRUE', 'UNBOUNDED', 'UNION', 'UNNEST', 'USING', 'WHEN', 'WHERE',
    'WINDOW', 'WITH', 'WITHIN'
]

# BigQuery standard-sql functions
# https://cloud.google.com/bigquery/docs/reference/standard-sql/functions-and-operators?hl=ja
RESERVED_FUNCTIONS = [
    # aggregate-functions
    'ANY_VALUE', 'ARRAY_AGG', 'ARRAY_CONCAT_AGG', 'AVG', 'BIT_AND', 'BIT_OR', 'BIT_XOR',
    'COUNT', 'COUNTIF', 'LOGICAL_AND', 'LOGICAL_OR', 'MAX', 'MIN', 'STRING_AGG', 'SUM',
    # statistical-aggregate-functions
    'CORR', 'COVAR_POP', 'COVAR_SAMP', 'STDDEV_POP', 'STDDEV_SAMP', 'STDDEV', 'VAR_POP',
    'VAR_SAMP', 'VARIANCE',
    # approximate-aggregate-functions
    'APPROX_COUNT_DISTINCT', 'APPROX_QUANTILES', 'APPROX_TOP_COUNT', 'APPROX_TOP_SUM',
    # hyperloglog-functions
    # TODO: Not Suppored.
    # numbering-functions
    'RANK', 'DENSE_RANK', 'PERCENT_RANK', 'CUME_DIST', 'NTILE', 'ROW_NUMBER',
    # bit-functions
    'BIT_COUNT',
    # mathematical-functions
    'ABS', 'SIGN', 'IS_INF', 'IS_NAN', 'IEEE_DIVIDE', 'RAND', 'SQRT', 'POW', 'POWER',
    'EXP', 'LN', 'LOG', 'LOG10', 'GREATEST', 'LEAST', 'DIV', 'SAFE_DIVIDE', 'MOD',
    'ROUND', 'TRUNC', 'CEIL', 'CEILING', 'FLOOR', 'COS', 'COSH', 'ACOS', 'ACOSH',
    'SIN', 'SINH', 'ASIN', 'ASINH', 'TAN', 'TANH', 'ATAN', 'ATANH', 'ATAN2',
    # navigation-functions
    'FIRST_VALUE', 'LAST_VALUE', 'NTH_VALUE', 'LEAD', 'LAG', 'PERCENTILE_CONT', 'PERCENTILE_DISC',
    # hash-functions
    'FARM_FINGERPRINT', 'MD5', 'SHA1', 'SHA256', 'SHA512',
    # string-functions
    'BYTE_LENGTH', 'CHAR_LENGTH', 'CHARACTER_LENGTH', 'CODE_POINTS_TO_BYTES', 'CODE_POINTS_TO_STRING',
    'CONCAT', 'ENDS_WITH', 'FORMAT', 'FROM_BASE32', 'FROM_BASE64', 'FROM_HEX', 'LENGTH', 'LPAD',
    'LOWER', 'LTRIM', 'NORMALIZE', 'NORMALIZE_AND_CASEFOLD', 'REGEXP_CONTAINS', 'REGEXP_EXTRACT',
    'REGEXP_EXTRACT_ALL', 'REGEXP_REPLACE', 'REPLACE', 'REPEAT', 'REVERSE', 'RPAD', 'RTRIM',
    'SAFE_CONVERT_BYTES_TO_STRING', 'SPLIT', 'STARTS_WITH', 'STRPOS', 'SUBSTR', 'TO_BASE32',
    'TO_BASE64', 'TO_CODE_POINTS', 'TO_HEX', 'TRIM', 'UPPER',
    # json-functions
    'JSON_EXTRACT', 'JSON_EXTRACT_SCALAR', 'TO_JSON_STRING',
    # array-functions
    'ARRAY', 'ARRAY_CONCAT', 'ARRAY_LENGTH', 'ARRAY_TO_STRING', 'GENERATE_ARRAY', 'GENERATE_DATE_ARRAY',
    'GENERATE_TIMESTAMP_ARRAY', 'ARRAY_REVERSE', 'SAFE_OFFSET', 'SAFE_ORDINAL',
    # date-functions
    'CURRENT_DATE', 'EXTRACT', 'DATE', 'DATE_ADD', 'DATE_SUB', 'DATE_DIFF', 'DATE_TRUNC',
    'DATE_FROM_UNIX_DATE', 'FORMAT_DATE', 'PARSE_DATE', 'UNIX_DATE',
    # datetime-functions
    'CURRENT_DATETIME', 'DATETIME', 'DATETIME_ADD', 'DATETIME_SUB', 'DATETIME_DIFF', 'DATETIME_TRUNC',
    'FORMAT_DATETIME', 'PARSE_DATETIME',
    # time-functions
    'CURRENT_TIME', 'TIME', 'TIME_ADD', 'TIME_DIFF', 'TIME_TRUNC', 'FORMAT_TIME', 'PARSE_TIME',
    # timestamp-functions
    'CURRENT_TIMESTAMP', 'EXTRACT', 'STRING', 'TIMESTAMP', 'TIMESTAMP_ADD', 'TIMESTAMP_SUB',
    'TIMESTAMP_DIFF', 'TIMESTAMP_TRUNC', 'FORMAT_TIMESTAMP', 'PARSE_TIMESTAMP', 'TIMESTAMP_SECONDS',
    'TIMESTAMP_MILLIS', 'TIMESTAMP_MICROS', 'UNIX_SECONDS', 'UNIX_MILLIS', 'UNIX_MICROS',
    # security-functions
    'SESSION_USER'
    # net-functions
    # TODO: Not Supported.
]

BINARY_OPERATORS_ESCAPED = [
    '=', '<', '>', '!',
    '\+', '\-', '\*', '/', '%',
]
