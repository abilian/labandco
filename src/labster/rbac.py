from __future__ import annotations

from flask import current_app
from werkzeug.exceptions import Forbidden, NotFound, abort

from labster.auth import AuthContext
from labster.di import injector
from labster.domain2.model.demande import Demande, DemandeConvention, DemandeRH
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import Structure, StructureRepository
from labster.domain2.model.type_structure import FA, LA
from labster.domain2.services.contacts import ContactService, ContactType
from labster.domain2.services.roles import Role
from labster.domain2.services.workflow.states import EN_EDITION
from labster.ldap.constants import DRI_DN, DRV_DNS
from labster.security import get_current_profile

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)


#
# DR&I
#
def is_membre_dri(user: Profile) -> bool:
    dri = structure_repo.get_by_dn(DRI_DN)
    return user.has_role(Role.MEMBRE, dri)


#
# DRV
#
def is_membre_drv(user: Profile, structure: Structure | None = None) -> bool:
    drv = get_drv_membership(user)
    if not drv:
        return False

    if not structure:
        return True

    fac = drv.parent
    assert fac
    if structure == fac or fac in structure.ancestors:
        return True

    return False


def get_drv_membership(user: Profile) -> Structure | None:
    for drv_dn in DRV_DNS.values():
        drv = structure_repo.get_by_dn(drv_dn)

        # For tests
        if not drv:
            continue

        for role in [Role.MEMBRE, Role.MEMBRE_RATTACHE, Role.MEMBRE_AFFECTE]:
            if user.has_role(role, drv):
                return drv

    return None


#
# Read access
#
def check_read_access(demande: Demande | None):
    """Raises 'Forbidden' if current user doesn't have access to demande."""
    if not demande:
        abort(404)
    if not has_read_access(demande):
        raise Forbidden()


def has_read_access(demande: Demande) -> bool:
    user = get_current_profile()

    if user in (demande.porteur, demande.gestionnaire, demande.contact_labco):
        return True

    if user.has_role(Role.ADMIN_CENTRAL):
        return True

    wf_states = {
        state["new_state"] for state in demande.wf_history if "new_state" in state
    }

    # DRI & DRV
    if wf_states != {EN_EDITION.id}:
        if is_membre_dri(user):
            return True
        if demande.structure and is_membre_drv(user, demande.structure):
            return True

    if is_responsable_ou_gestionnaire(user, demande):
        return True

    if is_responsable_structure_concernee(user, demande):
        return True

    if is_contributeur(user, demande):
        return True

    return False


def is_responsable_ou_gestionnaire(user: Profile, demande: Demande) -> bool:
    if demande.structure:
        structures = [demande.structure] + demande.structure.ancestors
        for structure in structures:
            if user.has_role(Role.RESPONSABLE, structure):
                return True
            if user.has_role(Role.GESTIONNAIRE, structure):
                return True

    return False


def is_gestionnaire(user: Profile, demande: Demande) -> bool:
    if demande.structure:
        structures = [demande.structure] + demande.structure.ancestors
        for structure in structures:
            if user.has_role(Role.GESTIONNAIRE, structure):
                return True

    return False


def is_contributeur(user: Profile, demande: Demande) -> bool:
    for d in demande.data.get("contributeurs", []):
        contributeur_id = d["value"]
        contributeur = profile_repo.get_by_id(contributeur_id)
        if not contributeur:
            continue
        if contributeur == user:
            return True

    return False


def is_responsable_structure_concernee(user: Profile, demande: Demande) -> bool:
    for d in demande.data.get("structures_concernees", []):
        structure_id = d["value"]
        structure = structure_repo.get_by_id(structure_id)
        if not structure:
            continue
        if user.has_role(Role.RESPONSABLE, structure):
            return True

    return False


#
# Write access
#
def check_write_access(demande: Demande | None):
    """Raises 'Forbidden' if current user doesn't have write access to
    demande."""
    if not demande:
        abort(404)
    if not has_write_access(demande):
        raise Forbidden()


def has_write_access(demande: Demande) -> bool:
    if not demande.editable:
        return False

    user = get_current_profile()

    if user in {demande.porteur, demande.gestionnaire}:
        return True

    if is_contributeur(user, demande):
        return True

    return False


def feuille_cout_editable(demande: Demande) -> bool:
    """
    Feuille de coût : celle-ci devient modifiable par le Contact Lab&Co lorsqu'il a la main.
    Chaque enregistrement, par le Porteur, un Contributeur, un Gestionnaire ou un Contact...

    https://trello.com/c/O702eRzQ/
    """
    if not isinstance(demande, DemandeConvention):
        return False

    user = get_current_profile()
    if user in (demande.porteur, demande.gestionnaire, demande.contact_labco):
        return True

    if is_gestionnaire(user, demande):
        return True

    if is_contributeur(user, demande):
        return True

    return False


def check_can_add_pj(demande: Demande | None):
    """Raises 'Forbidden' if current user doesn't have write access to
    demande."""
    if not demande:
        abort(404)
    if not can_add_pj(demande):
        raise Forbidden()


def can_add_pj(demande: Demande) -> bool:
    user = get_current_profile()
    if user in (demande.porteur, demande.gestionnaire, demande.contact_labco):
        return True

    if is_gestionnaire(user, demande):
        return True

    if is_contributeur(user, demande):
        return True

    if user in demande.valideurs():
        return True

    return False


#
# Other (demandes)
#
def can_duplicate(demande):
    user = get_current_profile()
    return user in {demande.gestionnaire, demande.porteur}


def acces_restreint(demande: Demande) -> bool:
    """Retourne True si l'utilisateur courant n'a pas le droit de voir les info
    confidentielles d'un formulaire RH."""

    if not isinstance(demande, DemandeRH):
        return False

    user = get_current_profile()

    if user in {demande.porteur, demande.gestionnaire, demande.contact_labco}:
        return False

    if user.has_role(Role.ADMIN_CENTRAL):
        return False

    # Les responsables "ascendants" ne voient pas le détail
    # sauf pour les structures "concernées".
    # NB: le labo est toujours "concerné"
    if demande.structure:
        if user.has_role(Role.RESPONSABLE, demande.structure):
            return False

    dri = structure_repo.get_by_dn(DRI_DN)
    if user.has_role(Role.RESPONSABLE, dri):
        return False

    structures = demande.get_structure_concernees()
    for structure in structures:
        if user.has_role(Role.RESPONSABLE, structure):
            return False

    # Responsable facultaire et admin facultaire
    if demande.structure:
        structures.add(demande.structure)

    for structure in structures:
        ancestors = structure.ancestors
        for ancestor in ancestors:
            if ancestor.type != FA:
                continue
            if user.has_role(Role.RESPONSABLE, ancestor):
                return False

            # Admin facultaire
            for sous_structure in ancestor.children:
                if sous_structure.sigle.startswith("DRV "):
                    if user.has_role(Role.ADMIN_LOCAL, sous_structure):
                        return False

    contact_service = injector.get(ContactService)
    mapping = contact_service.get_mapping()
    for d in mapping.values():
        if d.get(ContactType.CONTACT_RH) == user:
            return False

    return True


#
# Structures
#
def get_permissions_for_structure(structure: Structure) -> set[str]:
    if current_app.config.get("TESTING"):
        return set()

    user = get_current_profile()
    permissions = set()

    # cas admin central
    if user.has_role(Role.ADMIN_CENTRAL):
        return {"P1", "P2", "P3", "P4", "P5", "P6"}

    # P1: Infos clés - Edition
    # Admin local: Pour S seulement (et ses départements et équipes si S est un Labo)
    # Admin facultaire: De F et de toute structure descendante

    # P2: Hiérarchie des structures – Edition de structures existantes
    # Admin local: Non, à l’exception des départements et équipes si S est un Labo
    # Admin facultaire: De F et de toute structure descendante

    # P3: Hiérarchie des structures – Création / suppression de structures virtuelles (ex : Carnot)
    # Admin local: Non, à l’exception des départements et équipes si S est un Labo
    # Admin facultaire: Non, à l’exception des départements et équipes des laboratoires
    # descendant de F

    # P4: Membre – Edition pour rattachement d’un utilisateur
    # Admin local: Pour S seulement
    # Admin facultaire: Pour F et toute structure descendante

    # P5: Rôles - Edition
    # Admin local: Pour S seulement (et ses départements et équipes si S est un Labo)
    # Admin facultaire: Pour F et toute structure descendante

    # P6: Contacts Lab & Co - Edition
    # Admin local: Non
    # Admin facultaire: Pour F et toute structure descendante

    # Cas admin facultaire
    for ancestor in [structure] + structure.ancestors:
        if user.has_role(Role.ADMIN_LOCAL, ancestor) and ancestor.type == FA:
            permissions.update(["P1", "P2", "P3", "P4", "P5", "P6"])
            return permissions

    # Cas admin local "normal"
    if user.has_role(Role.ADMIN_LOCAL, structure):
        permissions.update(["P3", "P4", "P5"])

    for ancestor in structure.ancestors:
        if user.has_role(Role.ADMIN_LOCAL, ancestor) and ancestor.type == LA:
            permissions.update(["P1", "P2", "P3", "P4", "P5"])

    return permissions


def has_permission(structure: Structure, permission: str) -> bool:
    if current_app.config.get("TESTING"):
        return True

    permissions = get_permissions_for_structure(structure)
    return permission in permissions


def check_permission(structure: Structure | None, permission: str) -> None:
    if not structure:
        raise NotFound()

    if not has_permission(structure, permission):
        raise Forbidden()


def check_structure_editable(structure: Structure | None):
    check_permission(structure, "P1")


def check_can_edit_roles(structure: Structure | None):
    check_permission(structure, "P5")


def check_can_edit_contacts(structure: Structure | None):
    check_permission(structure, "P6")


def is_admin_local(structure: Structure):
    profile = get_current_profile()
    for ancestor in [structure] + structure.ancestors:
        if profile.has_role(Role.ADMIN_LOCAL, ancestor):
            return True
    return False


def can_view_stats():
    auth_context = injector.get(AuthContext)
    user = auth_context.current_profile

    # For tests
    if not user:
        return True

    if user.has_role(Role.RESPONSABLE, "*"):
        return True
    if user.has_role(Role.ADMIN_CENTRAL):
        return True

    return False
