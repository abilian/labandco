# TODO: this is still being worked out by the mypy team
from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Union

JSON = Union[str, int, float, bool, None, dict[str, Any], list[Any]]
JSONDict = dict[str, JSON]
JSONList = Sequence[JSON]
