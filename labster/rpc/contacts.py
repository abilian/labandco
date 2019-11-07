from __future__ import annotations

from typing import Any, Dict, List

from jsonrpcserver import method

from labster.di import injector
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.model.structure import Structure, StructureId, \
    StructureRepository
from labster.domain2.services.contacts import ContactService, ContactType
from labster.persistence import Persistence
from labster.types import JSON

from .util import ensure_role

DRI_DN = "ou=0107,ou=SCUN,ou=SU,ou=Affectations,dc=chapeau,dc=fr"
DRI_ET_DRV_DNS = [
    DRI_DN,
    "ou=M0107,ou=FACM,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=RE,ou=SG,ou=FACL,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    "ou=S0107,ou=UP6,ou=SU,ou=Affectations,dc=chapeau,dc=fr",
]

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
contact_service = injector.get(ContactService)
persistence = injector.get(Persistence)


@method
def get_contacts(structure_id) -> JSON:
    structure = structure_repo.get_by_id(StructureId(structure_id))
    assert structure
    return make_contacts_dto(structure)


@method
def get_all_contacts() -> JSON:
    structures: List[Structure] = list(structure_repo.get_all())
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
def get_membres_dri() -> JSON:
    profiles = profile_repo.get_all()
    membres_dri = [p for p in profiles if p.affectation in DRI_ET_DRV_DNS]
    membres_dri.sort(key=lambda x: (x.nom, x.prenom))
    return [{"uid": m.uid, "nom": m.nom, "prenom": m.prenom} for m in membres_dri]


@method
def update_contacts(structure_id: str, contacts: Dict[str, str]):
    ensure_role("alc")

    structure = structure_repo.get_by_id(StructureId(structure_id))
    assert structure

    for contact_type_name, uid in contacts.items():
        contact_type = getattr(ContactType, contact_type_name)
        if uid:
            profile = profile_repo.get_by_uid(uid)
            contact_service.set_contact(structure, contact_type, profile)
        else:
            contact_service.delete_contact(structure, contact_type)

    persistence.save()


#
# Util
#
def make_contacts_dto(structure: Structure) -> List[Dict[str, Any]]:
    result = []
    for contact_type in ContactType:
        contact = contact_service.get_contact(structure, contact_type)
        if contact:
            dto = {
                "id": contact.id,
                "uid": contact.uid,
                "name": contact.full_name,
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
