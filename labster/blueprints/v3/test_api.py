"""API tests."""
from __future__ import annotations

from flask.testing import FlaskClient
from sqlalchemy.orm.scoping import scoped_session

from labster.di import injector
from labster.domain2.model.structure import Structure, StructureRepository
from labster.domain2.model.type_structure import FA, UN
from labster.test.test_web import login_as_dgrtt
from labster.util import url_for

structure_repo = injector.get(StructureRepository)


def test_menu(client: FlaskClient, db_session: scoped_session) -> None:
    login_as_dgrtt(client, db_session)

    r = client.get(url_for("v3.menu"))
    assert r.status_code == 200


# def test_demandes(client, db_session):
#     login_as_dgrtt(client, db_session)
#
#     r = client.get(url_for("v3.demandes"))
#     assert r.status_code == 200


def test_structures(client: FlaskClient, db_session: scoped_session) -> None:
    login_as_dgrtt(client, db_session)

    universite = Structure(
        nom="Sorbonne Université",
        type_name=UN.name,
        sigle="SU",
        dn="ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    )
    fac_sciences = Structure(nom="Faculté des Sciences", type_name=FA.name)
    structure_repo.put(universite)
    structure_repo.put(fac_sciences)

    r = client.get(url_for("v3.all_structures"))
    assert r.status_code == 200

    structure_repo.clear()


def test_users(client: FlaskClient, db_session: scoped_session) -> None:
    login_as_dgrtt(client, db_session)

    r = client.get(url_for("v3.all_users"))
    assert r.status_code == 200
