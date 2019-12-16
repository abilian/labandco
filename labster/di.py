from __future__ import annotations

import sys

from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from injector import Injector, singleton
from sqlalchemy.orm import Session

from labster.auth import AuthContext
from labster.domain2.model.demande import DemandeRepository
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.contacts import ContactService
from labster.domain2.services.roles import RoleService
from labster.extensions import db, mail
from labster.infrastructure.repositories.inmemory import InmemoryProfileRepository, \
    InmemoryStructureRepository
from labster.infrastructure.repositories.sqla import SqlaProfileRepository
from labster.infrastructure.repositories.sqla.demande_repository import \
    SqlaDemandeRepository
from labster.infrastructure.repositories.sqla.mappers import Mapper
from labster.infrastructure.repositories.sqla.structure_repository import \
    SqlaStructureRepository
from labster.infrastructure.services.inmemory.contacts import \
    InmemoryContactService
from labster.infrastructure.services.inmemory.roles import InmemoryRoleService
from labster.infrastructure.services.sqla.contacts import SqlaContactService
from labster.infrastructure.services.sqla.roles import SqlaRoleService
from labster.persistence import NoPersistence, Persistence, SqlaPersistence


def configure_for_prod(binder):
    binder.bind(ProfileRepository, to=SqlaProfileRepository, scope=singleton)
    binder.bind(StructureRepository, to=SqlaStructureRepository, scope=singleton)
    binder.bind(RoleService, to=SqlaRoleService, scope=singleton)
    binder.bind(ContactService, to=SqlaContactService, scope=singleton)
    binder.bind(DemandeRepository, to=SqlaDemandeRepository, scope=singleton)

    binder.bind(Persistence, to=SqlaPersistence, scope=singleton)
    binder.bind(SQLAlchemy, to=db, scope=singleton)
    binder.bind(Mapper, scope=singleton)


def configure_for_testing(binder):
    binder.bind(ProfileRepository, to=InmemoryProfileRepository, scope=singleton)
    binder.bind(StructureRepository, to=InmemoryStructureRepository, scope=singleton)
    binder.bind(RoleService, to=InmemoryRoleService, scope=singleton)
    binder.bind(ContactService, to=InmemoryContactService, scope=singleton)

    binder.bind(DemandeRepository, to=SqlaDemandeRepository, scope=singleton)

    binder.bind(Persistence, to=NoPersistence, scope=singleton)
    binder.bind(SQLAlchemy, to=db, scope=singleton)
    binder.bind(Mapper, scope=singleton)
    binder.bind(Session, to=db.session, scope=singleton)


def configure_flask_globals(binder):
    binder.bind(Mail, to=mail, scope=singleton)
    binder.bind(AuthContext, scope=singleton)


if hasattr(sys, "_called_from_test"):
    modules = [configure_for_testing, configure_flask_globals]
else:
    modules = [configure_for_prod, configure_flask_globals]

injector = Injector(modules=modules)
