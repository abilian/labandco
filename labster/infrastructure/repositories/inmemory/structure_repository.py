from __future__ import annotations

from typing import Set

from labster.domain2.model.structure import Structure, StructureId, \
    StructureRepository

from .base import BaseInMemoryRepository


class InmemoryStructureRepository(BaseInMemoryRepository, StructureRepository):
    def put(self, structure: Structure):
        if not structure.id:
            structure.id = StructureId.new()
        self._data[structure.id] = structure

    def delete(self, structure: Structure):
        del self._data[structure.id]

    def get_by_id(self, id: StructureId) -> Structure:
        assert isinstance(id, StructureId)
        return self._data[id]

    def get_all(self) -> Set[Structure]:
        return set(self._data.values())
