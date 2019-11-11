from __future__ import annotations

from typing import Dict

from jsonrpcserver import method

from labster.di import injector
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.model.structure import StructureId, StructureRepository
from labster.domain2.services.contacts import ContactService, ContactType
from labster.persistence import Persistence

from ..util import ensure_role

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
