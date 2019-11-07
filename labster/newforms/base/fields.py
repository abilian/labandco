from __future__ import annotations

import hashlib
from typing import List

from flask_babel import format_date

from labster.domain.models.profiles import Profile
from labster.domain.models.util import parse_date
from labster.types import JSONDict


class Field:
    required = False
    visible = True
    hidden = False
    editable = True
    note = ""

    def __init__(self, name, label, **kw):
        self.name = name
        self.label = label
        for k, v in kw.items():
            setattr(self, k, v)

    def to_dict(self) -> JSONDict:
        class_name = self.__class__.__name__
        return {
            "name": self.name,
            "type": [class_name],
            "scalar": not class_name.startswith("List"),
            "label": self.label,
            "required": self.required,
            "visible": self.visible,
            "hidden": self.hidden,
            "editable": self.editable,
            "note": self.note,
        }

    def get_display_value(self, demande) -> str:
        """Return the name of this field for display in the form."""
        if self.name == "porteur":
            # get a Profile object, so than we get the full_name below
            # and not just its uid.
            value = demande.porteur
        else:
            value = demande.data.get(self.name, "")

        if value in (None, "None"):
            value = ""
        elif value is False:
            value = "Non"
        elif value is True:
            value = "Oui"
        elif isinstance(value, Profile):
            value = value.full_name

        return str(value)


class StringField(Field):
    pass


class DateField(Field):
    def get_display_value(self, demande):
        value = demande.data.get(self.name, "")
        date_value = parse_date(value)
        if not value:
            return ""
        return format_date(date_value, format="medium")


class IntegerField(Field):
    pass


class EmailField(Field):
    pass


class BooleanField(Field):
    pass


class Boolean2Field(Field):
    pass


class TriStateField(Field):
    pass


class Select2Field(Field):
    choices: List[str] = []

    def to_dict(self) -> JSONDict:
        d = Field.to_dict(self)
        if callable(self.choices):
            choices = self.choices()
        else:
            choices = self.choices
        if choices and isinstance(choices[0], str):
            d["choices"] = [[x, x] for x in choices]
        else:
            d["choices"] = choices
        return d


class TextAreaField(Field):
    pass


class HTML(Field):
    editable = False

    def __init__(self, text, name=""):
        if not name:
            name = "html-" + hashlib.md5(text.encode("utf8")).hexdigest()
        super().__init__(name, text)


class ListePartenaires(Field):
    pass


class ListePartenairesContactes(Field):
    pass


class ListeDivulgationsPassees(Field):
    pass


class ListeDivulgationsFutures(Field):
    pass


class ListeContrats(Field):
    pass


class ListeMateriels(Field):
    pass


class ListeAutresDeclarations(Field):
    pass


class ListeLicencesExistantes(Field):
    pass


class FieldSet:
    def __init__(self, name, label, fields):
        self.name = name
        self.label = label
        self.fields = fields
        self.visible = True
        self.hidden = False

    def to_dict(self) -> JSONDict:
        return {
            "name": self.name,
            "type": [self.__class__.__name__],
            "label": self.label,
            "fields": [field.name for field in self.fields],
            "visible": self.visible,
            "hidden": self.hidden,
        }

    def __repr__(self):
        return f"<FieldSet name={self.name} visible={self.visible}>"
