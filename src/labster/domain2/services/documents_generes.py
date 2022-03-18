""""""
from __future__ import annotations

from os.path import dirname
from typing import Any

from flask import render_template
from flask_weasyprint import HTML

from labster.di import injector
from labster.domain2.model.demande import DemandeRH
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.calculs_couts import get_ctx_for_demande

structure_repo = injector.get(StructureRepository)


def devis_rh(demande: DemandeRH):
    ctx = get_ctx_for_demande(demande)
    ctx.update(additional_ctx_for_demande(demande))

    ctx["css_rules"] = open(dirname(__file__) + "/../../static/print/devis.css").read()
    html = render_template("documents-generes/devis-rh.html", **ctx)
    pdf = HTML(string=html).write_pdf()
    return pdf


def lettre_commande_rh(demande: DemandeRH):
    ctx = get_ctx_for_demande(demande)
    ctx.update(additional_ctx_for_demande(demande))

    if demande.data.get("nature_du_recrutement") == "Doctorant":
        template = "documents-generes/lettre-commande-recrutement-doctorant.html"
    else:
        template = "documents-generes/lettre-commande-recrutement.html"
    html = render_template(template, **ctx)
    pdf = HTML(string=html).write_pdf()
    return pdf


def additional_ctx_for_demande(demande: DemandeRH):
    ctx: dict[str, Any] = {}

    structure_inconnue = {
        "nom": "Structure inconnue",
        "signataire": None,
    }
    ctx["structure_d_accueil"] = demande.structure or structure_inconnue

    d = demande.data.get("structure_financeuse")
    if d:
        id = d["value"]
        ctx["structure_financeuse"] = structure_repo.get_by_id(id)
    else:
        ctx["structure_financeuse"] = demande.structure

    structure_financeuse = ctx["structure_financeuse"]

    if structure_financeuse:
        ctx["signataire"] = structure_financeuse.signataire
    else:
        ctx["structure_financeuse"] = structure_inconnue
        ctx["signataire"] = None

    return ctx
