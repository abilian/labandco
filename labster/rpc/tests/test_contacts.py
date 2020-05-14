from __future__ import annotations

from glom import glom
from sqlalchemy.orm import scoped_session

from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure
from labster.domain2.model.type_structure import UN
from labster.domain2.services.contacts import ContactType
from labster.rpc.commands.contacts import update_contacts
from labster.rpc.queries.contacts import get_contacts


def test_contacts(structure_repo, profile_repo, db_session: scoped_session):
    universite = Structure(nom="SU", type_name=UN.name)
    structure_repo.put(universite)

    result = get_contacts(universite.id)
    assert len(result) == 8

    user = Profile(uid="toto")
    profile_repo.put(user)

    contacts = {ct.name: "" for ct in ContactType}
    update_contacts(universite.id, contacts)
    result = get_contacts(universite.id)
    assert len(result) == 8
    assert glom(result, ["uid"]) == [None] * 8

    contacts["CONTACT_ENTREPRISES"] = user.uid
    update_contacts(universite.id, contacts)
    result = get_contacts(universite.id)
    assert len(result) == 8

    result1 = glom(result, ["uid"])
    assert result1[0] == "toto"
    assert result1[1:8] == [None] * 7

    contacts = {ct.name: user.uid for ct in ContactType}
    update_contacts(universite.id, contacts)
    result = get_contacts(universite.id)
    assert len(result) == 8
    assert glom(result, ["uid"]) == ["toto"] * 8
