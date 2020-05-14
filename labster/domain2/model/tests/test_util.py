from __future__ import annotations

from datetime import date

from labster.domain2.model.util import parse_date


def test_parsedate() -> None:
    assert parse_date("2014/01/10") == date(2014, 1, 10)
    assert parse_date("2014-01-10") == date(2014, 1, 10)
    assert parse_date("10-01-2014") == date(2014, 1, 10)
    assert parse_date("10/01/2014") == date(2014, 1, 10)
