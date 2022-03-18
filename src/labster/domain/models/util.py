from __future__ import annotations

from datetime import date
from typing import Any

import structlog

logger = structlog.get_logger()

SEP = ("-", "/")


def parse_date(dd: Any) -> date | None:
    if not dd:
        return None

    try:
        if dd[4] in SEP and dd[7] in SEP:
            year = int(dd[0:4])
            month = int(dd[5:7])
            day = int(dd[8:10])
            value = date(year, month, day)
            return value
        elif dd[2] in SEP and dd[5] in SEP:
            day = int(dd[0:2])
            month = int(dd[3:5])
            year = int(dd[6:10])
            value = date(year, month, day)
            return value
        else:
            return None
    except Exception:
        logger.exception(f"Can't parse date: {dd}")
        return None
