from __future__ import annotations

from jsonrpcserver import method
from sqlalchemy.orm import joinedload

from labster.blueprints.util import get_current_user
from labster.domain.models.demandes import Demande
from labster.types import JSON
from labster.util import url_for

HOME_BOXES = [
    # Recherche
    ["porteur", "Mes demandes comme porteur"],
    ["directeur", "Mes demandes comme directeur"],
    ["gestionnaire", "Mes demandes comme gestionnaire"],
    ["gestionnaire/2", "Mes demandes de mes structures"],
    # DR&I
    ["direction dgrtt", "Mes demandes comme directeur/trice de la DR&I"],
    ["chef de bureau", "Mes demandes comme chef/cheffe de bureau DR&I"],
    ["référent", "Mes demandes comme référent DR&I"],
    ["contact dgrtt", "Mes demandes comme contact DR&I"],
    ["contact dgrtt/2", "Les demandes de mes structures de recherche"],
    ["dgrtt", "Toutes les demandes actives à la DR&I"],
]

ARCHIVES_BOXES = [
    # Recherche
    ["porteur", "Demandes archivées dont j'ai été porteur"],
    ["directeur", "Demandes archivées de ma structure"],
    ["gestionnaire", "Demandes archivées dont j'ai été gestionnaire"],
    ["gestionnaire/2", "Demandes archivées de mes structures"],
    # DR&I
    ["dgrtt", "Demandes archivées dont j'ai été le contact"],
    ["dgrtt/2", "Toutes les demandes archivées à la DR&I"],
]


QUERY = Demande.query.options(
    joinedload(Demande.structure),
    joinedload(Demande.contact_dgrtt),
    joinedload(Demande.gestionnaire),
    joinedload(Demande.porteur),
)


@method
def get_boxes(archives=False) -> JSON:
    user = get_current_user()
    if archives:
        boxes = ARCHIVES_BOXES
    else:
        boxes = HOME_BOXES

    result = []
    for scope, title in boxes:
        role = scope.split("/")[0]
        if not user.has_role(role):
            continue

        url = url_for("v3.demandes", scope=scope, archives=archives)
        result.append({"title": title, "api_url": url})

    return result
