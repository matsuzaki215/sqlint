select
    a
    , b
from
    test_table as t1
    left outer join join_table1 as jt1
        on t1.a = jt1.a
    left outer join
    join_table2 as jt2
        on t1.a = jt2.a
