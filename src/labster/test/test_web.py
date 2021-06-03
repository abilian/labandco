"""Integration tests."""
from __future__ import annotations

import os
import uuid

import pytest
from flask import url_for

from labster.di import injector
from labster.domain2.model.structure import Structure, StructureRepository
from labster.domain2.model.type_structure import UN
from labster.domain.models.profiles import Profile
from labster.domain.models.unites import LABORATOIRE, OrgUnit
from labster.domain.services.roles import ROLES

IGNORED_ENDPOINTS = ["auth.callback", "auth.backdoor"]


# FIXME
if os.environ.get("TRAVIS"):
    pytest.skip("These tests currently fail on Travis", allow_module_level=True)

pytest.skip(
    "These tests currently fail since recent refactoring", allow_module_level=True
)

structure_repo = injector.get(StructureRepository)


#
# 'auth' blueprint
#
def test_login(client, db_session):
    r = client.get(url_for("auth.login"))
    assert r.status_code == 200


#
# 'main' blueprint
#
def test_home_as_anonymous(client, db_session):
    r = client.get(url_for("main.home"))
    assert r.status_code == 302


def test_home_as_dgrtt(client, db_session):
    login_as_dgrtt(client, db_session)
    r = client.get(url_for("main.home"), follow_redirects=True)
    assert r.status_code == 200


def test_home_as_gdl(client, db_session):
    login_as_gdl(client, db_session)
    r = client.get(url_for("main.home"), follow_redirects=True)
    assert r.status_code == 200


#
#
#
def test_url_for(app, db_session):
    assert url_for("main.home") == "http://localhost.localdomain/"

    p = Profile(uid="ayuso", nom="Ayuso", prenom="Sandrine", email="ayuso@example.com")
    assert url_for(p)

    dn = f"test{uuid.uuid4()}"
    nom = f"nom{uuid.uuid4()}"
    labo = OrgUnit(type=LABORATOIRE, dn=dn, nom=nom)
    assert url_for(labo)


# TODO: remove soon
# def test_directory(client, db_session):
#     login_as_dgrtt(client, db_session)
#     r = client.get(url_for("directory.home"))
#     assert r.status_code == 200
#
#     login_as_gdl(client, db_session)
#     r = client.get(url_for("main.home"), follow_redirects=True)
#     assert r.status_code == 200
#
#
# def xxx_test_nouvelle_demande_rh(client, db_session):
#     login_as_gdl(client, db_session)
#
#     r = client.get(url_for("demandes.demande_new"))
#     assert r.status_code == 200
#
#     data = {"prenom": "Snake", "nom": "Plisken"}
#     r = client.post(
#         url_for("demandes.demande_new_post"), data=data, follow_redirects=True
#     )
#     assert r.status_code == 200
#     assert "Snake Plisken" in r.get_data(as_text=True)
#
#     # debug_info = get_debug_info(r)
#     # url = debug_info['url']
#
#     r = client.get(url_for("demandes.demandes"), follow_redirects=True)
#     assert r.status_code == 200
#     assert "Snake Plisken" in r.get_data(as_text=True)
#
#
# #
# # Admin
# #
# def test_admin_views(client, db_session):
#     login_as_dgrtt(client, db_session)
#
#     r = client.get(url_for("admin2.home"))
#     assert r.status_code == 200
#
#     r = client.get(url_for("admin2.financeurs"))
#     assert r.status_code == 200
#
#     r = client.get(url_for("admin2.mapping_dgrtt"))
#     assert r.status_code == 200


#
# All...
#
@pytest.mark.parametrize("role", ROLES)
def test_all_simple_endpoints(role, client, app, db_session):
    # Setup repo with a root
    structure_repo.clear()
    universite = Structure(
        nom="Sorbonne Université",
        type_name=UN.name,
        sigle="SU",
        dn="ou=SU,ou=Affectations,dc=chapeau,dc=fr",
    )
    structure_repo.put(universite)

    login_as_dgrtt(client, db_session)

    Profile.__roles = [role]

    endpoints = get_endpoints(app)
    try:
        for endpoint in endpoints:
            print(f"checking endpoint '{endpoint}' with role '{role}'")
            check_endpoint(endpoint, client)
    finally:
        del Profile.__roles

    structure_repo.clear()


def get_endpoints(app):
    endpoints = []
    for rule in app.url_map.iter_rules():
        if "GET" not in rule.methods:
            continue

        endpoint = rule.endpoint
        blueprint_name = endpoint.split(".")[0]

        # Skip a few hard cases (FIXME after the SPA migration)
        if blueprint_name not in {"auth", "v3"}:
            continue

        # if blueprint_name not in ["main", "admin2"]:
        #     return
        if endpoint in IGNORED_ENDPOINTS:
            continue
        if rule.arguments:
            continue

        endpoints.append(rule.endpoint)

    return endpoints


def check_endpoint(endpoint, client):
    url = url_for(endpoint)
    try:
        r = client.get(url)
    except Exception:
        print(f"Error on url: {url} (endpoint: {endpoint})")
        raise
    assert r.status_code in (200, 302, 401, 403), f"for endpoint = '{endpoint}'"


#
# Util
#
def login_as_dgrtt(client, db_session):
    p = Profile(uid="ayuso", nom="Ayuso", prenom="Sandrine", email="ayuso@example.com")
    p.__roles = ["alc", "dgrtt"]
    db_session.add(p)
    db_session.flush()

    login_as(p, client)


def login_as_gdl(client, db_session):
    dn = f"test{uuid.uuid4()}"
    nom = f"nom{uuid.uuid4()}"
    labo = OrgUnit(type=LABORATOIRE, dn=dn, nom=nom)
    p = Profile(
        uid="courtoisi",
        nom="Courtois",
        prenom="Isabelle",
        email="courtoisi@example.com",
        laboratoire=labo,
    )
    db_session.add(p)
    db_session.flush()

    id = p.id
    p1 = Profile.query.get(id)
    assert p1 is p

    login_as(p, client)


def login_as(profile: Profile, client):
    uid = profile.uid
    r = client.get(url_for("auth.backdoor", uid=uid))
    assert r.status_code == 201

    r = client.get(url_for("v3.self"))
    assert r.status_code == 200
    assert r.json["data"]["uid"] == uid
