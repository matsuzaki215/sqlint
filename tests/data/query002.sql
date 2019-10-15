SELECT
    a
    , COUNT(b)
from
    test_table as t1
group by
    a
