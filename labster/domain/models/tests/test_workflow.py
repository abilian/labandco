from __future__ import annotations

from labster.domain.models.demandes import RECRUTEMENT, DemandeRH
from labster.domain.models.profiles import Profile
from labster.domain.models.unites import LABORATOIRE, OrgUnit
from labster.domain.models.workflow import ABANDONNEE, ABANDONNER, \
    ACCUSER_RECEPTION, COMMENTER, CONFIRMER_FINALISATION_DGRTT, \
    CONFIRMER_RECEVABILITE_DGRTT, DESARCHIVER, EN_EDITION, EN_INSTRUCTION, \
    EN_VALIDATION, EN_VERIFICATION, PRENDRE_LA_MAIN_DGRTT, REJETER_DGRTT, \
    REQUERIR_MODIFICATION_DGRTT, REQUERIR_MODIFICATION_DIR, SOUMETTRE, \
    TRAITEE, VALIDER_DIR, LabsterWorkflow
from labster.lib.workflow import State

labo = OrgUnit(dn="labo", nom="Labo", type=LABORATOIRE)

joe_gdl = Profile(uid="joe_gdl", email="1", prenom="Joe", nom="GDL", laboratoire=labo)
jim_porteur = Profile(
    uid="jim_porteur", email="2", prenom="Jim", nom="Porteur", laboratoire=labo
)
jake_directeur = Profile(
    uid="jake_directeur", email="3", prenom="Jake", nom="Directeur", laboratoire=labo
)
jules_dgrtt = Profile(
    uid="jules_dgrtt", email="4", prenom="Jules", nom="Contact DR&I", dgrtt=True
)
jules2_dgrtt = Profile(
    uid="jules2_dgrtt", email="5", prenom="Jules2", nom="Contact DR&I", dgrtt=True
)


def test_state():
    class SomeState(State):
        pass

    assert SomeState().id == "SOME_STATE"


def test_abandon(app_context):
    demande = DemandeRH(type=RECRUTEMENT, gestionnaire=joe_gdl)

    wf = LabsterWorkflow(demande, joe_gdl)
    wf.start()

    assert wf.current_state() == EN_EDITION
    assert demande.active
    assert wf.possible_transitions() == [ABANDONNER]

    wf.execute_transition(ABANDONNER)
    assert wf.current_state() == ABANDONNEE
    assert not demande.active
    assert not demande.editable
    assert demande.current_owners() == []


def test_happy_path(mocker, app_context):
    demande = DemandeRH(
        type=RECRUTEMENT, porteur=jim_porteur, contact_dgrtt=jules_dgrtt
    )
    demande.id = 0
    mocker.patch.object(demande, "is_valid", return_value=True)
    mocker.patch.object(demande, "assigne_contact_dgrtt")
    mocker.patch.object(labo, "get_directeurs", return_value=[jake_directeur])

    assert labo.direction == [jake_directeur]

    wf = LabsterWorkflow(demande, jim_porteur)
    wf.start()

    assert wf.current_state() == EN_EDITION
    assert demande.active
    assert demande.editable
    assert wf.possible_transitions() == [SOUMETTRE, ABANDONNER, COMMENTER]

    wf.execute_transition(SOUMETTRE)
    assert wf.current_state() == EN_VALIDATION
    assert demande.active
    assert not demande.editable
    assert demande.current_owners() == [jake_directeur]
    assert demande.porteur not in demande.structure.direction
    assert wf.possible_transitions() == [ABANDONNER]

    wf.set_actor(jake_directeur)
    assert wf.possible_transitions() == [VALIDER_DIR, REQUERIR_MODIFICATION_DIR]

    wf.execute_transition(VALIDER_DIR)
    assert wf.current_state() == EN_VERIFICATION
    assert demande.active
    assert not demande.editable
    assert demande.current_owners() == [jules_dgrtt]
    assert wf.possible_transitions() == [COMMENTER]

    wf.set_actor(jules_dgrtt)
    assert wf.possible_transitions() == [
        ACCUSER_RECEPTION,
        CONFIRMER_RECEVABILITE_DGRTT,
        REQUERIR_MODIFICATION_DGRTT,
        REJETER_DGRTT,
        COMMENTER,
    ]

    wf.execute_transition(ACCUSER_RECEPTION)
    assert wf.possible_transitions() == [
        CONFIRMER_RECEVABILITE_DGRTT,
        REQUERIR_MODIFICATION_DGRTT,
        REJETER_DGRTT,
        COMMENTER,
    ]

    wf.execute_transition(CONFIRMER_RECEVABILITE_DGRTT)
    assert wf.current_state() == EN_INSTRUCTION
    assert demande.active
    assert not demande.editable
    assert demande.current_owners() == [jules_dgrtt]
    assert wf.possible_transitions() == [
        CONFIRMER_FINALISATION_DGRTT,
        REQUERIR_MODIFICATION_DGRTT,
        REJETER_DGRTT,
        COMMENTER,
    ]

    wf.execute_transition(CONFIRMER_FINALISATION_DGRTT)
    assert wf.current_state() == TRAITEE
    assert not demande.active
    assert not demande.editable
    assert demande.current_owners() == []
    assert wf.possible_transitions() == [DESARCHIVER]

    demande.id = None


def test_demande_modification(mocker, app_context):
    demande = DemandeRH(
        type=RECRUTEMENT, gestionnaire=joe_gdl, porteur=jim_porteur, id=1
    )
    mocker.patch.object(demande, "is_valid", return_value=True)
    mocker.patch.object(labo, "get_directeurs", return_value=[jake_directeur])
    mocker.patch.object(demande, "assigne_contact_dgrtt")

    wf = LabsterWorkflow(demande, joe_gdl)
    wf.start()

    wf.set_actor(jim_porteur)
    wf.execute_transition(SOUMETTRE)

    wf.set_actor(jake_directeur)
    wf.execute_transition(REQUERIR_MODIFICATION_DIR)

    wf.set_actor(jim_porteur)
    wf.execute_transition(SOUMETTRE)


def test_demande_modification_dgrtt(mocker, app_context):
    demande = DemandeRH(type=RECRUTEMENT, gestionnaire=joe_gdl, porteur=jim_porteur)
    demande.id = 0
    mocker.patch.object(demande, "is_valid", return_value=True)
    mocker.patch.object(labo, "get_directeurs", return_value=[jake_directeur])
    mocker.patch.object(demande, "assigne_contact_dgrtt")

    wf = LabsterWorkflow(demande, joe_gdl)
    wf.start()

    wf.set_actor(jim_porteur)
    wf.execute_transition(SOUMETTRE)

    wf.set_actor(jake_directeur)
    wf.execute_transition(VALIDER_DIR)

    demande.contact_dgrtt = jules_dgrtt

    wf.set_actor(jules_dgrtt)
    wf.execute_transition(ACCUSER_RECEPTION)
    wf.execute_transition(REQUERIR_MODIFICATION_DGRTT)

    wf.set_actor(jim_porteur)
    wf.execute_transition(SOUMETTRE)

    wf.set_actor(jules_dgrtt)
    wf.execute_transition(CONFIRMER_RECEVABILITE_DGRTT)
    wf.execute_transition(REQUERIR_MODIFICATION_DGRTT)

    wf.set_actor(jim_porteur)
    wf.execute_transition(SOUMETTRE)

    wf.set_actor(jules_dgrtt)
    wf.execute_transition(CONFIRMER_FINALISATION_DGRTT)

    assert not demande.active


def test_gestionnaire_peut_soumettre(mocker, app_context):
    # si la structure permet aux gestionnaires de soumettre directement
    # le gestionnaire voit le bouton soumettre (arrive à soumettre).
    demande = DemandeRH(
        type=RECRUTEMENT, porteur=jim_porteur, contact_dgrtt=jules_dgrtt, id=1
    )
    mocker.patch.object(demande, "is_valid", return_value=True)
    mocker.patch.object(
        demande.structure, "permettre_soummission_directe", return_value=True
    )  # warn: this is a function, not a boolean.
    mocker.patch.object(demande, "assigne_contact_dgrtt")
    mocker.patch.object(labo, "get_directeurs", return_value=[jake_directeur])
    mocker.patch.object(labo, "get_gestionnaires", return_value=[jules_dgrtt])

    wf = LabsterWorkflow(demande, jules_dgrtt)
    wf.start()
    wf.execute_transition(SOUMETTRE)
    assert wf.state == EN_VALIDATION


def test_prendre_la_main_drgtt(mocker, app_context):
    demande = DemandeRH(
        type=RECRUTEMENT, porteur=jim_porteur, contact_dgrtt=jules_dgrtt, id=1
    )
    mocker.patch.object(demande, "is_valid", return_value=True)
    mocker.patch.object(demande, "assigne_contact_dgrtt")
    mocker.patch.object(labo, "get_directeurs", return_value=[jake_directeur])

    wf = LabsterWorkflow(demande, jim_porteur)
    wf.start()
    wf.execute_transition(SOUMETTRE)

    wf.set_actor(jake_directeur)
    wf.execute_transition(VALIDER_DIR)
    assert wf.state == EN_VERIFICATION

    # Jules2 veut prendre la main
    wf.set_actor(jules2_dgrtt)
    assert wf.possible_transitions() == [
        PRENDRE_LA_MAIN_DGRTT,
        REJETER_DGRTT,
        # COMMENTER,
    ]
    assert demande.contact_dgrtt == jules_dgrtt

    wf.execute_transition(PRENDRE_LA_MAIN_DGRTT)
    assert wf.possible_transitions() == [
        ACCUSER_RECEPTION,
        CONFIRMER_RECEVABILITE_DGRTT,
        REQUERIR_MODIFICATION_DGRTT,
        REJETER_DGRTT,
        COMMENTER,
    ]
    assert demande.contact_dgrtt == jules2_dgrtt

    wf.set_actor(jules_dgrtt)
    assert wf.possible_transitions() == [
        PRENDRE_LA_MAIN_DGRTT,
        REJETER_DGRTT,
        # COMMENTER,
    ]
