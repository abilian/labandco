from __future__ import annotations

from sqlalchemy.orm.scoping import scoped_session

from ..financeurs import Financeur
from ..mapping_dgrtt import MappingDgrtt
from ..profiles import Profile
from ..roles import Role
from ..unites import LABORATOIRE, OrgUnit


def test_profile(db_session: scoped_session) -> None:
    profile = Profile(
        uid="jojolapin", nom="Lapin", prenom="Jojo", email="jojo@lapin.org"
    )
    db_session.add(profile)
    db_session.flush()


def test_labo(db_session: scoped_session) -> None:
    labo = OrgUnit(type=LABORATOIRE, nom="Institut Henri Poincaré", sigle="IHP")
    db_session.add(labo)
    db_session.flush()


def test_mapping(db_session: scoped_session) -> None:
    profile = Profile(
        uid="jojolapin", nom="Lapin", prenom="Jojo", email="jojo@lapin.org"
    )
    labo = OrgUnit(type=LABORATOIRE, nom="Institut Henri Poincaré", sigle="IHP")
    mapping = MappingDgrtt(
        ou_recherche=labo, contact_dgrtt=profile, bureau_dgrtt="TEST"
    )
    assert str(mapping)
    db_session.add(mapping)
    db_session.flush()


def test_financeur(db_session: scoped_session) -> None:
    financeur = Financeur(
        nom="Agence National de la Recherche",
        sigle="ANR",
        type="TYPE",
        sous_type="SOUS-TYPE",
        pays="France",
    )
    db_session.add(financeur)
    db_session.flush()


def test_role() -> None:
    role = Role()  # noqa


# def test_config(db_session):
#     data = {1: 2, "a": "b"}
#     cfg = Config(name="test", data=data)
#     db_session.add(cfg)
#     db_session.flush()
#
#     db_session.expunge(cfg)
#
#     cfg2 = Config.query.get_by_name("test")
#     assert cfg2 is not cfg
#     assert cfg2.data == data
