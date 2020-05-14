from __future__ import annotations

from glom import glom
from pytest import mark

from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure
from labster.domain2.model.type_structure import UN
from labster.domain2.services.roles import Role
from labster.rpc.commands.roles import add_roles, delete_role
from labster.rpc.queries.roles import get_role_selectors, get_roles


@mark.skip
def test_roles(structure_repo, profile_repo):
    universite = Structure(nom="SU", type_name=UN.name)
    structure_repo.put(universite)

    user = Profile(uid="toto")
    profile_repo.put(user)

    result = get_roles(universite.id)
    assert glom(result, (["users"], [["id"]])) == [[], [], [], [], []]

    add_roles(universite.id, [user.id], Role.PORTEUR.name)
    result = get_roles(universite.id)
    assert glom(result, (["users"], [["id"]])) == [[], [], [], [], [user.id]]

    delete_role(universite.id, user.id, Role.PORTEUR.name)
    result = get_roles(universite.id)
    assert glom(result, (["users"], [["id"]])) == [[], [], [], [], []]

    result = get_role_selectors(universite.id)
    # First select is not multiple
    assert glom(result, ["value"]) == [None, [], [], [], []]
