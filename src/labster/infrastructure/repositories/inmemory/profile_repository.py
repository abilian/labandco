# from __future__ import annotations
#
# from typing import Set
#
# from labster.domain2.model.profile import Profile, ProfileId, ProfileRepository
#
# from .base import BaseInMemoryRepository
#
#
# class InmemoryProfileRepository(BaseInMemoryRepository, ProfileRepository):
#     def put(self, profile: Profile):
#         if not profile.id:
#             profile.id = ProfileId.new()
#         self._data[profile.id] = profile
#
#     def delete(self, profile: Profile):
#         del self._data[profile.id]
#
#     def get_all(self) -> Set[Profile]:
#         return set(self._data.values())
from __future__ import annotations
