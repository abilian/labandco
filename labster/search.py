from __future__ import annotations

from abilian.services.indexing.adapter import SAAdapter

from labster.domain.models.demandes import Demande
from labster.domain.models.faq import FaqEntry


def register(app):
    index_service = app.services["indexing"]
    index_service.adapters_cls.insert(0, DemandeAdapter)
    index_service.adapters_cls.insert(0, FaqAdapter)


class DemandeAdapter(SAAdapter):
    @staticmethod
    def can_adapt(obj_cls):
        return issubclass(obj_cls, Demande)

    def get_document(self, obj):
        kw = super().get_document(obj)

        indexed_values = []
        for k in ["nom", "name", "no_infolab", "no_eotp"]:
            v = getattr(obj, k)
            if v:
                indexed_values.append(v)

        for v in obj.data.values():
            if isinstance(v, str):
                indexed_values.append(v)

        allowed_roles_and_users = []

        v = obj.porteur
        if v:
            indexed_values.append(v.full_name)
            allowed_roles_and_users += [f"user:{v.id}"]

        v = obj.gestionnaire
        if v:
            indexed_values.append(v.full_name)
            allowed_roles_and_users += [f"user:{v.id}"]

        v = obj.laboratoire
        if v:
            indexed_values.append(v.nom)

        v = obj.structure
        if v:
            indexed_values.append(v.nom)
            allowed_roles_and_users += [f"org:{v.id}"]

        kw["text"] = " ".join(indexed_values)
        kw["name"] = obj.nom

        kw["allowed_roles_and_users"] = " ".join(allowed_roles_and_users)
        return kw


class FaqAdapter(SAAdapter):
    @staticmethod
    def can_adapt(obj_cls):
        return issubclass(obj_cls, FaqEntry)

    def get_document(self, obj):
        kw = super().get_document(obj)

        indexed_values = []
        for k in ["title", "body"]:
            v = getattr(obj, k)
            if v:
                indexed_values.append(v)

        kw["text"] = " ".join(indexed_values)
        kw["allowed_roles_and_users"] = "all"
        return kw
