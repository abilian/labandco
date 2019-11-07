from __future__ import annotations


class Repository:
    def put(self, obj) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def is_empty(self) -> bool:
        raise NotImplementedError
