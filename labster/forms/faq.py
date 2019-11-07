from __future__ import annotations

from abilian.web.forms import Form, RichTextWidget, Select2Field, required, \
    strip
from wtforms import StringField


class FaqEditForm(Form):
    title = StringField("Titre", validators=[required()])
    category = Select2Field("Catégorie", choices=[], validators=[required()])
    body = StringField(
        "Contenu", validators=[required()], filters=(strip,), widget=RichTextWidget()
    )
