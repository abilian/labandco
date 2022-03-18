from __future__ import annotations

from typing import Any

from jsonrpcserver import method

from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import Structure, StructureRepository
from labster.domain2.services.contacts import ContactService, ContactType
from labster.domain2.services.roles import Role, RoleService
from labster.ldap.constants import DRI_ET_DRV_DNS
from labster.security import get_current_profile
from labster.types import JSONDict, JSONList

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
contact_service = injector.get(ContactService)
role_service = injector.get(RoleService)


@method
def get_contacts(structure_id) -> JSONList:
    structure = structure_repo.get_by_id(structure_id)
    assert structure
    return make_contacts_dto(structure)


@method
def get_all_contacts() -> JSONList:
    structures: list[Structure] = list(structure_repo.get_all())
    structures.sort(key=lambda x: x.nom)

    result = []
    for structure in structures:
        for contact_type in ContactType:
            contact = contact_service.get_contact(structure, contact_type)
            if contact:
                structure_dto = {
                    "name": structure.nom,
                    "id": structure.id,
                    "type": structure.type_name,
                    "sigle": structure.sigle,
                }
                result.append(
                    {
                        "structure": structure_dto,
                        "contacts": make_contacts_dto(structure),
                    }
                )
                break

    return result


@method
def get_membres_dri() -> JSONList:
    membres_dri_et_drv_set = set()
    for dn in DRI_ET_DRV_DNS:
        structure = structure_repo.get_by_dn(dn)
        membres_structure = role_service.get_users_with_given_role(
            Role.MEMBRE, structure
        )
        membres_dri_et_drv_set.update(membres_structure)

    membres_dri_et_drv = list(membres_dri_et_drv_set)
    membres_dri_et_drv.sort(key=lambda x: (x.nom, x.prenom))
    return [
        {"uid": m.uid, "nom": m.nom, "prenom": m.prenom} for m in membres_dri_et_drv
    ]


@method
def get_contacts_for_user() -> JSONDict:
    user = get_current_profile()

    roles: dict[Role, set[Structure]] = role_service.get_roles_for_user(user)
    structures = list(roles[Role.MEMBRE])
    structures.sort(key=lambda x: x.nom)

    result1 = []
    for structure in structures:
        for contact_type in ContactType:
            contact = contact_service.get_contact(structure, contact_type)
            if contact:
                structure_dto = {
                    "name": structure.nom,
                    "id": structure.id,
                    "type": structure.type_name,
                    "sigle": structure.sigle,
                }
                result1.append(
                    {
                        "structure": structure_dto,
                        "contacts": make_contacts_dto(structure),
                    }
                )
                break

    result2 = []
    mapping: dict[Structure, dict[ContactType, Profile]] = contact_service.get_mapping()
    for structure, d in mapping.items():
        if user in d.values():
            for contact_type, user1 in d.items():
                if user1 == user:
                    structure_dto = {
                        "name": structure.nom,
                        "id": structure.id,
                        "type": structure.type_name,
                        "sigle": structure.sigle,
                    }
                    result2.append(
                        {
                            "structure": structure_dto,
                            "bureau": contact_type.value,
                        }
                    )

    return {
        "structures": result1,
        "mes_contacts": result2,
    }


#
# Serialization
#
def make_contacts_dto(structure: Structure) -> list[dict[str, Any]]:
    result = []
    for contact_type in ContactType:
        contact = contact_service.get_contact(structure, contact_type)
        if contact:
            dto = {
                "id": contact.id,
                "uid": contact.uid,
                "name": contact.full_name,
                "tel": contact.telephone,
                "email": contact.email,
                "type_name": contact_type.name,
                "type_value": contact_type.value,
            }
        else:
            dto = {
                "id": None,
                "uid": None,
                "name": "",
                "type_name": contact_type.name,
                "type_value": contact_type.value,
            }
        result.append(dto)
    return result
