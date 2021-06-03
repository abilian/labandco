# from __future__ import annotations
#
# from collections import defaultdict
# from typing import Any, Dict, Set, Tuple
#
# from injector import inject
#
# from labster.domain2.model.profile import Profile, ProfileId, ProfileRepository
# from labster.domain2.model.structure import Structure, StructureId, \
#     StructureRepository
# from labster.domain2.services.roles import Role, RoleService
#
#
# class InmemoryRoleService(RoleService):
#     grants: Set[Tuple[str, str, str]]
#     profile_repository: ProfileRepository
#     structure_repository: StructureRepository
#
#     @inject
#     def __init__(
#         self,
#         profile_repository: ProfileRepository,
#         structure_repository: StructureRepository,
#     ):
#         self.grants = set()
#         self.profile_repository = profile_repository
#         self.structure_repository = structure_repository
#
#     def get_state(self):
#         return [self.grants]
#
#     def set_state(self, state):
#         self.grants = state[0]
#
#     def is_empty(self):
#         return len(self.grants) == 0
#
#     def clear(self):
#         self.grants.clear()
#
#     def grant_role(self, user: Profile, role: Role, context: Any = None):
#         assert isinstance(user, Profile)
#         assert isinstance(role, Role)
#
#         if context:
#             entry = (user.id, role.name, context.id)
#         else:
#             entry = (user.id, role.name, None)
#         self.grants.add(entry)
#
#     def ungrant_role(self, user: Profile, role: Role, context: Any = None):
#         assert isinstance(user, Profile)
#         assert isinstance(role, Role)
#
#         if context:
#             entry = (user.id, role.name, context.id)
#         else:
#             entry = (user.id, role.name, None)
#         assert entry in self.grants
#         self.grants.remove(entry)
#
#     def has_role(self, user: Profile, role: Role, context: Any = None):
#         assert isinstance(user, Profile)
#         assert isinstance(role, Role)
#
#         if context:
#             return (user.id, role.name, context.id) in self.grants
#         else:
#             return (user.id, role.name, None) in self.grants
#
#     def get_users_with_role(self, role: Role, context: Any = None):
#         assert isinstance(role, Role)
#
#         if context:
#             must_match = (role.name, context.id)
#         else:
#             must_match = (role.name, None)
#         users = set()
#         for entry in self.grants:
#             user_id, role_name, context1_id = entry
#             if (role_name, context1_id) == must_match:
#                 user = self.profile_repository.get_by_id(ProfileId(user_id))
#                 users.add(user)
#
#         assert all(self.has_role(u, role, context) for u in users)
#         return users
#
#     def get_users_with_role_on(self, context: Structure) -> Dict[Role, Set[Profile]]:
#         result: Dict[Role, Set] = defaultdict(set)
#         for entry in self.grants:
#             user_id, role_name, context1_id = entry
#             if context1_id == context.id:
#                 user = self.profile_repository.get_by_id(ProfileId(user_id))
#                 role = getattr(Role, role_name)
#                 result[role].add(user)
#         return result
#
#     def get_users_with_given_role(self, role: Role, context: Structure):
#         assert isinstance(role, Role)
#
#         structures_id_to_match = {context.id}
#
#         users = set()
#         for entry in self.grants:
#             user_id, role_name, context1_id = entry
#             if role_name == role.name and context1_id in structures_id_to_match:
#                 user = self.profile_repository.get_by_id(ProfileId(user_id))
#                 users.add(user)
#
#         return users
#
#     def get_roles_for_user(self, user: Profile) -> Dict[Role, Set[Structure]]:
#         result: Dict[Role, Set[Structure]] = defaultdict(set)
#         for entry in self.grants:
#             user_id, role_name, context_id = entry
#             if user_id == user.id:
#                 context = self.structure_repository.get_by_id(StructureId(context_id))
#                 if not context:
#                     continue
#                 role = getattr(Role, role_name)
#                 result[role].add(context)
#
#         return result
from __future__ import annotations
