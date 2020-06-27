from __future__ import annotations

from sqlalchemy.orm import scoped_session

from labster.domain2.model.structure import Structure
from labster.domain2.model.type_structure import UN
from labster.rpc.queries.structures import sg_get_structure


def test_structures(structure_repo, db_session: scoped_session):
    universite = Structure(nom="SU", type_name=UN.name)
    structure_repo.put(universite)

    result = sg_get_structure(universite.id)
    expected = {
        "_depth": -1,
        "active": True,
        "ancestors": [],
        "can_be_deleted": True,
        "children": [],
        "dn": "",
        "email": "",
        "id": universite.id,
        "is_reelle": True,
        "nom": "SU",
        "old_dn": "",
        "old_id": None,
        "parents": [],
        "permettre_reponse_directe": True,
        "permettre_soummission_directe": False,
        "permissions": {},
        "sigle": "",
        "supann_code_entite": None,
        "type_name": "Université",
    }
    assert result == expected
