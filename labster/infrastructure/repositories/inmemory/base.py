from __future__ import annotations


class BaseInMemoryRepository:
    def __init__(self):
        self._data = {}
        self.is_dirty = False

    def clear(self):
        self._data.clear()
        self.is_dirty = True

    def is_empty(self):
        return len(self._data) == 0

    def get_state(self):
        return [self._data]

    def set_state(self, state):
        self._data = state[0]
