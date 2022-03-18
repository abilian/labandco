# TODO: this is still being worked out by the mypy team
from __future__ import annotations

from typing import Any, Sequence, Union

JSON = Union[str, int, float, bool, None, dict[str, Any], list[Any]]
JSONDict = dict[str, JSON]
JSONList = Sequence[JSON]
