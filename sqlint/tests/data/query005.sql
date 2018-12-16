select
    if( a > 10, 0, 1 ) as x
    , if(b < 10, 0, 1) as y
from
    test_table as t1
