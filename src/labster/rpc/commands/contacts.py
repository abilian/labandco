from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method

from labster.di import injector
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.contacts import ContactService, ContactType
from labster.rbac import check_can_edit_contacts

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
contact_service = injector.get(ContactService)
db = injector.get(SQLAlchemy)


@method
def update_contacts(structure_id: str, contacts: dict[str, str]):
    structure = structure_repo.get_by_id(structure_id)
    check_can_edit_contacts(structure)

    for contact_type_name, uid in contacts.items():
        contact_type = getattr(ContactType, contact_type_name)
        if uid:
            profile = profile_repo.get_by_uid(uid)
            contact_service.set_contact(structure, contact_type, profile)
        else:
            contact_service.delete_contact(structure, contact_type)

    db.session.commit()
