from __future__ import annotations

from werkzeug.exceptions import Forbidden

from labster.domain.models.demandes import Demande, DemandeRH
from labster.domain.models.profiles import Profile
from labster.domain.models.workflow import EN_EDITION
from labster.domain.services.dgrtt import get_bureau_dgrtt
from labster.domain.services.roles import has_role
from labster.util import get_current_user


def check_read_access(demande: Demande) -> None:
    """Raises 'Forbidden' if current user doesn't have access to demande.
    """
    user = get_current_user()
    if not has_read_access(user, demande):
        raise Forbidden()

    return None


def has_read_access(user: Profile, demande: Demande):
    if user.has_role("recherche"):
        if user in (demande.porteur, demande.gestionnaire):
            return True

        structure = demande.structure

        equipe = structure.equipe
        if equipe and (
            has_role(user, "directeur", equipe)
            or has_role(user, "gestionnaire", equipe)
        ):
            return True

        departement = structure.departement
        if departement and (
            has_role(user, "directeur", departement)
            or has_role(user, "gestionnaire", departement)
        ):
            return True

        laboratoire = structure.laboratoire
        if laboratoire and (
            has_role(user, "directeur", laboratoire)
            or has_role(user, "gestionnaire", laboratoire)
        ):
            return True

        return False

    elif user.has_role("dgrtt"):
        return demande.wf_state != EN_EDITION.id

    else:
        # Should not happen
        return False


def acces_restreint(demande: Demande) -> bool:
    """Retourne True si l'utilisateur courant n'a pas le droit de voir les info
    confidentielles d'un formulaire RH."""
    user = get_current_user()
    bureau_dgrtt = get_bureau_dgrtt(user)

    if isinstance(demande, DemandeRH):
        if bureau_dgrtt and bureau_dgrtt.id == "CT":
            return False
        if user.has_role("direction dgrtt"):
            return False
        if user.has_role("alc"):
            return False

        if user in demande.owners:
            return False

        labo = demande.laboratoire
        if has_role(user, "directeur", labo):
            return False

        # TODO: c'est quoi les règles à présent ?
        # dept = demande.departement
        # if dept:
        #     info = wf_info(dept)
        #     if info["validation_dept"] and has_role(user, "directeur", dept):
        #         return False
        #
        # equipe = demande.equipe
        # if equipe:
        #     info = wf_info(equipe)
        #     if info["validation_equipe"] and has_role(user, "directeur", equipe):
        #         return False

        return True

    return False
