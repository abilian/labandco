# from __future__ import annotations
#
# from typing import Dict, List, Optional, Set, Tuple
#
# from injector import inject
#
# from labster.domain2.model.profile import Profile, ProfileId, ProfileRepository
# from labster.domain2.model.structure import Structure, StructureId, \
#     StructureRepository
# from labster.domain2.services.contacts import ContactService, ContactType
#
#
# class InmemoryContactService(ContactService):
#     edges: Set[Tuple[str, ContactType, str]]
#
#     @inject
#     def __init__(
#         self, profile_repo: ProfileRepository, structure_repo: StructureRepository,
#     ):
#         self.profile_repo = profile_repo
#         self.structure_repo = structure_repo
#         self.edges = set()
#
#     def get_state(self):
#         return [self.edges]
#
#     def set_state(self, state):
#         self.edges = state[0]
#
#     def is_empty(self):
#         return len(self.edges) == 0
#
#     def clear(self):
#         self.edges.clear()
#
#     def set_contact(
#         self, structure: Structure, contact_type: ContactType, user: Profile
#     ):
#         assert isinstance(structure, Structure)
#         assert isinstance(contact_type, ContactType)
#         assert isinstance(user, Profile)
#
#         if self.get_contact(structure, contact_type) == user:
#             return
#
#         self.delete_contact(structure, contact_type)
#         edge = (structure.id, contact_type, user.id)
#         self.edges.add(edge)
#
#     def delete_contact(self, structure: Structure, contact_type: ContactType):
#         assert isinstance(structure, Structure)
#         assert isinstance(contact_type, ContactType)
#
#         for edge in list(self.edges):
#             if (edge[0], edge[1]) == (structure.id, contact_type):
#                 self.edges.remove(edge)
#
#     def get_contact(
#         self, structure: Structure, contact_type: ContactType
#     ) -> Optional[Profile]:
#         for edge in self.edges:
#             if (structure.id, contact_type) != edge[0:2]:
#                 continue
#             user_id = edge[2]
#             user = self.profile_repo.get_by_id(ProfileId(user_id))
#             return user
#         return None
#
#     def get_mapping(self) -> Dict[Structure, Dict[ContactType, Profile]]:
#         result = {}
#         contact_types: List[ContactType] = list(ContactType)
#
#         structure_ids = {edge[0] for edge in self.edges}
#
#         structures = [
#             self.structure_repo.get_by_id(StructureId(structure_id))
#             for structure_id in structure_ids
#         ]
#         structures2: List[Structure] = [s for s in structures if s]
#         structures2.sort(key=lambda x: x.name)
#
#         for structure in structures2:
#             d: Dict[ContactType, Optional[Profile]] = {
#                 key: None for key in contact_types
#             }
#             for edge in self.edges:
#                 if edge[0] == structure.id:
#                     contact_type = edge[1]
#                     user = self.profile_repo.get_by_id(ProfileId(edge[2]))
#                     if user:
#                         d[contact_type] = user
#             result[structure] = d
#
#         return result
from __future__ import annotations
