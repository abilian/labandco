from __future__ import annotations

from flask import g, render_template, request

from labster.domain.models.demandes import AVENANT_CONVENTION, CONVENTION, \
    PI_INVENTION, PI_LOGICIEL, RECRUTEMENT
from labster.domain.models.profiles import Profile


#
# Workflow
#
def demandes_a_valider():
    type = request.args.get("type", None)

    demandes = g.current_user.demandes_a_valider()

    if type == "convention":
        title = "Demandes à valider de type Convention"
        demandes = [d for d in demandes if d.type in [CONVENTION, AVENANT_CONVENTION]]

    elif type == "rh":
        title = "Demandes à valider de type Recrutement/RH"
        demandes = [d for d in demandes if d.type in [RECRUTEMENT]]

    elif type == "pi":
        title = "Demandes à valider de type Transfert/PI"
        demandes = [d for d in demandes if d.type in [PI_LOGICIEL, PI_INVENTION]]

    else:
        title = "Demandes à valider"

    ctx = {"title": title, "demandes": demandes}
    return render_template("wf/demandes_a_valider.html", **ctx)


def late_tasks():
    user = g.current_user  # type: Profile
    demandes = user.mes_taches_en_retard()

    ctx = {
        "title": f"Mes tâches en retard ({len(demandes)})",
        "demandes": demandes,
        "nb_demandes": len(demandes),
    }
    return render_template("wf/late_tasks.html", **ctx)
