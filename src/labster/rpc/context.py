from __future__ import annotations

from jsonrpcserver import method

from labster.types import JSONDict

from .registry import registry


@method
def get_context(name: str, params: JSONDict | None = None, **kw) -> JSONDict:
    if params is None:
        params = {}

    if kw:
        params = kw

    if name in registry:
        return registry[name](**params)
    else:
        return {}
