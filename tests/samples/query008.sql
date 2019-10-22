select
    a
    , b
from
    test_table as t1
    join join_table1 as jt1
        on t1.a = jt1.a
    inner join join_table2 as jt2
        on t1.a = jt2.a
    left join join_table3 as jt3
        on t1.a = jt3.a
    left outer join join_table4 as jt4
        on t1.a = jt4.a
    right join join_table5 as jt5
        on t1.a = jt5.a
    right outer join join_table6 as jt6
        on t1.a = jt6.a
    full join join_table7 as jt7
        on t1.a = jt7.a
    full outer join join_table8 as jt8
        on t1.a = jt8.a
    cross join join_table9 as jt9
        on t1.a = jt9.a
