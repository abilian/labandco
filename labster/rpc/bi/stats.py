from __future__ import annotations

from pprint import pprint
from typing import List

import dateutil.parser
import pandas as pd
import ramda as r
from jsonrpcserver import method
from werkzeug.exceptions import Forbidden

from labster.auth import AuthContext
from labster.bi.model import StatsLine
from labster.di import injector
from labster.domain.models.demandes import AVENANT_CONVENTION, CONVENTION, \
    PI_INVENTION, PI_LOGICIEL, RECRUTEMENT
from labster.domain.models.unites import OrgUnit
from labster.domain.models.workflow import ALL_STATES
from labster.rpc.registry import context_for

from .form import get_selectors
from .util import mes_structures

SECONDS_IN_DAY = 60.0 * 60 * 24
ALLOWED_ROLES = ["alc", "directeur", "chef de bureau", "gouvernance", "direction dgrtt"]


@method
@context_for("bi")
def get_bi_context():
    user = injector.get(AuthContext).current_user

    if user.is_anonymous or not user.has_role(ALLOWED_ROLES):
        raise Forbidden()

    ctx = get_stats2(user)
    ctx["selectors"] = get_selectors()
    return ctx


@method
def get_stats(**args):
    user = injector.get(AuthContext).current_user

    if user.is_anonymous or not user.has_role(ALLOWED_ROLES):
        raise Forbidden()

    args2 = {}
    pprint(args)
    for arg_name, arg_value in args.items():
        if not arg_value:
            continue
        if isinstance(arg_value, List):
            value = r.map(lambda x: x["value"], arg_value)
        else:
            value = arg_value["value"]
        args2[arg_name] = value

    return get_stats2(user, **args2)


def get_stats2(
    user,
    periode_debut=None,
    periode_fin=None,
    type_demande=None,
    type_recrutement=None,
    financeur=None,
    structure_id=None,
    porteur_id=None,
):

    query = StatsLine.query

    if periode_debut:
        query = query.filter(StatsLine.date_soumission >= periode_debut)

    if periode_fin:
        query = query.filter(StatsLine.date_soumission <= periode_fin)

    if type_demande:
        query = query.filter(StatsLine.type_demande.in_(type_demande))

    if type_recrutement:
        query = query.filter(StatsLine.type_recrutement.in_(type_recrutement))

    if financeur:
        query = query.filter(StatsLine.financeur.in_(financeur))

    if porteur_id not in ("", "None", None):
        query = query.filter(StatsLine.porteur_id == porteur_id)

    if structure_id not in ("", "None", None):
        structure_id = int(structure_id)
        if user.has_role("recherche"):
            structures = mes_structures(user)
            if structure_id not in {s.id for s in structures}:
                raise Forbidden()

        structure = OrgUnit.query.get(structure_id)
        descendant_ids = [s.id for s in structure.descendants()]
        query = query.filter(
            StatsLine.structure_id.in_([structure_id] + descendant_ids)
        )

    elif user.has_role("directeur"):
        structures = mes_structures(user)
        query = query.filter(StatsLine.structure_id.in_([s.id for s in structures]))

    # Stats
    totals = {}
    for state in ALL_STATES:
        state_id = state.id.lower()
        totals["nb_" + state_id] = query.filter(StatsLine.wf_state == state.id).count()

    totals["nb_en_cours"] = sum(
        totals[id]
        for id in [
            "nb_en_edition",
            "nb_en_validation",
            "nb_en_verification",
            "nb_en_instruction",
        ]
    )
    totals["nb_archivee"] = sum(
        totals[id] for id in ["nb_traitee", "nb_rejetee", "nb_abandonnee"]
    )
    totals["nb_total"] = totals["nb_en_cours"] + totals["nb_archivee"]
    assert totals["nb_total"] == query.count()

    totals = {k: int(v) for k, v in totals.items()}

    stats = {
        "conventions": make_conventions_stats(query),
        "rh": make_rh_stats(query),
        "avenants": make_avenants_stats(query),
        "pi_logiciel": make_pi_logiciel_stats(query),
        "pi_invention": make_pi_invention_stats(query),
        "duree_traitement": make_duree_traitement_stats(query),
    }

    ctx = {
        "totals": totals,
        "stats": stats,
    }

    return ctx


def parse_date(s):
    return dateutil.parser.parse(s)


def make_rh_stats(query):
    lines = query.filter(StatsLine.type_demande == RECRUTEMENT).all()
    result = make_stats(lines, ["duree", "salaire_brut_mensuel", "cout_total_mensuel"])
    result["count"] = len(lines)
    return result


def make_conventions_stats(query):
    lines = query.filter(StatsLine.type_demande == CONVENTION).all()
    result = make_stats(lines, ["montant", "recrutements_prev", "duree"])
    result["count"] = len(lines)
    return result


def make_avenants_stats(query):
    lines = query.filter(StatsLine.type_demande == AVENANT_CONVENTION).all()
    result = make_stats(lines, [])
    result["count"] = len(lines)
    return result


def make_pi_logiciel_stats(query):
    lines = query.filter(StatsLine.type_demande == PI_LOGICIEL).all()
    result = make_stats(lines, [])
    result["count"] = len(lines)
    return result


def make_pi_invention_stats(query):
    lines = query.filter(StatsLine.type_demande == PI_INVENTION).all()
    result = make_stats(lines, [])
    result["count"] = len(lines)
    return result


def make_duree_traitement_stats(query):
    def duree_traitement(line):
        if line.date_soumission and line.date_finalisation:
            dt = line.date_finalisation - line.date_soumission
            days = dt.days + dt.seconds / SECONDS_IN_DAY
            return days
        else:
            return None

    lines = query.all()
    series = pd.Series([duree_traitement(line) for line in lines])
    return r.map(
        format_float,
        [
            series.mean(),
            series.median(),
            series.std(),
            series.min(),
            series.max(),
            series.sum(),
        ],
    )


def make_stats(lines, attrs):
    result = {}
    for attr in attrs:
        series = pd.Series([getattr(line, attr) for line in lines])
        result[attr] = r.map(
            format_float,
            [
                series.mean(),
                series.median(),
                series.std(),
                series.min(),
                series.max(),
                series.sum(),
            ],
        )
    return result


def format_float(x):
    return "{:,.2f}".format(float(x)).replace(",", "\u00A0").replace(".", ",")
