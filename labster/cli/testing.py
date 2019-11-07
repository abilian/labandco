"""Tests and validation commands."""
from __future__ import annotations

import random
from typing import List

import click
from flask import current_app
from flask.cli import AppGroup, with_appcontext

from labster.cli.commands import run_daemons
from labster.domain.models.demandes import DemandeRH
from labster.domain.models.unites import OrgUnit
from labster.domain.services.calculs_couts import get_ctx_for_demande

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
        ("test-e2e", f"yarn --cwd front cypress run tests/e2e"),
    ]
    run_daemons(daemons)


@test.command("validate-db")
@with_appcontext
def test_validatedb():
    def validate_org_units():
        orgunits = OrgUnit.query.all()
        print(f"Validating {len(orgunits)} orgunits")
        for ou in orgunits:
            ou.validate()

    def validate_demandes():
        demandes = DemandeRH.query.all()
        print(f"Validating {len(demandes)} demandes")
        for demande in demandes:
            ctx = get_ctx_for_demande(demande)
            assert ctx

    with current_app.test_request_context():
        validate_org_units()
        validate_demandes()


@test.command("crawl")
@with_appcontext
def test_selfcrawl():
    from flask_linktester import LinkTester
    from labster.domain.models.profiles import Profile

    config = current_app.config
    config["TESTING"] = True

    users: List[Profile] = Profile.query.all()
    for user in random.sample(users, 5000):
        if not user.active:
            continue

        print(f"# Crawling with user {user.uid}")

        client = current_app.test_client()
        client.get(f"/switch?uid={user.uid}")

        black_list = ["/_debug_toolbar/*", "/go"]
        linktester = LinkTester(
            client, verbosity=1, black_list=black_list, max_links=500
        )
        linktester.allowed_codes = {200, 301, 302}
        linktester.crawl("/")
