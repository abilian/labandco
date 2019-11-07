from __future__ import annotations

from typing import Dict

from labster.domain.services.constants import TYPES, get_constants

from . import route


@route("/constants")
def constants_json() -> Dict:
    constants = get_constants()
    constants["types"] = TYPES
    return constants
