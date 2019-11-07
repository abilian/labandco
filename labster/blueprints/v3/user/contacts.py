from __future__ import annotations

from typing import Any, Dict, List

from attr import dataclass
from marshmallow import Schema, fields

from labster.blueprints.util import get_current_user
from labster.blueprints.v3 import route
from labster.domain.models.mapping_dgrtt import MappingDgrtt
from labster.domain.models.profiles import Profile
from labster.domain.services.dgrtt import BUREAUX_DGRTT, BureauDgrtt


@dataclass
class Contact:
    bureau: BureauDgrtt
    profile: Profile


class BureauSchema(Schema):
    id = fields.String()
    nom = fields.String()


class ProfileSchema(Schema):
    id = fields.String()
    nom = fields.String()


class ContactSchema(Schema):
    bureau = fields.Nested(BureauSchema)
    profile = fields.Nested(ProfileSchema)


@route("/user/contacts")
def contacts() -> Dict[str, Any]:
    user = get_current_user()

    contacts = contacts_dgrtt(user)

    contacts_dto = ContactSchema().dump(contacts, many=True).data
    title = "Mes contacts"
    return {"title": title, "contacts_dgrtt": contacts_dto}

    # if user.laboratoire:
    #     return contacts_dgrtt(user)
    # else:
    #     return contacts_labos(user)


def contacts_dgrtt(user) -> List[Contact]:
    labo = user.laboratoire
    mapping_dgrtt = MappingDgrtt.query.filter(MappingDgrtt.ou_recherche == labo).all()

    result = []
    for bureau in BUREAUX_DGRTT:
        if bureau.id in ["AIPI 2", "Com", "Finance 2", "Finance 3", "Moyens"]:
            continue

        for m in mapping_dgrtt:
            if m.bureau_dgrtt == bureau.id:
                result.append(Contact(bureau=bureau, profile=m.contact_dgrtt))
                break

    return result


# def contacts_dgrtt(user) -> Dict[str, Any]:
#
#     title = "Mes contacts"
#     ctx = {"title": title, "contacts_dgrtt": user.contacts_dgrtt}
#     return render_template("contacts.html", **ctx)
#
#
# def contacts_labos(user) -> str:
#     title = "Mes laboratoires"
#     ctx = {"title": title, "user": user}
#     return render_template("labos.html", **ctx)
