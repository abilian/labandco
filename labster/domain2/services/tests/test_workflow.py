from __future__ import annotations

from labster.domain2.model.demande import DemandeRH
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import Structure, StructureRepository
from labster.domain2.model.type_structure import DU, LA
from labster.domain2.services.roles import Role, RoleService
from labster.domain2.services.workflow.states import ABANDONNEE, \
    EN_INSTRUCTION, EN_VALIDATION, EN_VERIFICATION, TRAITEE
from labster.domain2.services.workflow.transitions import ABANDONNER, \
    ACCUSER_RECEPTION, COMMENTER, CONFIRMER_FINALISATION_DGRTT, \
    CONFIRMER_RECEVABILITE_DGRTT, DESARCHIVER, PRENDRE_LA_MAIN_DGRTT, \
    REJETER_DGRTT, REQUERIR_MODIFICATION_DGRTT, REQUERIR_MODIFICATION_DIR, \
    SOUMETTRE, VALIDER_DIR
from labster.domain2.services.workflow.workflow import LabsterWorkflow
from labster.domain.models.workflow import EN_EDITION
from labster.ldap.constants import DRI_DN
from labster.lib.workflow import State


def test_state():
    class SomeState(State):
        pass

    assert SomeState().id == "SOME_STATE"


def prepare_test(injector, db):
    # On créé in certain nombre de structures et de profils utilisateurs pour chaque tests
    class NS:
        # Create structures
        labo = Structure(dn="labo", nom="Labo", type_name=LA.name)
        dri = Structure(dn=DRI_DN, nom="DR&I", type_name=DU.name)

        # Create profiles
        joe_gdl = Profile(uid="joe_gdl", email="1", prenom="Joe", nom="GDL")
        jim_porteur = Profile(uid="jim_porteur", email="2", prenom="Jim", nom="Porteur")
        jake_directeur = Profile(
            uid="jake_directeur", email="3", prenom="Jake", nom="Directeur"
        )
        jules_dri = Profile(
            uid="jules_dgrtt", email="4", prenom="Jules", nom="Contact DR&I"
        )
        jules2_dri = Profile(
            uid="jules2_dgrtt", email="5", prenom="Jules2", nom="Contact DR&I"
        )

    x = NS()

    role_service = injector.get(RoleService)
    structure_repository = injector.get(StructureRepository)
    profile_repository = injector.get(ProfileRepository)

    structure_repository.put(x.labo)
    structure_repository.put(x.dri)

    profile_repository.put(x.jim_porteur)
    profile_repository.put(x.jake_directeur)
    profile_repository.put(x.joe_gdl)
    profile_repository.put(x.jules_dri)
    profile_repository.put(x.jules2_dri)

    role_service.grant_role(x.jake_directeur, Role.RESPONSABLE, x.labo)
    role_service.grant_role(x.jim_porteur, Role.MEMBRE, x.labo)
    role_service.grant_role(x.joe_gdl, Role.GESTIONNAIRE, x.labo)
    role_service.grant_role(x.joe_gdl, Role.GESTIONNAIRE, x.labo)
    role_service.grant_role(x.jules_dri, Role.MEMBRE, x.dri)
    role_service.grant_role(x.jules2_dri, Role.MEMBRE, x.dri)

    db.session.flush()

    assert role_service.has_role(x.jake_directeur, Role.RESPONSABLE, x.labo)
    assert role_service.has_role(x.jim_porteur, Role.MEMBRE, x.labo)
    assert role_service.has_role(x.joe_gdl, Role.GESTIONNAIRE, x.labo)
    assert role_service.has_role(x.jules_dri, Role.MEMBRE, x.dri)
    assert role_service.has_role(x.jules2_dri, Role.MEMBRE, x.dri)

    db.session.flush()

    return x


def test_abandon(request_context, injector, db):
    x = prepare_test(injector, db)
    demande = DemandeRH(gestionnaire=x.joe_gdl)

    wf = LabsterWorkflow(demande, x.joe_gdl)
    wf.start()

    assert wf.current_state() == EN_EDITION
    assert demande.active
    assert wf.possible_transitions() == [ABANDONNER]

    wf.execute_transition(ABANDONNER)
    assert wf.current_state() == ABANDONNEE
    assert not demande.active
    assert not demande.editable
    assert demande.current_owners() == set()


def test_happy_path(mocker, injector, request_context, db, db_session):
    x = prepare_test(injector, db)

    demande = DemandeRH(
        porteur=x.jim_porteur, contact_labco=x.jules_dri, structure=x.labo
    )
    mocker.patch.object(demande, "is_valid", return_value=True)

    assert x.labo.responsables == {x.jake_directeur}

    wf = LabsterWorkflow(demande, x.jim_porteur)
    wf.start()

    assert wf.current_state() == EN_EDITION
    assert demande.active
    assert demande.editable
    assert wf.possible_transitions() == [SOUMETTRE, ABANDONNER, COMMENTER]

    wf.execute_transition(SOUMETTRE)
    assert wf.current_state() == EN_VALIDATION
    assert demande.active
    assert not demande.editable
    assert demande.current_owners() == {x.jake_directeur}
    assert demande.porteur not in demande.structure.responsables
    assert wf.possible_transitions() == [ABANDONNER]

    wf.set_actor(x.jake_directeur)
    assert wf.possible_transitions() == [VALIDER_DIR, REQUERIR_MODIFICATION_DIR]

    wf.execute_transition(VALIDER_DIR)
    assert wf.current_state() == EN_VERIFICATION
    assert demande.active
    assert not demande.editable
    assert demande.current_owners() == {x.jules_dri}
    assert wf.possible_transitions() == [COMMENTER]

    wf.set_actor(x.jules_dri)
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
    assert demande.current_owners() == {x.jules_dri}
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
    assert demande.current_owners() == set()
    assert wf.possible_transitions() == [DESARCHIVER]

    demande.id = None


def test_demande_modification(mocker, request_context, injector, db):
    x = prepare_test(injector, db)

    demande = DemandeRH(porteur=x.jim_porteur, structure=x.labo)
    mocker.patch.object(demande, "is_valid", return_value=True)

    wf = LabsterWorkflow(demande, x.joe_gdl)
    wf.start()

    wf.set_actor(x.jim_porteur)
    wf.execute_transition(SOUMETTRE)
    assert wf.current_state() == EN_VALIDATION

    wf.set_actor(x.jake_directeur)
    wf.execute_transition(REQUERIR_MODIFICATION_DIR)
    assert wf.current_state() == EN_EDITION

    wf.set_actor(x.jim_porteur)
    wf.execute_transition(SOUMETTRE)
    assert wf.current_state() == EN_VALIDATION


def test_demande_modification_dri(mocker, request_context, injector, db):
    x = prepare_test(injector, db)

    demande = DemandeRH(gestionnaire=x.joe_gdl, porteur=x.jim_porteur, structure=x.labo)
    mocker.patch.object(demande, "is_valid", return_value=True)

    wf = LabsterWorkflow(demande, x.joe_gdl)
    wf.start()

    wf.set_actor(x.jim_porteur)
    wf.execute_transition(SOUMETTRE)

    wf.set_actor(x.jake_directeur)
    wf.execute_transition(VALIDER_DIR)

    demande.contact_labco = x.jules_dri

    wf.set_actor(x.jules_dri)
    wf.execute_transition(ACCUSER_RECEPTION)
    wf.execute_transition(REQUERIR_MODIFICATION_DGRTT)

    wf.set_actor(x.jim_porteur)
    wf.execute_transition(SOUMETTRE)

    wf.set_actor(x.jules_dri)
    wf.execute_transition(CONFIRMER_RECEVABILITE_DGRTT)
    wf.execute_transition(REQUERIR_MODIFICATION_DGRTT)

    wf.set_actor(x.jim_porteur)
    wf.execute_transition(SOUMETTRE)

    wf.set_actor(x.jules_dri)
    wf.execute_transition(CONFIRMER_FINALISATION_DGRTT)

    assert not demande.active


def test_gestionnaire_peut_soumettre(mocker, request_context, injector, db):
    # si la structure permet aux gestionnaires de soumettre directement
    # le gestionnaire voit le bouton soumettre (arrive à soumettre).

    x = prepare_test(injector, db)

    demande = DemandeRH(porteur=x.jim_porteur, structure=x.labo)
    mocker.patch.object(demande, "is_valid", return_value=True)

    x.labo.permettre_soummission_directe = True

    wf = LabsterWorkflow(demande, x.joe_gdl)
    wf.start()
    wf.execute_transition(SOUMETTRE)
    assert wf.state == EN_VALIDATION


def test_prendre_la_main_dri(mocker, request_context, injector, db):
    x = prepare_test(injector, db)

    demande = DemandeRH(
        porteur=x.jim_porteur, contact_labco=x.jules_dri, structure=x.labo
    )

    mocker.patch.object(demande, "is_valid", return_value=True)
    mocker.patch.object(demande, "assigne_contact_labco")

    wf = LabsterWorkflow(demande, x.jim_porteur)
    wf.start()
    wf.execute_transition(SOUMETTRE)

    wf.set_actor(x.jake_directeur)
    wf.execute_transition(VALIDER_DIR)
    assert wf.state == EN_VERIFICATION

    # Jules2 veut prendre la main
    wf.set_actor(x.jules2_dri)
    assert wf.possible_transitions() == [
        PRENDRE_LA_MAIN_DGRTT,
        # REJETER_DGRTT,
        # COMMENTER,
    ]
    assert demande.contact_labco == x.jules_dri

    wf.execute_transition(PRENDRE_LA_MAIN_DGRTT)
    assert wf.possible_transitions() == [
        ACCUSER_RECEPTION,
        CONFIRMER_RECEVABILITE_DGRTT,
        REQUERIR_MODIFICATION_DGRTT,
        REJETER_DGRTT,
        COMMENTER,
    ]
    assert demande.contact_labco == x.jules2_dri

    wf.set_actor(x.jules_dri)
    assert wf.possible_transitions() == [
        PRENDRE_LA_MAIN_DGRTT,
        # REJETER_DGRTT,
        # COMMENTER,
    ]
