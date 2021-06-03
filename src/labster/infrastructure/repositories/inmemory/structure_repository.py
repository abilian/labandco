# from __future__ import annotations
#
# from typing import Set
# from uuid import uuid4
#
# from labster.domain2.model.structure import Structure, StructureRepository
#
# from .base import BaseInMemoryRepository
#
#
# class InmemoryStructureRepository(BaseInMemoryRepository, StructureRepository):
#     def put(self, structure: Structure):
#         if not structure.id:
#             structure.id = str(uuid4())
#         self._data[structure.id] = structure
#
#     def delete(self, structure: Structure):
#         del self._data[structure.id]
#
#     def get_by_id(self, id: str) -> Structure:
#         return self._data[id]
#
#     def get_all(self) -> Set[Structure]:
#         return set(self._data.values())
from __future__ import annotations
