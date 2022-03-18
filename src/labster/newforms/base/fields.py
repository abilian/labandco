from __future__ import annotations

import uuid

from flask_babel import format_date

from labster.domain.models.profiles import Profile
from labster.domain.models.util import parse_date
from labster.types import JSONDict


class Field:
    required = False
    visible = True
    hidden = False
    editable = True
    scalar = True
    note = ""
    specs: list[list[str]] = []

    def __init__(self, name, label, **kw):
        self.name = name
        self.label = label
        for k, v in kw.items():
            setattr(self, k, v)

    def to_dict(self) -> JSONDict:
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "scalar": self.scalar,
            "label": self.label,
            "required": self.required,
            "visible": self.visible,
            "hidden": self.hidden,
            "editable": self.editable,
            "note": self.note,
            "specs": self.specs,
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


# def make_choices(l: List[str]):
#     return [{"value": x, "label": x} for x in l]


class Select2Field(Field):
    choices: list[str] = []

    def to_dict(self) -> JSONDict:
        d = Field.to_dict(self)
        if callable(self.choices):
            choices = self.choices()
        else:
            choices = self.choices

        d["choices"] = choices
        return d

        # if choices and isinstance(choices[0], str):
        #     d["choices"] = make_choices(choices)
        # else:
        #     d["choices"] = choices
        # return d


class MultipleSelect2Field(Field):
    choices: list[str] = []

    def to_dict(self) -> JSONDict:
        d = Field.to_dict(self)
        if callable(self.choices):
            choices = self.choices()
        else:
            choices = self.choices
        d["choices"] = choices
        return d


class TextAreaField(Field):
    pass


class HTML(Field):
    editable = False

    def __init__(self, text, name=""):
        if not name:
            name = "html-" + uuid.uuid4().hex
        super().__init__(name, text)


class ListField(Field):
    scalar = False


class ListePartenaires(ListField):
    specs = [
        ["nom_partenaire", "Nom du partenaire"],
        ["prenom_nom_contact", "Contact"],
        ["mail_contact", "Email"],
        ["telephone_contact", "Téléphone"],
    ]


class ListePartenairesContactes(ListField):
    specs = [
        ["contact", "Contact"],
        ["nom_partenaire", "Nom du partenaire"],
    ]


class ListeDivulgationsPassees(ListField):
    specs = [
        ["type_divulgation", "Type de divulgation"],
        ["titre", "Titre"],
        ["date_lieu", "Date et lieu"],
    ]


class ListeDivulgationsFutures(ListField):
    specs = [
        ["type_divulgation", "Type de divulgation"],
        ["date", "Date envisagée"],
    ]


class ListeContrats(ListField):
    specs = [
        ["contrat", "Contrat/Partenariat de recherche"],
        ["date_signature", "Date de signature du contrat"],
        ["reference", "Référence du contrat"],
    ]


class ListeMateriels(ListField):
    specs = [
        ["materiel", "Matériel"],
    ]


class ListeAutresDeclarations(ListField):
    specs = [
        ["type_protection", "Type de protection"],
        ["organisme", "Organisme ayant fait le dépôt"],
        ["exploitation", "Exploitation industrielle"],
    ]


class ListeLicencesExistantes(ListField):
    specs = [
        ["type_licence", "Type de la licence"],
        ["nom_version_licence", "Nom et version de la licence"],
    ]


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
