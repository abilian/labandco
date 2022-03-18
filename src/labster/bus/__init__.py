from __future__ import annotations

from functools import singledispatch

import requests
from flask import current_app
from marshmallow import Schema, fields

from labster.domain2.model.demande import Demande
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure
from labster.extensions import db
from labster.signals import model_saved

COLLECTIONS = ["users", "structures", "demandes"]


class ProfileSchema(Schema):
    uid = fields.Str()
    full_name = fields.Str()
    fonction_structurelle_principale = fields.Str()
    ldap_dict = fields.Dict()


class PorteurSchema(ProfileSchema):
    pass


class GestionnaireSchema(ProfileSchema):
    pass


class OrgUnitSchema(Schema):
    nom = fields.Str()
    sigle = fields.Str()
    dn = fields.Str()


class DemandeSchema(Schema):
    id = fields.Integer()
    nom = fields.Str()
    no_infolab = fields.Str()
    no_eotp = fields.Str()

    # FIXME
    # date_effective = fields.DateTime()
    # date_soumission = fields.DateTime()
    # date_finalisation = fields.DateTime()

    porteur = fields.Nested(PorteurSchema)
    gestionnaire = fields.Nested(GestionnaireSchema)
    contact_dgrtt = fields.Nested(ProfileSchema)

    laboratoire = fields.Nested(OrgUnitSchema)
    structure = fields.Nested(OrgUnitSchema)

    active = fields.Boolean()
    wf_state = fields.Str()
    wf_date_derniere_action = fields.DateTime()
    wf_retard = fields.Integer()
    wf_current_owner = fields.Str()
    wf_history = fields.List(fields.Dict())
    age = fields.Integer()
    retard = fields.Integer()
    contact = fields.Str()

    data = fields.Method("get_data")

    def get_data(self, obj):
        d = obj.data
        d = {k: v for k, v in d.items() if not k.startswith("html-")}
        return d


class RestHeart:
    def __init__(self):
        config = current_app.config
        self.root_url = config.get("RESTHEART_URL")
        self.auth = config["RESTHEART_AUTH"]

    def put(self, url, **kw):
        url = self.root_url + "/" + url
        response = requests.put(url, auth=self.auth, **kw)
        return response

    def post(self, url, **kw):
        url = self.root_url + "/" + url
        response = requests.post(url, auth=self.auth, **kw)
        return response


def init():
    rh = RestHeart()
    rh.put("db")
    for coll_name in COLLECTIONS:
        print(f"Creating collection {coll_name}")
        response = rh.put(coll_name)
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Server send invalid response: {response}")


def sync_all_objects():
    print("Syncing users")
    sync_objects(Profile)
    print("Syncing structures")
    sync_objects(Structure)
    print("Syncing demandes")
    sync_objects(Demande)


def sync_objects(cls: type):
    objects = db.session.query(cls).all()
    for obj in objects:
        sync_object(obj)


def sync_object(obj):
    rh = RestHeart()
    url, data = serialize(obj)
    # print(url, data)
    response = rh.put(url, json=data)
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Server send invalid response: {response}")


@singledispatch
def serialize(obj):
    raise NotImplementedError


@serialize.register(Profile)
def serialize_profile(obj):
    url = f"users/{obj.uid}"
    schema = ProfileSchema()
    result = schema.dump(obj)
    assert not result.errors, result.errors
    data = result.data
    return url, data


@serialize.register(Structure)
def serialize_structure(obj):
    url = f"structures/{obj.id}"
    schema = OrgUnitSchema()
    result = schema.dump(obj)
    assert not result.errors, result.errors
    data = result.data
    return url, data


@serialize.register(Demande)
def serialize_demande(obj):
    url = f"demandes/{obj.id}"
    schema = DemandeSchema()
    result = schema.dump(obj)
    assert not result.errors, result.errors
    data = result.data
    return url, data


def on_model_saved(obj):
    print(f"Model {obj} saved")
    sync_object(obj)


def register_callback() -> None:
    model_saved.connect(on_model_saved)
