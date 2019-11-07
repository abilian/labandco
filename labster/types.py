from __future__ import annotations

from typing import Any, Dict, List, Union

# TODO: this is still being worked out by the mypy team
JSON = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
JSONDict = Dict[str, JSON]
JSONList = List[JSON]
