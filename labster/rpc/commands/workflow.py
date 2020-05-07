from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method

from labster.di import injector
from labster.domain2.model.demande import Demande
from labster.security import get_current_profile


@method
def wf_transition(demande_id, action, data=None):
    data = data or {}
    user = get_current_profile()
    db = injector.get(SQLAlchemy)

    demande = db.session.query(Demande).get(demande_id)
    workflow = demande.get_workflow(user)

    try:
        transition = workflow.get_transition_by_id(action)
    except IndexError:
        msg = (
            "Action impossible. Quelqu'un a probablement effectué une action "
            "sur la demande en parallèle avec vous.",
            "danger",
        )
        return msg

    workflow.execute_transition(transition, data=data)
    db.session.commit()
    msg = (
        f"Votre action '{transition.label}' sur la demande '{demande.nom}' a bien été prise en compte.",
        "success",
    )
    return msg


# @method
# def wf_transition(demande_id, action):
#     user = get_current_profile()
#     db = injector.get(SQLAlchemy)
#
#     form = transition.get_form(workflow)
#     for field in form:
#         field.form = form
#     is_form_valid = form.validate()
#
#     if __action == "confirm":
#         if is_form_valid:
#             data = {}
#             for field in form:
#                 data[field.id] = field.data
#             workflow.execute_transition(transition, data=data)
#             db.session.commit()
#             flash(
#                 "Votre action '{}' sur la demande '{}' a bien été prise en compte.".format(
#                     transition.label, demande.nom
#                 )
#             )
#             return redirect(url_for(demande, _external=True))
#         else:
#             flash(
#                 "Merci de bien vouloir corriger ou compléter les informations "
#                 "ci-dessous.",
#                 "danger",
#             )
#             flash(f"{form.errors}")
#
#     title = "Confirmer l'action"
#     breadcrumbs = [{"name": "Demandes", "url": url_for(".demandes")}, {"name": title}]
#
#     ctx = {
#         "title": title,
#         "breadcrumbs": breadcrumbs,
#         "form": form,
#         "transition": transition,
#         "demande": demande,
#     }
#     return render_template("wf/confirm.html", **ctx)
