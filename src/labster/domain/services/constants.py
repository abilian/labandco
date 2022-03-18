from __future__ import annotations

import json
from os.path import dirname
from typing import Any

import structlog
from dotted.collection import DottedCollection, DottedDict

from labster.domain.models.config import Config
from labster.extensions import db

"""

- adding new constants: add their type in TYPES and their values in
constants.json. get_constant will check for the new constants.

- upgrading the value of existing constants: use _upgrade_if_needed and the version number.

"""


logger = structlog.get_logger()

TYPES = {
    "api_key": "str",
    "convention.COUT_ENVIRONNEMENT_PERSONNEL_HEBERGE": "int",
    "convention.COUT_HORAIRE_STAGE": "float",
    "convention.DUREE_AMORTISSEMENT": "list[list[str,int]]",
    "convention.REMUNERATION": "list[list[str,int]]",
    "convention.TAUX_CHARGE_PATRONALE": "float",
    "convention.TAUX_ENVIRONNEMENT_PERSONNEL_NON_PERMANENT": "float",
    "convention.TAUX_ENVIRONNEMENT_PERSONNEL_PERMANENT": "float",
    "convention.TAUX_PARTICIPATION_COUTS_INDUITS": "float",
    "convention.TAUX_PROVISION_RISQUE": "float",
    "faq_categories": "list[str]",
    "message_dgrtt": "HTML",
    "nom_bureaux_dgrtt.MSAR": "str",
    "nom_bureaux_dgrtt.PIJ": "str",
    "nom_bureaux_dgrtt.ETI": "str",
    "nom_bureaux_dgrtt.AIPI": "str",
    "nom_bureaux_dgrtt.CC": "str",
    "nom_bureaux_dgrtt.CFE": "str",
    "nom_bureaux_dgrtt.GF": "str",
    "nom_bureaux_dgrtt.EU": "str",
    "nom_bureaux_dgrtt.PI2": "str",
    "nom_bureaux_dgrtt.CP": "str",
    "nom_bureaux_dgrtt.REF": "str",
    "nom_bureaux_dgrtt.DIR": "str",
    "nom_bureaux_dgrtt.CT": "str",
    "nom_bureaux_dgrtt.ETT": "str",
    "point_indice": "float",
    "recrutement.charges_moins_12_mois": "float",
    "recrutement.charges_plus_12_mois": "float",
    "recrutement.ecoles_doctorales": "list[str]",
    "recrutement.grades": "list[str]",
    "recrutement.salaire_brut_mensuel_indicatif.Chercheur": "str",
    "recrutement.salaire_brut_mensuel_indicatif.Post-doctorant": "list[list[str,int]]",
    "recrutement.salaire_brut_mensuel_indicatif.IGR": "list[list[str,int]]",
    "recrutement.salaire_brut_mensuel_indicatif.IGE": "list[list[str,int]]",
    "recrutement.salaire_brut_mensuel_indicatif.ASI": "list[list[str,int]]",
    "recrutement.salaire_brut_mensuel_indicatif.technicien-sup": "list[list[str,int]]",
    "recrutement.salaire_brut_mensuel_indicatif.technicien-normale": "list[list[str,int]]",
    "recrutement.salaire_brut_mensuel_indicatif.adjoint": "list[list[str,int]]",
    "recrutement.principes": "HTML",
    "recrutement.provision_risque_charge_employeur": "float",
    "recrutement.salaire_min_doctorant": "float",
    "recrutement.couts_charges.PU/DR C EX Confirmé": "str",
    "recrutement.couts_charges.PU/DR C EX": "str",
    "recrutement.couts_charges.PU/DR C1 Confirmé": "str",
    "recrutement.couts_charges.PU/DR C1": "str",
    "recrutement.couts_charges.PU/DR C2 Confirmé": "str",
    "recrutement.couts_charges.PU/DR C2": "str",
    "recrutement.couts_charges.MC/CR HC Confirmé": "str",
    "recrutement.couts_charges.MC/CR HC": "str",
    "recrutement.couts_charges.MC/CR CN Confirmé": "str",
    "recrutement.couts_charges.MC/CR CN": "str",
    "recrutement.couts_charges.IR HC Confirmé": "str",
    "recrutement.couts_charges.IR HC": "str",
    "recrutement.couts_charges.IR C1 Confirmé": "str",
    "recrutement.couts_charges.IR C1": "str",
    "recrutement.couts_charges.IR C2 Confirmé": "str",
    "recrutement.couts_charges.IR C2": "str",
    "recrutement.couts_charges.IE HC confirmé": "str",
    "recrutement.couts_charges.IE HC": "str",
    "recrutement.couts_charges.IE C1 Confirmé": "str",
    "recrutement.couts_charges.IE C1": "str",
    "recrutement.couts_charges.IE C2 Confirmé": "str",
    "recrutement.couts_charges.IE C2": "str",
    "recrutement.couts_charges.ASI Confirmé": "str",
    "recrutement.couts_charges.ASI": "str",
    "recrutement.couts_charges.TR CE Confirmé": "str",
    "recrutement.couts_charges.TR CE": "str",
    "recrutement.couts_charges.TR CS Confirmé": "str",
    "recrutement.couts_charges.TR CS": "str",
    "recrutement.couts_charges.TR CN Confirmé": "str",
    "recrutement.couts_charges.TR CN": "str",
    "recrutement.transport": "float",
    "demande_recrutement.pj": "HTML",
    "demande_recrutement.bareme": "HTML",
    "pi_invention.pieces_a_joindre": "HTML",
    "pi_invention.conditions": "HTML",
    "pi_logiciel.conditions": "HTML",
}

VALID_TYPES = [
    "int",
    "float",
    "bool",
    "str",
    "HTML",
    "list[str]",
    "list[list[str,int]]",
]

for t in TYPES.values():
    assert t in VALID_TYPES, t


def get_message_dgrtt():
    return get_constant("message_dgrtt", "OK")


def get_faq_categories():
    categories = get_constant("faq_categories", [])
    return [(x, x) for x in categories]


def _get_constants() -> dict[str, Any]:
    """Get constants from config or local json with updating system.

    Pick new constants that are defined in TYPES but are not saved in
    the config yet from the json.

    Upgrades constants that already exist, given the version number.
    """
    from labster.domain.models.config import Config

    config = Config.query.first()

    if config is None:
        config = Config()
        db.session.add(config)

    initial_constants = get_initial_constants()

    # upgrade
    _upgrade_if_needed(config, initial_constants)

    constants = config.data
    dotted_constants = DottedCollection.factory(constants)
    json_dotted_constants = DottedCollection.factory(initial_constants)

    if dotted_constants:
        for key in TYPES.keys():
            # do not write "key not in .keys()", it doesn't return "dotted keys".
            if dotted_constants.get(key, _MARKER) is _MARKER:
                dotted_constants[key] = json_dotted_constants.get(key)

        constants = dotted_constants.to_python()

    return constants


def _upgrade_if_needed(config: Config, initial_constants: dict[str, Any]):
    """ "data migration" tool.

    - constants: the ones from the config, to update.
    - initial_constants: from the json file, that may have additions.
    """
    needs_commit = False
    version = initial_constants.get("version")

    if not version:
        return

    constants = config.data or {}

    # Check the state we want rather than a version number.
    # if version == 0.2 and constants.get('version', 0) < 0.2:
    if "recrutement" not in constants:
        constants["recrutement"] = {}
        needs_commit = True

    if "grades" not in constants["recrutement"]:
        constants["recrutement"]["grades"] = []
        needs_commit = True

    if (
        "recrutement" in constants
        and constants["recrutement"]["grades"]
        and constants["recrutement"]["grades"][0] == "IR"
    ):
        constants["recrutement"]["grades"] = initial_constants["recrutement"]["grades"]
        constants["version"] = version
        needs_commit = True

    if version == 0.3:
        # add salaire_brut_mensuel_indicatif.doctorat-plus-3
        # Maybe a new DB doesn't have salaire_brut_mensuel_indicatif yet.
        if not constants["recrutement"].get("salaire_brut_mensuel_indicatif"):
            constants["recrutement"][
                "salaire_brut_mensuel_indicatif"
            ] = initial_constants["recrutement"]["salaire_brut_mensuel_indicatif"]
        else:
            post_doct_names = [
                it[0]
                for it in constants["recrutement"]["salaire_brut_mensuel_indicatif"][
                    "Post-doctorant"
                ]
            ]
            if "doctorat-plus-3" not in post_doct_names:
                constants["recrutement"]["salaire_brut_mensuel_indicatif"][
                    "Post-doctorant"
                ].append(
                    initial_constants["recrutement"]["salaire_brut_mensuel_indicatif"][
                        "Post-doctorant"
                    ][-1]
                )

        # logger.info("--- constants updated for 0.3 - doctorat-plus-3")
        constants["version"] = 0.3
        needs_commit = True

    if needs_commit:
        config.data = constants
        db.session.commit()


def get_initial_constants() -> dict[str, Any]:
    filename = dirname(__file__) + "/constants.json"
    return json.load(open(filename, "rb"))


def get_constants() -> dict[str, Any]:
    constants = _get_constants()
    return update_constants(constants)


_MARKER = object()


def get_constant(path: str, default: object = _MARKER) -> Any:
    """Return this constant's value from a dotted path.

    Raises a KeyError if the path is illegal.

    - path: a dotted key (str) (example: "convention.REMUNERATION")
    - returns: the value or a default one (of the good type, if specified).
    """
    if path not in TYPES:
        raise KeyError(path)

    constants = _get_constants()
    dotted_constants = DottedCollection.factory(constants)

    try:
        value = dotted_constants[path]
        if isinstance(value, DottedCollection):
            return dotted_constants[path].to_python()
        else:
            return value
    except KeyError:
        pass

    # If a default value is supplied, return it
    if default != _MARKER:
        return default

    # Otherwise, use a default depending on the type
    type_ = TYPES[path]
    return default_value(type_)


def default_value(type_: str) -> Any:
    if type_ in ["str", "HTML"]:
        return ""
    elif type_ == "int":
        return 0
    elif type_ == "float":
        return 0.0
    elif type_ == "bool":
        return False
    elif type_.startswith("list"):
        return []
    else:
        raise RuntimeError(f"Unknown type: {type_}")


def save_constants(constants):
    from labster.domain.models.config import Config

    updated_constants = update_constants(constants)

    config = Config.query.first()
    if config is None:
        config = Config(data=updated_constants)
    else:
        config.data = updated_constants
    return config


def update_constants(constants: dict[str, Any]) -> dict[str, Any]:
    if "types" in constants:
        del constants["types"]
    dotted_constants = DottedCollection.factory(constants)

    updated_constants = DottedDict()
    for key, type_ in TYPES.items():
        try:
            # do not write "key in .keys()", it doesn't check for dotted keys.
            if dotted_constants.get(key, _MARKER) is not _MARKER:
                value = dotted_constants[key]
            elif key in TYPES.keys():
                value = get_constant(key)
            else:
                value = default_value(type_)
        except KeyError:
            value = default_value(type_)

        try:
            value = coerce(value, type_)
        except TypeError:
            msg = "Wrong type for key: {}, value{} "
            raise TypeError(msg.format(key, value))
        check_type(key, value, type_)
        updated_constants[key] = value

    return updated_constants.to_python()


def check_type(key: str, value: Any, type_: str) -> None:
    def ensure_types(types):
        val = value
        if isinstance(value, DottedCollection):
            val = value.to_python()
        if not isinstance(val, types):
            msg = f"Wrong type for key: {key}. Expected: {type_}, got: {type(val)}"
            raise TypeError(msg)

    if type_ == "int":
        ensure_types(int)
    elif type_ == "float":
        ensure_types((float, int))
    elif type_ == "str":
        ensure_types(str)
    elif type_ == "bool":
        ensure_types(bool)
    elif type_.startswith("list"):
        ensure_types(list)
        # TODO: more specific cases


def coerce(value: Any, type_: str) -> Any:
    if type_ == "int":
        return int(value)
    elif type_ == "float":
        return float(value)
    elif type_ == "str":
        return str(value)
    elif type_ == "bool":
        return bool(value)
    else:
        return value
