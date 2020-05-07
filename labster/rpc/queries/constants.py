from __future__ import annotations

from jsonrpcserver import method

from labster.domain2.services.constants import TYPES
from labster.domain2.services.constants import get_constants as _get_constants
from labster.types import JSONDict


@method
def get_constants() -> JSONDict:
    return {"values": _get_constants(), "types": TYPES}
