from __future__ import annotations

from jsonrpcserver import method

from labster.domain2.model.demande import DemandeAutre, \
    DemandeAvenantConvention, DemandeConvention, DemandePiMixin, DemandeRH
from labster.domain2.services.roles import Role
from labster.domain2.services.workflow.states import EN_VALIDATION
from labster.rpc.queries.demandes_tables import mes_taches
from labster.security import get_current_profile


@method
def get_nb_demandes_a_valider():
    user = get_current_profile()

    ctx = {
        "total_demandes": 0,
        "nb_pi_a_valider": 0,
        "nb_recrutements_a_valider": 0,
        "nb_conventions_a_valider": 0,
        "nb_autres_a_valider": 0,
    }

    if user.has_role(Role.RESPONSABLE, "*"):
        demandes = mes_taches(user)
        demandes = [d for d in demandes if d.wf_state == EN_VALIDATION.id]

        conventions = [
            d
            for d in demandes
            if isinstance(d, (DemandeConvention, DemandeAvenantConvention))
        ]
        recrutements = [d for d in demandes if isinstance(d, DemandeRH)]
        pi = [d for d in demandes if isinstance(d, DemandePiMixin)]
        autres = [d for d in demandes if isinstance(d, DemandeAutre)]

        ctx["total_demandes"] = len(demandes)
        ctx["nb_conventions_a_valider"] = len(conventions)
        ctx["nb_recrutements_a_valider"] = len(recrutements)
        ctx["nb_pi_a_valider"] = len(pi)
        ctx["nb_autres_a_valider"] = len(autres)

    return ctx
