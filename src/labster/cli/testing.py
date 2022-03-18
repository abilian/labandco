"""Tests and validation commands."""
from __future__ import annotations

import random

import click
from flask import current_app
from flask.cli import AppGroup, with_appcontext

from labster.domain2.model.demande import DemandeRH
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure
from labster.domain2.services.calculs_couts import get_ctx_for_demande

from .commands import run_daemons

test = AppGroup("test")


@test.command("testcafe")
@click.option("--headless", is_flag=True)
@with_appcontext
def test_testcafe(headless):
    """Runs the e2e suite using testcafe (old suite)"""
    if headless:
        driver = "chrome:headless"
    else:
        driver = "chrome"

    daemons = [
        ("web", "flask run"),
        ("webpack", "yarn --cwd front run serve"),
        ("test-e2e", f"yarn --cwd front run testcafe {driver} tests/testcafe"),
    ]
    run_daemons(daemons)


@test.command("cypress")
@with_appcontext
def test_cypress():
    """Runs the e2e suite using Cypress (new suite)"""
    daemons = [
        ("web", "flask run"),
        ("webpack", "yarn --cwd front run serve"),
        ("test-e2e", "yarn --cwd front cypress run tests/e2e"),
    ]
    run_daemons(daemons)


@test.command("rpc")
def test_rpc():
    """Runs functional tests on the RPC endpoints."""
    daemons = [
        ("web", "flask run"),
        ("rpc-tests", "pytest rpc_tests"),
    ]
    run_daemons(daemons)


@test.command("validate-db")
@with_appcontext
def test_validatedb():
    def validate_structures():
        structures = Structure.query.all()
        print(f"Validating {len(structures)} structures")
        for ou in structures:
            ou.validate()

    def validate_demandes():
        demandes = DemandeRH.query.all()
        print(f"Validating {len(demandes)} demandes")
        for demande in demandes:
            ctx = get_ctx_for_demande(demande)
            assert ctx

    with current_app.test_request_context():
        validate_structures()
        validate_demandes()


@test.command("crawl")
@with_appcontext
def test_selfcrawl():
    config = current_app.config
    config["TESTING"] = True

    users: list[Profile] = Profile.query.all()
    for user in sorted(random.sample(users, 5000), key=lambda x: x.login):
        if not user.active:
            continue

        print(f"# Crawling with user {user.login}")

        client = current_app.test_client()

        client.get("/backdoor")
        client.get(f"/switch?uid={user.uid}")
        res = client.get("/")
        assert res.status_code == 200
