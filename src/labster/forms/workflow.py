from __future__ import annotations

from abilian.web.forms import Form, optional, required
from wtforms import BooleanField, StringField, TextAreaField


class WorkflowForm(Form):
    note = TextAreaField("Note", validators=[optional()])
    resoumission = BooleanField(
        "Redemander validation par la hiérarchie", validators=[optional()]
    )

    def __init__(self, require_note=False, ask_for_revalidation=False, *args, **kw):
        super().__init__(*args, **kw)

        if require_note:
            self["note"].validators = [required()]
        else:
            self["note"].validators = [optional()]

        if not ask_for_revalidation:
            del self["resoumission"]


class ConfirmerRecevabiliteForm(WorkflowForm):
    no_infolab = StringField("N° Infolab / référence DRI", validators=[required()])


class ConfirmerFinalisationForm(WorkflowForm):
    no_eotp = StringField("N° EOTP / référence DRI", validators=[required()])
