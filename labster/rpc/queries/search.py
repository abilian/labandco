from __future__ import annotations

import toolz
from abilian.web.search.views import BOOTSTRAP_MARKUP_HIGHLIGHTER, \
    RESULTS_FRAGMENTER
from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from marshmallow import Schema, fields
from whoosh.qparser import DisMaxParser
from whoosh.searching import ResultsPage

from labster.di import injector
from labster.domain2.model.demande import Demande
from labster.domain.models.faq import FaqEntry
from labster.extensions import whoosh
from labster.rbac import has_read_access, is_membre_dri
from labster.security import get_current_profile
from labster.types import JSONDict

PAGE_SIZE = 25

db = injector.get(SQLAlchemy)


@method
def search_api(q: str, page=1) -> JSONDict:
    q = q.strip()

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
    results = ResultsPage(results, page, PAGE_SIZE)

    def is_demande(hit):
        return hit["cls"] == "Demande"

    groups = toolz.groupby(is_demande, results)

    demande_ids = [hit["id"] for hit in groups.get(True, [])]
    faq_ids = [hit["id"] for hit in groups.get(False, [])]

    demandes = db.session.query(Demande).filter(Demande.id.in_(demande_ids)).all()
    demandes = filter_demandes_by_visibility(demandes)

    faqs = FaqEntry.query.filter(FaqEntry.id.in_(faq_ids)).all()

    return {"demandes": demandes, "faqs": faqs}


class FaqEntrySchema(Schema):
    id = fields.String()
    title = fields.String()
    # body = fields.String()
    # category = fields.String()


class StructureSchema(Schema):
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
    wf_state = fields.String()
    icon_class = fields.String()

    porteur = fields.Nested(UserSchema)
    gestionnaire = fields.Nested(UserSchema)
    structure = fields.Nested(StructureSchema)


def filter_demandes_by_visibility(demandes):
    return [demande for demande in demandes if has_read_access(demande)]


def search(q, **search_args):
    """Interface to search indexes.

    :param q: unparsed search string.
    :param search_args: any valid parameter for
        :meth:`whoosh.searching.Search.search`. This includes `limit`,
        `groupedby` and `sortedby`
    """
    index = whoosh.index

    fields = {"name": 1.5, "text": 1.0}
    parser = DisMaxParser(fields, index.schema)
    query = parser.parse(q)

    # security access filter
    user = get_current_profile()

    if not is_membre_dri(user):
        pass
        # TODO
        # roles = {f"user:{user.id}", "all"}
        # for role in user.get_roles():
        #     if role.type in [RoleType.DIRECTION.value, RoleType.GDL.value]:
        #         structure = role.context
        #         structures = [structure] + structure.descendants()
        #         roles |= {f"org:{s.id}" for s in structures}
        #
        # terms = [wq.Term("allowed_roles_and_users", role) for role in roles]
        # query &= wq.Or(terms)

    with index.searcher(closereader=False) as searcher:
        # 'closereader' is needed, else results cannot by used outside 'with'
        # statement
        return searcher.search(query, **search_args)
