from __future__ import annotations

from typing import Optional

from jsonrpcserver import method

from labster.types import JSONDict

from .registry import registry


@method
def get_context(name: str, params: Optional[JSONDict] = None) -> JSONDict:
    if params is None:
        params = {}
    if name in registry:
        return registry[name](**params)
    else:
        return {}
