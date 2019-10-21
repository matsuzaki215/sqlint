select
    count(*)
    , test_table.*
    , (2 * 3) as x
from
    `test_table` as t1
