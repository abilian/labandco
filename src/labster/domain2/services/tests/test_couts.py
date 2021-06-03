from __future__ import annotations

import re
from decimal import Decimal

from labster.domain2.services.calculs_couts import sft

expected_table = """\
0	0
1	2.29
2	94.02
3	237.49
4	408.75
5	580.01
6	751.28
7	922.54
8	1093.8
9	1265.06
10	1436.32
"""


def test_sft() -> None:
    for s in expected_table.strip().split("\n"):
        t1, t2 = re.split(r"\s+", s)
        n = int(t1)
        expected = Decimal(t2)
        assert sft(600, n) == expected
