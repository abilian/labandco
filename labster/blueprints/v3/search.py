from __future__ import annotations

from typing import Dict

import ramda as r
import toolz
import whoosh
import whoosh.query as wq
from abilian.web.search.views import BOOTSTRAP_MARKUP_HIGHLIGHTER, \
    RESULTS_FRAGMENTER
from flask import current_app, request
from marshmallow import Schema, fields
from whoosh.qparser import DisMaxParser

from labster.domain.models.demandes import Demande
from labster.domain.models.faq import FaqEntry
from labster.domain.models.roles import RoleType
from labster.rbac import has_read_access
from labster.util import get_current_user

from . import route

PAGE_SIZE = 25


class FaqEntrySchema(Schema):
    id = fields.String()
    title = fields.String()
    # body = fields.String()
    # category = fields.String()


class OrgUnitSchema(Schema):
    id = fields.String()
    nom = fields.String()


class UserSchema(Schema):
    id = fields.String()
    full_name = fields.String()


class DemandeSchema(Schema):
    id = fields.String()
    nom = fields.String()
    created_at = fields.DateTime()
    type = fields.String()
    porteur = fields.Nested(UserSchema)
    gestionnaire = fields.Nested(UserSchema)
    laboratoire = fields.Nested(OrgUnitSchema)


@route("/search")
def search_api() -> Dict[str, str]:
    page = int(request.args.get("page", 1))
    q = request.args.get("q", "").strip()

    if q:
        results = search_results(q, page)
        demandes, faqs = results["demandes"], results["faqs"]
    else:
        demandes = []
        faqs = []

    ctx = {
        "q": q,
        "demandes": DemandeSchema().dump(demandes, many=True).data,
        "faqs": FaqEntrySchema().dump(faqs, many=True).data,
    }
    return ctx


def search_results(q, page):
    search_kwargs = {"limit": page * PAGE_SIZE}
    results = search(q, **search_kwargs)

    results.formatter = BOOTSTRAP_MARKUP_HIGHLIGHTER
    results.fragmenter = RESULTS_FRAGMENTER
    results = whoosh.searching.ResultsPage(results, page, PAGE_SIZE)

    def is_demande(hit):
        return hit["object_type"].startswith("labster.domain.models.demandes")

    groups = toolz.groupby(is_demande, results)

    demande_ids = [hit["id"] for hit in groups.get(True, [])]
    faq_ids = [hit["id"] for hit in groups.get(False, [])]
    demandes = Demande.query.filter(Demande.id.in_(demande_ids)).all()
    demandes = filter_demandes_by_visibility(demandes)
    faqs = FaqEntry.query.filter(FaqEntry.id.in_(faq_ids)).all()

    return {"demandes": demandes, "faqs": faqs}


def filter_demandes_by_visibility(demandes):
    user = get_current_user()
    return [demande for demande in demandes if has_read_access(user, demande)]


def search(q, **search_args):
    """Interface to search indexes.

    :param q: unparsed search string.
    :param search_args: any valid parameter for
        :meth:`whoosh.searching.Search.search`. This includes `limit`,
        `groupedby` and `sortedby`
    """
    service = current_app.extensions["indexing"]
    index = service.indexes["default"]

    fields = {"name": 1.5, "text": 1.0}
    parser = DisMaxParser(fields, index.schema)
    query = parser.parse(q)

    # security access filter
    user = get_current_user()
    if not user.has_role("dgrtt"):
        roles = {f"user:{user.id}", "all"}
        for role in user.get_roles():
            if role.type in [RoleType.DIRECTION.value, RoleType.GDL.value]:
                structure = role.context
                structures = [structure] + structure.descendants()
                roles |= {f"org:{s.id}" for s in structures}

        terms = [wq.Term("allowed_roles_and_users", role) for role in roles]
        query &= wq.Or(terms)

    with index.searcher(closereader=False) as searcher:
        # 'closereader' is needed, else results cannot by used outside 'with'
        # statement
        return searcher.search(query, **search_args)
