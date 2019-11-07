from __future__ import annotations

from pytest import fixture

from labster.domain.models.profiles import Profile
from labster.domain.models.roles import RoleType
from labster.domain.models.unites import LABORATOIRE, OrgUnit
from labster.domain.services import dgrtt as dgrtt_service
from labster.domain.services import roles as roles_service
from labster.domain.services.dgrtt import BureauDgrtt


@fixture
def ihp(db_session):
    ihp = OrgUnit(type=LABORATOIRE, nom="IHP", sigle="IHP")
    db_session.add(ihp)
    db_session.flush()
    return ihp


@fixture
def lov(db_session):
    lov = OrgUnit(type=LABORATOIRE, nom="LOV", sigle="LOV")
    db_session.add(lov)
    db_session.flush()
    return lov


@fixture
def jojo(db_session):
    jojo = Profile(
        uid="jojolapin", nom="Lapin", prenom="Jojo", email="jojo@lapin.org", dgrtt=True
    )
    db_session.add(jojo)
    db_session.flush()
    return jojo


@fixture
def lulu(ihp, db_session):
    lulu = Profile(
        uid="lulubear",
        nom="Bear",
        prenom="Lulu",
        email="lulu@bear.org",
        laboratoire=ihp,
    )
    db_session.add(lulu)
    db_session.flush()
    return lulu


def test_dgrtt_service(jojo, ihp, db_session):
    assert jojo.has_role("dgrtt")
    assert not jojo.has_role("référent")

    bureau = BureauDgrtt.from_id("ETT")
    dgrtt_service.set_mapping(ihp, "ETT", jojo)
    db_session.flush()

    assert ihp in dgrtt_service.get_perimetre_dgrtt(jojo)

    assert bureau == dgrtt_service.get_bureau_dgrtt(jojo)

    assert dgrtt_service.get_membres_du_bureau_dgrtt(bureau) == [jojo]

    contacts = dgrtt_service.contacts_structure(ihp)
    assert "ETT" in contacts.keys()
    assert jojo in contacts.values()

    assert dgrtt_service.get_contact_dgrtt(ihp, "ETT") == jojo
    assert dgrtt_service.get_contact_dgrtt(ihp, "CFE") == None

    assert dgrtt_service.mapping() == {ihp: [jojo, None, None, None, None, None, None]}

    dgrtt_service.check()

    dgrtt_service.set_mapping(ihp, "REF", jojo)
    db_session.flush()

    assert jojo.has_role("référent")
    assert dgrtt_service.get_referent(ihp) == jojo
    assert dgrtt_service.labos_dont_je_suis_referent(jojo) == {ihp}

    dgrtt_service.check()


def test_roles(lulu, db_session):
    assert lulu.has_role("recherche")
    assert not lulu.has_role("dgrtt")

    assert not lulu.has_role("porteur")
    roles = roles_service.get_roles(lulu)
    assert len(roles) == 0

    roles_service.grant_role(lulu, RoleType.PORTEUR)
    db_session.flush()
    assert lulu.has_role("porteur")
    roles = roles_service.get_roles(lulu)
    assert len(roles) == 1
    assert roles[0].type == RoleType.PORTEUR.value
    assert roles[0].profile == lulu

    roles_service.ungrant_role(lulu, RoleType.PORTEUR)
    db_session.flush()
    assert not lulu.has_role("porteur")
    roles = roles_service.get_roles(lulu)
    assert len(roles) == 0


def test_roles2(lulu, db_session):
    assert not lulu.has_role("porteur")

    roles_service.set_role_value(lulu, "porteur", True)
    db_session.flush()
    assert lulu.has_role("porteur")

    roles_service.set_role_value(lulu, "porteur", False)
    db_session.flush()
    assert not lulu.has_role("porteur")


def test_roles3(ihp, jojo, db_session):
    ihp.set_roles([jojo], RoleType.GDL)
    db_session.flush()
    assert jojo.has_role("gestionnaire", ihp)

    # ihp.set_roles([], RoleType.GDL)
    # db_session.flush()
    # assert not jojo.has_role('gestionnaire', ihp)
