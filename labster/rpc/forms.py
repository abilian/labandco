from __future__ import annotations

import json

import structlog
from jsonrpcserver import method

from labster.newforms import get_form_class_by_name
from labster.rpc.demande import get_gestionnaire, get_laboratoire, get_porteur
from labster.types import JSONDict

logger = structlog.get_logger()


@method
def get_formulaire_vierge(type: str = "rh") -> JSONDict:
    """Retourne les données nécessaires pour un formulaire vierge."""
    labo = get_laboratoire()

    # Temp fixes to make crawler work.
    if not labo:
        return {}
        # return "Ignore", 200, {"content-type": "text/plain"}

    form_class = get_form_class_by_name(type)

    form = form_class(
        laboratoire=labo,
        porteur=get_porteur(),
        gestionnaire=get_gestionnaire(),
        mode="create",
    )

    model = form.empty_model()
    model["laboratoire"] = labo.nom

    porteur = get_porteur()
    if porteur and "porteur" in model:
        model["porteur"] = porteur.uid

    json.dumps(form.to_dict())

    return {"form": form.to_dict(), "model": model}
