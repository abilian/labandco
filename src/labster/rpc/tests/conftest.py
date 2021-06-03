from __future__ import annotations

from pytest import fixture

from labster.auth import AuthContext
from labster.di import injector
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.roles import RoleService


@fixture(scope="session")
def structure_repo():
    return injector.get(StructureRepository)


@fixture(scope="session")
def profile_repo():
    return injector.get(ProfileRepository)


@fixture(scope="session")
def role_service():
    return injector.get(RoleService)


@fixture(scope="session")
def auth_context():
    return injector.get(AuthContext)
