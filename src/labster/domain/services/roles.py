"""Stateless role service.

Dummy implementation for now.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from labster.extensions import db

from . import dgrtt as dgrtt_service

if TYPE_CHECKING:
    from labster.domain.models.profiles import Profile
    from labster.domain.models.roles import Role, RoleType


ROLES_RECHERCHE = ["recherche", "porteur", "gestionnaire", "directeur", "all"]
ROLES_DGRTT = [
    "dgrtt",
    "contact dgrtt",
    "référent",
    "chef de bureau",
    "direction dgrtt",
    "alc",
    "gestionnaire faq",
]
ROLES = ROLES_DGRTT + ROLES_RECHERCHE + ["gouvernance"]


def has_role(user: Profile, role: str, target=None) -> bool:
    """Returns True if user has given role on given target."""
    from labster.domain.models.demandes import Demande
    from labster.domain.models.roles import RoleType

    assert role in ROLES

    # XXX: hack for unit tests
    __roles = getattr(user, "__roles", [])
    if __roles and role in __roles:
        return True

    if role == "alc" and user.uid == "poulainm":
        return True

    ROLES_TO_ROLE_TYPES = {
        "directeur": RoleType.DIRECTION,
        "porteur": RoleType.PORTEUR,
        "contact dgrtt": RoleType.CONTACT_DGRTT,
        "gestionnaire faq": RoleType.ALC,  # TODO
        "alc": RoleType.ALC,
        "all": RoleType.ALL,
    }
    if role in ROLES_TO_ROLE_TYPES:
        return _has_role(user, ROLES_TO_ROLE_TYPES[role], target)

    if role == "recherche":
        return user.laboratoire is not None

    if role == "gouvernance":
        return bool(user.gouvernance_vraiment)

    if role == "dgrtt":
        return bool(user.dgrtt)

    # Rôles "recherche"
    if role == "gestionnaire":
        if isinstance(target, Demande):
            return has_role(user, role, target.structure)

        if _has_role(user, RoleType.GDL, target):
            return True
        if not target:
            return False
        parent = target.parent
        if not parent:
            return False
        if _has_role(user, RoleType.GDL, parent):
            return True

        parent = parent.parent
        if not parent:
            return False
        return _has_role(user, RoleType.GDL, parent)

    if target:
        return has_contextual_role(user, role, target)

    # Rôles DGRTT
    if role == "référent":
        return dgrtt_service.est_referent(user)

    if role == "chef de bureau":
        return bool(user.chef_du_bureau)

    if role == "direction dgrtt":
        fsp = user.fonction_structurelle_principale
        return (
            has_role(user, "dgrtt") and fsp and "Directeur de services centraux" in fsp
        )

    if role == "admin":
        raise RuntimeError("Role 'admin' has been replaced by 'alc'")

    raise NotImplementedError(f"Le rôle '{role}' n'existe pas")


def has_contextual_role(user: Profile, role: str, target) -> bool:
    assert role in ROLES

    from labster.domain.models.demandes import Demande
    from labster.domain.models.unites import OrgUnit

    # TODO: forward to OrgUnit instead ?
    if isinstance(target, OrgUnit):
        return has_role(user, role) and user in target.membres

    if isinstance(target, Demande):
        return has_role(user, role, target.structure)

    return False


def rename_role_dgrtt_to_dri(role):
    """Simple rename instead of data migration."""
    if "dgrtt" in role.lower():
        role = role.replace("DGRTT", "DR&I")
        role = role.replace("dgrtt", "DR&I")
    return role


def all_roles(user):
    roles = []
    for role in ROLES:
        if has_role(user, role):
            roles.append(rename_role_dgrtt_to_dri(role))
    return roles


#
# DB-backed roles
#
def _has_role(user, role_type, target=None):
    # type: (Profile, RoleType, Any) -> bool

    from labster.domain.models.roles import RoleType

    assert isinstance(role_type, RoleType)

    roles = user.roles
    if target:
        return any(r.type == role_type.value for r in roles if r.context == target)
    else:
        return any(r.type == role_type.value for r in roles)


def get_roles(user=None, role_type=None, target=None) -> list[Role]:
    from labster.domain.models.roles import Role, RoleType

    assert isinstance(role_type, (type(None), RoleType))
    assert user or role_type or target

    query = Role.query
    if user:
        query = query.filter_by(profile=user)
    if role_type:
        query = query.filter_by(type=role_type.value)
    if target:
        query = query.filter_by(context=target)
    return query.all()


def set_role_value(user, role: str, value: bool, target=None):
    from labster.domain.models.roles import RoleType

    assert isinstance(role, str)

    mapping = {
        # Rôles labos
        "porteur": RoleType.PORTEUR,
        "directeur": RoleType.DIRECTION,
        "gestionnaire": RoleType.GDL,
        "all": RoleType.ALL,
        # Rôles DGRTT
        "contact dgrtt": RoleType.CONTACT_DGRTT,
        "alc": RoleType.ALC,
    }
    try:
        role_type = mapping[role]
    except KeyError:
        raise RuntimeError(f"Unknown role: {role}")

    if value and not _has_role(user, role_type, target):
        grant_role(user, role_type, target)

    elif not value and _has_role(user, role_type, target):
        ungrant_role(user, role_type, target)


def grant_role(user: Profile, role_type: RoleType, target=None):
    from labster.domain.models.roles import Role, RoleType

    assert isinstance(role_type, RoleType)

    roles = (
        Role.query.filter(Role.profile == user)
        .filter(Role.type == role_type.value)
        .filter(Role.context == target)
        .all()
    )
    assert len(roles) == 0

    role = Role(type=role_type.value, profile=user, context=target)
    db.session.add(role)


def ungrant_role(user: Profile, role_type: RoleType, target=None):
    from labster.domain.models.roles import Role, RoleType

    assert isinstance(role_type, RoleType)

    roles = (
        Role.query.filter(Role.profile == user)
        .filter(Role.type == role_type.value)
        .filter(Role.context == target)
        .all()
    )
    assert len(roles) == 1
    role = roles[0]
    assert role in user.roles
    index = user.roles.index(role)
    del user.roles[index]


# Utilisé en phase de test (URL: /switch/).
def get_all_users() -> list[Profile]:
    from labster.domain.models.profiles import Profile

    gestionnaires = {"pulcherie", "boyern", "courtoisi", "sos", "girardv"}
    porteurs = {"carapezzi", "duhieu", "lombard", "diasdeamorim", "valdes"}
    directeurs = {
        "santiardbaro",
        "charretier",
        "sciandra",
        "mercierc",
        "mouchelj",
        "stemmann",
    }

    all_uids = gestionnaires | porteurs | directeurs

    users = Profile.query.filter(Profile.uid.in_(all_uids)).all()

    users += list(dgrtt_service.get_membres())
    users = sorted(users, key=lambda x: x.uid)

    return users
