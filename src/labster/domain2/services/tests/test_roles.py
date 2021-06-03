from __future__ import annotations

from sqlalchemy.orm import scoped_session

from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import Structure, StructureRepository
from labster.domain2.services.roles import Role, RoleService

profile_repo = injector.get(ProfileRepository)
structure_repo = injector.get(StructureRepository)
role_service = injector.get(RoleService)


def test_with_no_context(db_session: scoped_session):
    user = Profile()
    profile_repo.put(user)
    role_service.grant_role(user, Role.ADMIN_CENTRAL)
    assert role_service.has_role(user, Role.ADMIN_CENTRAL)
    assert role_service.get_users_with_role(Role.ADMIN_CENTRAL) == {user}

    role_service.clear()
    profile_repo.clear()


def test_with_context(db_session: scoped_session):
    user = Profile()
    profile_repo.put(user)

    structure = Structure()
    structure_repo.put(structure)

    role_service.grant_role(user, Role.ADMIN_LOCAL, structure)
    assert role_service.has_role(user, Role.ADMIN_LOCAL, structure)
    assert role_service.get_users_with_role(Role.ADMIN_LOCAL, structure) == {user}

    role_to_users = role_service.get_users_with_role_on(structure)
    assert len(role_to_users) == 1

    user1 = role_to_users[Role.ADMIN_LOCAL].pop()
    assert user1 == user

    roles_for_user = role_service.get_roles_for_user(user)
    assert len(roles_for_user) == 1
    assert roles_for_user[Role.ADMIN_LOCAL] == {structure}

    role_service.clear()
    profile_repo.clear()
