# TODO: this is still being worked out by the mypy team
from __future__ import annotations

from typing import Any, Dict, List, Sequence, Union

JSON = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
JSONDict = Dict[str, JSON]
JSONList = Sequence[JSON]
