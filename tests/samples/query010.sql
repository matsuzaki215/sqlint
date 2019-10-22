select
    a
    , b
from
    test_table as t1
    inner join test_table2 as tb2 on t1.a = tb2.a and t1.b = tb2.b
    inner join test_table3 as tb3
        using(c)
where
    a between 1 and 10
    and b between 10 and 20 and c = 10
    or d > 0 or e > 0
