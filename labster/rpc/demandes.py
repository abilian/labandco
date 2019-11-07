from __future__ import annotations

import re
import traceback
from datetime import date, timedelta
from typing import Any, Callable, Dict, List, Optional

from flask import request
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from webargs import fields
from webargs.flaskparser import parser
from werkzeug.exceptions import Forbidden

import labster.domain.services.dgrtt as dgrtt_service
from labster.blueprints.util import get_current_user, strip_accents
from labster.domain.models.demandes import Demande
from labster.domain.models.profiles import Profile
from labster.domain.models.roles import RoleType
from labster.types import JSON
from labster.util import url_for

QUERY = Demande.query.options(
    joinedload(Demande.structure),
    joinedload(Demande.contact_dgrtt),
    joinedload(Demande.gestionnaire),
    joinedload(Demande.porteur),
)


# @route("/demandes")
# def demandes() -> JSON:
#     specs = {"scope": fields.Str(missing="all"), "archives": fields.Bool(missing=False)}
#     args = parser.parse(specs, request)
#     scope = args["scope"]
#     archives = args["archives"]
#     user = get_current_user()
#
#     role = scope.split("/")[0]
#     if not user.has_role(role):
#         raise Forbidden()
#
#     name = strip_accents(role)
#     name = re.sub("[- /]", "_", name)
#     if "/" in scope:
#         n = int(scope.split("/")[1])
#         name += f"_{n}"
#
#     if archives:
#         function_name = f"archives_{name}"
#     else:
#         function_name = f"demandes_{name}"
#
#     func: Callable[[Profile], List[Demande]] = globals()[function_name]
#     demandes = func(user)
#     demandes = sorted(demandes, key=lambda d: d.created_at, reverse=True)
#     return demandes_to_json(demandes, user)
#
#
# @route("/tasks")
# def tasks() -> JSON:
#     user = get_current_user()
#     demandes = mes_taches(user)
#     return demandes_to_json(demandes, user)
#
#
# @route("/mes_demandes")
# def mes_demandes_json() -> JSON:
#     user = get_current_user()
#     demandes = mes_demandes(user)
#     return demandes_to_json(demandes, user)
#
#
# #
# # Demandes actives
# #
def demandes_porteur(user: Profile) -> List[Demande]:
    return (
        QUERY.filter(Demande.porteur == user)
        .filter(Demande.active == True)
        .order_by(Demande.created_at.desc())
        .all()
    )


def demandes_gestionnaire(user: Profile) -> List[Demande]:
    return (
        QUERY.filter(Demande.gestionnaire == user)
        .filter(Demande.active == True)
        .order_by(Demande.created_at.desc())
        .all()
    )


def demandes_contact_dgrtt(user: Profile) -> List[Demande]:
    return (
        QUERY.filter(Demande.contact_dgrtt == user)
        .filter(Demande.active == True)
        .order_by(Demande.created_at.desc())
        .all()
    )


def demandes_directeur(user: Profile) -> List[Demande]:
    assert user.stucture_dont_je_suis_le_directeur

    ma_structure = user.stucture_dont_je_suis_le_directeur
    mes_structures = [ma_structure] + ma_structure.descendants()
    ids = [l.id for l in mes_structures]

    return (
        QUERY.filter(Demande.structure_id.in_(ids))
        .filter(Demande.active == True)
        .order_by(Demande.created_at.desc())
        .all()
    )


def demandes_gestionnaire_2(user: Profile) -> List[Demande]:
    roles = user.get_roles(RoleType.GDL)
    mes_structures = [r.context for r in roles]
    for s in mes_structures[:]:
        mes_structures += s.descendants()

    return (
        QUERY.filter(Demande.structure_id.in_([s.id for s in mes_structures]))
        .filter(Demande.active == True)
        .order_by(Demande.created_at.desc())
        .all()
    )


def demandes_contact_dgrtt_2(user: Profile) -> List[Demande]:
    return demandes_de_mes_structures_de_recherche(user)


def demandes_referent(user: Profile) -> List[Demande]:
    demandes = (
        QUERY.filter(Demande.contact_dgrtt == user)
        .filter(Demande.active == True)
        .order_by(Demande.created_at.desc())
        .all()
    )
    labos = dgrtt_service.labos_dont_je_suis_referent(user)
    return [d for d in demandes if d.laboratoire in labos]


def demandes_chef_de_bureau(user: Profile) -> List[Demande]:
    bureau_dgrtt = dgrtt_service.get_bureau_dgrtt(user)
    assert bureau_dgrtt
    contacts_dgrtt = dgrtt_service.get_membres_du_bureau_dgrtt(bureau_dgrtt)
    contacts_dgrtt_ids = [c.id for c in contacts_dgrtt]
    return (
        QUERY.filter(Demande.contact_dgrtt_id.in_(contacts_dgrtt_ids))
        .filter(Demande.active == True)
        .order_by(Demande.created_at.desc())
        .all()
    )


def demandes_dgrtt(user: Profile) -> List[Demande]:
    return toutes_les_demandes_a_la_dgrtt()


#
# Archives
#
def archives_dgrtt(user: Profile) -> List[Demande]:
    return mes_demandes(user, archived=True)


def archives_dgrtt_2(user: Profile) -> List[Demande]:
    return toutes_les_demandes_a_la_dgrtt(actives=False)


def archives_directeur(user: Profile) -> List[Demande]:
    ma_structure = user.stucture_dont_je_suis_le_directeur
    assert ma_structure
    mes_structures = [ma_structure] + ma_structure.descendants()
    ids = [structure.id for structure in mes_structures]

    query = Demande.query.filter(Demande.active == False)
    return query.filter(Demande.structure_id.in_(ids)).all()


def archives_porteur(user: Profile) -> List[Demande]:
    return mes_demandes(user, archived=True)


def archives_gestionnaire(user: Profile) -> List[Demande]:
    return mes_demandes(user, archived=True)


def archives_gestionnaire_2(user: Profile) -> List[Demande]:
    return demandes_de_mes_structures_de_recherche(user, actives=False)


#
#
#
def mes_demandes(user, archived: bool = False, all: bool = False) -> List[Demande]:
    query = QUERY.filter(
        or_(
            (Demande.porteur == user),
            (Demande.contact_dgrtt == user),
            (Demande.gestionnaire == user),
        )
    )
    if archived:
        query = query.filter(Demande.active == False)
    elif not all:
        query = query.filter(Demande.active == True)
    query = query.order_by(Demande.created_at.desc())
    return query.all()


def toutes_les_demandes_a_la_dgrtt(actives=True) -> List[Demande]:
    from .demandes import Demande

    return (
        QUERY.filter(Demande.active == actives)
        .filter(Demande.contact_dgrtt != None)
        .order_by(Demande.created_at.desc())
        .all()
    )


def demandes_de_mes_structures_de_recherche(
    user: Profile, actives=True
) -> List[Demande]:
    assert user.has_role("contact dgrtt")

    mes_structures = set(user.perimetre_dgrtt)
    for s in list(mes_structures)[:]:
        mes_structures.update(s.descendants())
    mes_structures = set(mes_structures)

    if not mes_structures:
        return []
    return (
        QUERY.filter(Demande.structure_id.in_([l.id for l in mes_structures]))
        .filter(Demande.contact_dgrtt != None)
        .filter(Demande.active == actives)
        .order_by(Demande.created_at.desc())
        .all()
    )


def mes_taches(user) -> List[Demande]:
    """Retourne la liste des demandes pour lesquels l'utilisateur a une
    action à réaliser."""
    query = QUERY.filter(Demande.active == True).order_by(Demande.created_at.desc())

    if user.has_role("directeur"):
        assert user.stucture_dont_je_suis_le_directeur
        ma_structure = user.stucture_dont_je_suis_le_directeur
        mes_structures = [ma_structure] + ma_structure.descendants()
        ids = [l.id for l in mes_structures]
        query = query.filter(Demande.structure_id.in_(ids))

    elif user.has_role("porteur"):
        query = query.filter(Demande.porteur == user)

    elif user.has_role("gestionnaire"):
        query = query.filter(Demande.gestionnaire == user)

    else:
        return []

    demandes = query.all()

    def is_task(demande):
        workflow = demande.get_workflow(user)
        state = workflow.current_state()
        return user in state.task_owners(workflow)

    demandes = [d for d in demandes if is_task(d)]
    return demandes


def mes_taches_en_retard(user) -> List[Demande]:
    demandes = mes_taches(user)
    demandes = list(filter(lambda d: d.wf_retard > 0, demandes))
    demandes = sorted(demandes, key=lambda d: d.wf_retard, reverse=True)
    return demandes


#
# Serialization
#
def demandes_to_json(
    demandes: List[Demande], user: Profile
) -> Dict[str, List[Dict[str, Any]]]:
    result = []

    for demande in demandes:
        try:
            row = demande_to_json(demande, user)
            result.append(row)
        except Exception:
            traceback.print_exc()

    return {"demandes": result}


def demande_to_json(demande: Demande, user: Profile) -> Dict[str, Any]:
    row = {}
    workflow = demande.get_workflow(user)
    row["created_at"] = format_date(demande.created_at)
    row["__created_at__"] = isoformat_date(demande.created_at)
    row["icon_class"] = demande.icon_class
    row["type"] = demande.type
    row["url"] = url_for(demande)
    row["nom"] = demande.nom or demande.titre
    row["age"] = demande.age

    row["date_debut"] = format_date(demande.date_debut)
    row["__date_debut__"] = isoformat_date(demande.date_debut)

    date_soumission = demande.date_soumission
    if date_soumission:
        duree_traitement: timedelta = date.today() - date_soumission
        row["date_soumission"] = (
            format_date(date_soumission) + f" ({duree_traitement.days}j)"
        )
        row["__date_soumission__"] = isoformat_date(date_soumission)
    else:
        row["date_soumission"] = ""
        row["__date_soumission__"] = ""

    row["retard"] = demande.retard
    row["no_infolab"] = demande.no_infolab

    for k in ("porteur", "gestionnaire", "contact_dgrtt"):
        profile = getattr(demande, k)
        if profile:
            row[k] = profile.full_name
            row[k + "_url"] = url_for(profile)
            nom = getattr(profile, "nom", "")
            prenom = getattr(profile, "prenom", "")
            # helps sorting in JS
            row[k + "_nom"] = f"{nom}, {prenom}"
        else:
            row[k] = ""
            row[k + "_url"] = ""
            row[k + "_nom"] = ""

    structure = demande.structure
    if structure:
        row["structure"] = structure.sigle_ou_nom
        row["structure_url"] = url_for(structure)
        laboratoire = structure.laboratoire
        row["laboratoire"] = laboratoire.sigle_ou_nom
        row["laboratoire_url"] = url_for(laboratoire)
    else:
        row["structure"] = ""
        row["structure_url"] = ""
        row["laboratoire"] = ""
        row["laboratoire_url"] = ""

    # Workflow
    state = demande.get_state()
    row["etat"] = state.label_short
    row["prochaine_action"] = state.next_action
    owners = workflow.current_owners()
    if owners:
        row["owner"] = f"{owners[0].nom}, {owners[0].prenom}"
    else:
        row["owner"] = ""

    return row


def format_date(d: Optional[date]) -> str:
    if d:
        return d.strftime("%d/%m/%Y")
    else:
        return ""


def isoformat_date(d: Optional[date]) -> str:
    if d:
        return d.isoformat()
    else:
        return ""
