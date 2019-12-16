from __future__ import annotations

from typing import Optional

from werkzeug.exceptions import Forbidden, abort

from labster.auth import AuthContext
from labster.di import injector
from labster.domain2.model.demande import Demande, DemandeConvention, DemandeRH
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure, StructureRepository
from labster.domain2.model.type_structure import DE, EQ, LA
from labster.domain2.services.contacts import ContactService, ContactType
from labster.domain2.services.roles import Role
from labster.domain2.services.workflow import EN_EDITION
from labster.ldap.constants import DRI_DN, DRV_DNS, FAC_DNS
from labster.security import get_current_profile

structure_repo = injector.get(StructureRepository)


def is_membre_dri(user: Profile) -> bool:
    dri = structure_repo.get_by_dn(DRI_DN)
    return user.has_role(Role.MEMBRE, dri)


def get_drv_membership(user: Profile) -> Optional[Structure]:
    for drv_dn in DRV_DNS.values():
        drv = structure_repo.get_by_dn(drv_dn)
        assert drv
        if user.has_role(Role.MEMBRE, drv):
            return drv
    return None


def is_membre_drv(user: Profile) -> bool:
    return get_drv_membership(user) is not None


def check_read_access(demande: Optional[Demande]):
    """Raises 'Forbidden' if current user doesn't have access to demande.
    """
    if not demande:
        abort(404)
    if not has_read_access(demande):
        raise Forbidden()


def has_read_access(demande: Demande) -> bool:
    user = get_current_profile()

    if user in (demande.porteur, demande.gestionnaire):
        return True

    # DRI
    if is_membre_dri(user) and demande.wf_state != EN_EDITION.id:
        return True

    # DRV
    drv = get_drv_membership(user)
    if drv:
        fac = drv.parent
        assert fac
        if demande.structure in {fac} | fac.descendants:
            return True

    # TODO: verifier ce qu'on fait pour le cas des sous-structures
    if user.has_role(Role.GESTIONNAIRE, demande.structure):
        return True

    if user.has_role(Role.RESPONSABLE, demande.structure):
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

    structure = demande.structure
    if user.has_role(Role.GESTIONNAIRE, structure):
        return True

    # TODO: contributeur
    # TODO: un contact ?
    return False


def acces_restreint(demande: Demande) -> bool:
    """Retourne True si l'utilisateur courant n'a pas le droit de voir les info
    confidentielles d'un formulaire RH."""

    if not isinstance(demande, DemandeRH):
        return False

    user = get_current_profile()
    if user in demande.owners:
        return False

    if user.has_role(Role.ADMIN_CENTRAL):
        return False

    if demande.structure:
        structures_parentes = demande.structure.ancestors
        for structure in structures_parentes:
            if user.has_role(Role.RESPONSABLE, structure):
                return False

    dri = structure_repo.get_by_dn(DRI_DN)
    if user.has_role(Role.RESPONSABLE, dri):
        return False

    contact_service = injector.get(ContactService)
    mapping = contact_service.get_mapping()
    for d in mapping.values():
        if ContactType.CONTACT_RH in d.keys():
            return False

    return True


def structure_is_editable(structure: Optional[Structure]):
    """Cf. https://trello.com/c/cRUEKsVv/
    """
    if not structure:
        abort(404)

    auth_context = injector.get(AuthContext)
    user = auth_context.current_profile

    # For tests
    if not user:
        return True

    if user.has_role(Role.ADMIN_CENTRAL):
        return True

    if structure.type in [LA, DE, EQ]:
        return user.has_role(Role.ADMIN_LOCAL, structure)

    return False


def check_structure_editable(structure: Optional[Structure]):
    if not structure_is_editable(structure):
        raise Forbidden()


def can_edit_roles(structure: Optional[Structure]):
    if not structure:
        abort(404)

    auth_context = injector.get(AuthContext)
    user = auth_context.current_profile

    # For tests
    if not user:
        return True

    if user.has_role(Role.ADMIN_CENTRAL):
        return True

    for fac_dn in FAC_DNS:
        fac = structure_repo.get_by_dn(fac_dn)
        assert fac
        if user.has_role(Role.ADMIN_LOCAL, fac):
            if structure in {fac} | fac.descendants:
                return True

    return False


def check_can_edit_roles(structure: Optional[Structure]):
    if not can_edit_roles(structure):
        raise Forbidden()
