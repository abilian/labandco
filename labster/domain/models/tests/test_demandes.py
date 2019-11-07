from __future__ import annotations

from pytest import fixture

from ..demandes import demande_factory
from ..profiles import Profile
from ..unites import LABORATOIRE, OrgUnit
from ..workflow import EN_EDITION, REJETEE


@fixture
def ihp(db_session):
    ihp = OrgUnit(type=LABORATOIRE, nom="Institut Henri Poincaré", sigle="IHP")
    db_session.add(ihp)
    db_session.flush()
    return ihp


@fixture
def jojo(ihp, db_session):
    jojo = Profile(
        uid="jojolapin",
        nom="Lapin",
        prenom="Jojo",
        email="jojo@lapin.org",
        laboratoire=ihp,
    )
    db_session.add(jojo)
    db_session.flush()
    assert jojo.laboratoire == ihp
    return jojo


def test_demande(jojo, ihp, db_session):
    demande = demande_factory("rh", jojo, {}, nom="Nom de la convention", porteur=jojo)
    assert demande.porteur == jojo
    assert demande.structure == ihp

    db_session.add(demande)
    db_session.flush()

    assert isinstance(demande.id, int)
    assert demande.current_owners() == [jojo]
    assert len(demande.wf_history) == 1
    assert "DemandeRH" in repr(demande)

    # TODO: doesn't work with client-side validation
    # assert not demande.is_valid()

    demande.data = {
        "departement": "None",
        "numero_de_financement": "123",
        "grade_correspondant": "IR",
        "fonction_du_poste": "",
        "modification_mission": False,
        "porteur": "antoined",
        "justification_du_salaire": "",
        "co_finance": False,
        "indemnite_transport_en_commun": False,
        "equipe": "None",
        "email": "sf@fermigier.com",
        "nom": "Fermigier",
        "nombre_enfants_a_charge": None,
        "type_de_demande": "Contrat initial",
        "localisation": "Paris ou r\xe9gion parisienne",
        "modification_autre": False,
        "acceptation_principe_recrutement": True,
        "publicite": "",
        "quotite_de_travail": "100%",
        "commentaire": "",
        "ecole_doctorale": "ED 127 : Astronomie et astrophysique d'\xcele-de-France",
        "modification_remuneration": False,
        "nb_candidats_recus": None,
        "prenom": "Stefane",
        "financement2": "eOTP",
        "nature_du_recrutement": "cdd",
        "numero_de_financement2": "",
        "salaire_brut_mensuel": None,
        "civilite": "M.",
        "financement": "eOTP",
        "objet_de_la_mission": "",
    }
    validation = demande.validate()
    assert not validation.errors
    assert validation.extra_errors
    assert not validation.ok
    assert not demande.is_valid()


def test_demande_clone(jojo, ihp):
    demande = demande_factory(
        "rh",
        jojo,
        {},
        nom="Nom de la convention",
        porteur=jojo,
        structure=ihp,
        wf_state=REJETEE.id,
    )

    nouvelle_demande = demande.clone()
    assert nouvelle_demande.wf_state == EN_EDITION.id
