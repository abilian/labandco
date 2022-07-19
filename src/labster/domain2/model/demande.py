from __future__ import annotations

from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, unique
from functools import singledispatch
from typing import Any

import dateutil
import sqlalchemy as sa
from abilian.app import db
from email_validator import EmailNotValidError, validate_email
from sqlalchemy import JSON, Boolean, Column, Date, DateTime, ForeignKey, \
    Integer, String
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import relationship

from labster.domain2.model.base import Repository
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure, StructureRepository
from labster.domain2.model.util import parse_date
from labster.domain2.services.calculs_couts import cout_total_charge
from labster.domain2.services.contacts import ContactService, ContactType
from labster.domain2.services.workflow.states import EN_EDITION
from labster.domain2.services.workflow.workflow import LabsterWorkflow
from labster.lib.workflow import State


@unique
class DemandeType(Enum):
    CONVENTION = "Convention de recherche"
    AVENANT_CONVENTION = "Avenant à une convention de recherche"
    RECRUTEMENT = "Recrutement"
    PI_LOGICIEL = "Déclaration de logiciel / base de données"
    PI_INVENTION = "Déclaration d´invention"
    AUTRE = "Demande autre"
    # To please the typechecker
    ILLEGAL = "Should not happen"


types_demande = [x.value for x in DemandeType]


class Demande(db.Model):
    __tablename__ = "v3_demandes"

    _type: str = DemandeType.ILLEGAL.value

    id = Column(Integer, primary_key=True)
    old_id = Column(Integer)
    type = Column(
        sa.Enum(*types_demande, name="type_demande"),
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    #
    nom = Column(String)
    name = Column(String)
    active = Column(Boolean, default=True)
    editable = Column(Boolean, default=True)
    no_infolab = Column(String)
    no_eotp = Column(String)

    # Relations
    contact_labco_id = Column(String(36), ForeignKey(Profile.id))
    gestionnaire_id = Column(String(36), ForeignKey(Profile.id))
    porteur_id = Column(String(36), ForeignKey(Profile.id))
    structure_id = Column(String(36), ForeignKey(Structure.id))

    #
    data = Column(MutableDict.as_mutable(JSON))
    past_versions = Column(MutableList.as_mutable(JSON))
    form_state = Column(MutableDict.as_mutable(JSON))
    attachments = Column(MutableDict.as_mutable(JSON))
    feuille_cout = Column(MutableDict.as_mutable(JSON))
    documents_generes = Column(MutableList.as_mutable(JSON))

    # Workflow
    # wf_state = Column(WF_ENUM, default=EN_EDITION.id, nullable=False, index=True)
    wf_state = Column(String)
    wf_date_derniere_action = Column(DateTime)
    wf_retard = Column(Integer)
    wf_history = Column(MutableList.as_mutable(JSON))
    wf_data = Column(MutableDict.as_mutable(JSON))
    #: Date de validation par la hiérarchie
    date_effective = Column(Date, nullable=True)

    contact_labco = relationship(
        Profile, foreign_keys=lambda: [Demande.contact_labco_id]
    )
    porteur = relationship(Profile, foreign_keys=lambda: [Demande.porteur_id])
    gestionnaire = relationship(Profile, foreign_keys=lambda: [Demande.gestionnaire_id])
    structure = relationship(Structure)

    __mapper_args__ = {"polymorphic_identity": "", "polymorphic_on": type}

    # wf_stage_id = Column(Integer, ForeignKey(OrgUnit.id), index=True, nullable=True)
    # wf_stage = relationship(
    #     OrgUnit, primaryjoin=remote(Entity.id) == foreign(wf_stage_id)
    # )
    #
    # #: id de la personne responsable de la tâche en cours
    # wf_current_owner_id = Column(
    #     Integer, ForeignKey(Profile.id), index=True, nullable=True
    # )
    # #: la personne responsable de la tâche en cours
    # wf_current_owner = relationship(
    #     Profile, primaryjoin=remote(Entity.id) == foreign(wf_current_owner_id)
    # )

    # id: Optional[DemandeId] = None
    # created_at: datetime = field(default_factory=datetime.utcnow)
    #
    # nom: str = ""
    # name: str = ""
    # no_infolab: str = ""
    # no_eotp: str = ""
    #
    # # type = Column(Enum(*TYPE_ENUM, name="demande_type"), nullable=False, index=True)
    #
    # data: JSONDict = field(default_factory=dict)
    #
    # past_versions: JSONList = field(default_factory=list)
    # form_state: JSONDict = field(default_factory=dict)
    # attachments: JSONDict = field(default_factory=dict)
    # feuille_cout: JSONDict = field(default_factory=dict)
    # documents_generes: JSONList = field(default_factory=list)
    #
    # #: Date de validation par la hiérarchie
    # date_effective: Optional[date] = None
    #
    # #: Seules les demandes actives apparaissent dans le workflow.
    # #: Les autres sont considérées comme archivées.
    # active: bool = field(default_factory=lambda: True)
    # editable: bool = field(default_factory=lambda: True)
    #
    # # Les acteurs de la demande:
    # porteur: Optional[Profile] = None
    # gestionnaire: Optional[Profile] = None
    # contact_labco: Optional[Profile] = None
    #
    # # Structures liées
    # structure: Optional[Structure] = None
    #
    # # Variables liées au workflow [TODO]
    # wf_state: str = EN_EDITION.id
    # wf_date_derniere_action: Optional[datetime] = None
    # wf_retard: int = 0
    # wf_history: List[Dict[str, Any]] = field(default_factory=list)
    # wf_data: JSONDict = field(default_factory=dict)
    # wf_current_owner: Optional[Profile] = None

    # TODO:
    # wf_stage: a remplacer

    # wf_state = Column(WF_ENUM, default=EN_EDITION.id, nullable=False, index=True)
    #
    # wf_date_derniere_action = Column(DateTime, nullable=False)
    #
    # #: nombre de jours de retard (0 si pas de retard)
    # wf_retard = Column(Integer, nullable=False, default=0)
    #
    # wf_history = Column(JSONList(), default=list)
    #
    # wf_data = Column(JSONDict(), default=dict)
    #
    # wf_stage_id = Column(Integer, ForeignKey(OrgUnit.id), index=True, nullable=True)
    # wf_stage = relationship(
    #     OrgUnit, primaryjoin=remote(Entity.id) == foreign(wf_stage_id)
    # )
    #
    # #: id de la personne responsable de la tâche en cours
    # wf_current_owner_id = Column(
    #     Integer, ForeignKey(Profile.id), index=True, nullable=True
    # )
    # #: la personne responsable de la tâche en cours
    # wf_current_owner = relationship(
    #     Profile, primaryjoin=remote(Entity.id) == foreign(wf_current_owner_id)
    # )
    #
    # __mapper_args__ = {"polymorphic_identity": "", "polymorphic_on": type}

    def __init__(self, **kw):
        # if not hasattr(self, "porteur"):
        #     self.porteur = None
        # if not hasattr(self, "gestionnaire"):
        #     self.gestionnaire = None

        # assert self.porteur or self.gestionnaire
        # if self.porteur:
        #     self.structure = self.porteur.structure

        self.data = {}
        self.attachments = {}
        self.form_state = {"fields": []}
        self.versions = []
        self.wf_state = EN_EDITION.id
        self.wf_history = []
        self.wf_data = {}
        self.wf_retard = 0
        self.feuille_cout = {}
        self.editable = True
        self.active = True
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.wf_date_derniere_action = self.created_at

        super().__init__(**kw)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} with id={self.id}>"

    def log_creation(self, actor: Profile) -> None:
        if not self.wf_history:
            message = f"Demande créée par l'utilisateur {actor.full_name}"
            log_entry = {
                "date": datetime.now().strftime("%d %b %Y %H:%M:%S"),
                "actor_id": actor.id,
                "message": message,
                "note": "",
            }
            self.wf_history = [log_entry]

    def clone(self) -> Demande:
        return self.__class__(
            nom=self.nom,
            wf_state=EN_EDITION.id,
            porteur=self.porteur,
            gestionnaire=self.gestionnaire,
            structure=self.structure,
            data=self.data.copy(),
            form_state=self.form_state.copy(),
        )

    @property
    def date_debut(self):
        return None

    @property
    def age(self):
        if not self.date_effective:
            return 0
        dt = date.today() - self.date_effective
        return int(dt.days)

    @property
    def retard(self):
        if not self.wf_date_derniere_action or not self.active:
            return 0

        # TODO: implémenter la logique de jours ouvrés
        dt = datetime.utcnow() - self.wf_date_derniere_action
        return int(dt.days)

    def update_retard(self):
        # TODO: implémenter la logique de jours ouvrés
        dt = datetime.utcnow() - self.wf_date_derniere_action
        self.wf_retard = int(dt.days)

    def nom_par_defaut(self) -> str:
        return self.type + " sans nom"

    #
    # Accessors / properties
    #
    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(f"object has no attribute '{name}'")

        data = getattr(self, "data", None)
        if data and name in data:
            return data[name]

        raise AttributeError(f"object has no attribute '{name}'")

    def has_same_data(self, data: dict[str, Any]) -> bool:
        """Return True if the current version is the same as the given data."""
        current_data = self.data

        for k in set(current_data.keys()) | set(data.keys()):
            if k in ["csrf_token"]:
                continue
            if k.startswith("html-"):
                continue
            current_value = current_data.get(k)
            new_value = data.get(k)
            if current_value != new_value:
                return False
        return True

    @property
    def contact(self) -> Profile:
        result = self.gestionnaire or self.porteur
        assert result
        return result

    @property
    def directeur_name(self) -> str:
        structure = self.structure
        if structure and structure.directeur:
            return structure.directeur.full_name
        return ""

    @property
    def owners(self) -> set[Profile]:
        owners = set()
        if self.gestionnaire:
            owners.add(self.gestionnaire)
        if self.porteur:
            owners.add(self.porteur)
        return owners

    #
    # Workflow
    #
    def get_workflow(self, user: Profile | None = None) -> LabsterWorkflow:
        return LabsterWorkflow(self, user)

    def get_state(self, user: Profile | None = None) -> State:
        workflow = self.get_workflow(user)
        return workflow.current_state()

    def current_owners(self) -> list[Profile]:
        return self.get_workflow().current_owners()

    def structures_signataires(self) -> set[Structure]:
        result = self.get_structure_concernees()
        if self.structure:
            result.add(self.structure)
        return result

    def valideurs(self) -> set[Profile]:
        structures_signataires = self.structures_signataires()
        result = set()
        for structure in structures_signataires:
            result.update(structure.responsables)
        return result

    def get_structure_concernees(self):
        from labster.di import injector

        structure_repo = injector.get(StructureRepository)

        result = set()
        if self.data.get("structures_concernees"):
            for d in self.structures_concernees:
                structure_id = d["value"]
                structure = structure_repo.get_by_id(structure_id)
                if structure:
                    result.add(structure)

        return result

    @property
    def date_soumission(self) -> date | None:
        for entry in self.wf_history:
            if entry.get("transition") == "SOUMETTRE":
                return dateutil.parser.parse(entry["date"]).date()

        return None

    @property
    def date_finalisation(self) -> date | None:
        final_states = ["CONFIRMER_FINALISATION_DGRTT", "ABANDONNER", "REJETER_DGRTT"]
        for entry in self.wf_history:
            if entry.get("transition") in final_states:
                return dateutil.parser.parse(entry["date"]).date()

        return None

    def assigne_contact_labco(self):
        if self.contact_labco:
            return

        bureau = get_bureau_dri(self)
        if bureau:
            self.contact_labco = get_contact_labco(self.structure, bureau)
        else:
            # TODO: special case: demande "Autre"
            pass

    #
    # Data validation / manipulation
    #
    def validate(self) -> Validation:
        return Validation(self, self.get_errors(), self.get_extra_errors())

    def get_errors(self) -> list[Any]:
        errors = []
        form_state = self.form_state
        fields = form_state.get("fields", [])
        for field_name, field_value in self.data.items():
            if field_name not in fields:
                continue
            field: dict[str, Any] = fields[field_name]

            visible = bool(field.get("visible"))
            required = bool(field.get("required"))

            if visible and required and not field_value:
                errors.append(field["name"])

            if visible and "mail" in field_name and field_value:
                try:
                    validate_email(field_value)
                except EmailNotValidError:
                    errors.append(field_name)

        return errors

    def get_extra_errors(self) -> list[str]:
        return []

    def is_valid(self) -> bool:
        validation = self.validate()
        return validation.ok

    @property
    def errors(self):
        return self.validate().errors

    def update_data(self, data: dict) -> None:
        self.increase_version()
        self.data.update(data)

        self.update_nom()
        self.post_update()

    # new_name = data.get('nom', None)
    # if new_name is not None and new_name != self.name:
    #     self.name = new_name

    def post_update(self) -> None:
        new_porteur_uid = self.data.get("porteur", None)

        if new_porteur_uid is not None:
            try:
                new_porteur = db.session.query(Profile).get_by_uid(new_porteur_uid)
                self.porteur = new_porteur
                self.structure = new_porteur.structure
            except Exception:
                # TODO: better solution to deal with tests.
                pass

    def increase_version(self) -> None:
        if self.data:
            if not self.past_versions:
                self.past_versions = []
            self.past_versions.append(
                (self.data, datetime.utcnow().strftime("%d %b %Y %H:%M:%S"))
            )

    # Pièces jointes: TODO remove or debug.
    # @property
    # def pieces_jointes(self) -> List[Dict]:
    #     result = []
    #     for k, v in sorted(self.attachments.items()):
    #         if isinstance(v, dict):
    #             creator = db.session.query(Profile).filter(Profile.login==v["creator"]).first()
    #
    #             d = {"id": v["id"], "name": k, "creator": creator}
    #
    #             date_str = v.get("date")
    #             if date_str:
    #                 d["date"] = iso8601.parse_date(date_str)
    #             else:
    #                 d["date"] = None
    #         else:
    #             d = {"id": v, "name": k, "creator": None, "date": None}
    #         id = d["id"]
    #         blob = Blob.query.get(id)
    #         if blob:
    #             result.append(d)
    #     return result


#
# Concrete classes
#
class DemandeRH(Demande):
    _type = DemandeType.RECRUTEMENT.value
    icon_class = "far fa-user"

    __mapper_args__ = {"polymorphic_identity": _type}

    def update_nom(self) -> None:
        prenom = self.data.get("prenom") or "(prénom inconnu)"
        nom = self.data.get("nom") or "(nom inconnu)"
        nature = (
            self.data.get("nature_du_recrutement") or "(nature du recrutement inconnue)"
        )
        self.nom = f"Recrutement de {prenom} {nom} - {nature}"
        self.name = self.nom

    @property
    def date_debut(self) -> date | None:
        return parse_date(self.data.get("date_debut"))

    @property
    def date_fin(self) -> date | None:
        return parse_date(self.data.get("date_fin"))

    @property
    def duree_jours(self) -> int:
        if not (self.date_fin and self.date_debut):
            return 0
        return (self.date_fin - self.date_debut).days + 1

    @property
    def duree_mois(self) -> int:
        if not (self.date_fin and self.date_debut):
            return 0
        years = self.date_fin.year - self.date_debut.year
        months = self.date_fin.month - self.date_debut.month
        days = self.date_fin.day - self.date_debut.day
        return 12 * years + months + round(days / 30.4375)
        # return (self.date_fin - self.date_debut).days + 1

    @property
    def cout_total_charge(self) -> Decimal:
        try:
            return cout_total_charge(self)
        except Exception:
            return Decimal(0)

    def get_extra_errors(self) -> list[str]:
        errors: list[str] = []
        if not self.attachments:
            errors += ["Vous devez obligatoirement attacher une pièce-jointe."]
        if self.date_fin and self.date_debut and self.date_fin <= self.date_debut:
            errors += ["La date de fin est antérieure à la date de début."]
        return errors


class DemandeConvention(Demande):
    _type = DemandeType.CONVENTION.value
    icon_class = "far fa-briefcase"

    __mapper_args__ = {"polymorphic_identity": _type}

    @property
    def date_debut(self):
        return parse_date(self.data.get("date_depot"))

    def update_nom(self):
        nom_ou_acronyme = self.data.get("nom_ou_acronyme")
        if nom_ou_acronyme:
            self.nom = nom_ou_acronyme
        else:
            self.nom = self.nom_par_defaut()

    def get_extra_errors(self):
        errors = []
        if self.appel_a_projets == "oui":
            if not self.attachments:
                errors += [
                    "Vous devez renseigner la liste des partenaires en pièce-jointe."
                ]

        if self.appel_a_projets == "non" and not self.partenaires:
            errors += ["Vous devez saisir au moins un partenaire dans le formulaire."]

        return errors


class DemandeAvenantConvention(Demande):
    _type = DemandeType.AVENANT_CONVENTION.value
    icon_class = "far fa-briefcase"

    __mapper_args__ = {"polymorphic_identity": _type}

    def update_nom(self):
        nom_ou_acronyme = self.data.get("nom_projet")
        if nom_ou_acronyme:
            self.nom = nom_ou_acronyme
        else:
            self.nom = self.nom_par_defaut()

    @property
    def modifications(self):
        modifs = []
        if self.montant == "oui":
            modifs.append("montant")
        if self.duree == "oui":
            modifs.append("durée")
        if self.programme_scientifique == "oui":
            modifs.append("programme scientifique")
        if self.consortium == "oui":
            modifs.append("consortium")
        if self.autre == "oui":
            modifs.append("autre")
        return ", ".join(modifs) + "."


# Abstract
class DemandePiMixin:
    intitule = ""
    acronyme = ""
    titre = ""

    def update_nom(self):
        intitule = self.intitule or self.titre
        acronyme = self.acronyme
        if acronyme and intitule:
            self.nom = f"{intitule} ({acronyme})"
        elif acronyme or intitule:
            self.nom = acronyme or intitule
        else:
            self.nom = self.nom_par_defaut()


# Concrete
class DemandePiLogiciel(Demande, DemandePiMixin):
    _type = DemandeType.PI_LOGICIEL.value
    icon_class = "far fa-save"

    __mapper_args__ = {"polymorphic_identity": _type}

    @property
    def intitule(self):
        return self.data.get("intitule", "")

    @property
    def acronyme(self):
        return self.data.get("acronyme", "")


class DemandePiInvention(Demande, DemandePiMixin):
    _type = DemandeType.PI_INVENTION.value
    icon_class = "far fa-rocket"

    __mapper_args__ = {"polymorphic_identity": _type}

    @property
    def titre(self):
        return self.data.get("titre", "")


class DemandeAutre(Demande):
    _type = DemandeType.AUTRE.value
    commentaire = ""
    icon_class = "far fa-folder-open"

    __mapper_args__ = {"polymorphic_identity": _type}

    @property
    def titre(self):
        return self.data.get("titre", "")

    def update_nom(self):
        self.nom = self.titre


_REGISTRY: dict[str, type[Demande]] = {
    "rh": DemandeRH,
    "convention": DemandeConvention,
    "avenant_convention": DemandeAvenantConvention,
    "pi_logiciel": DemandePiLogiciel,
    "pi_invention": DemandePiInvention,
    "autre": DemandeAutre,
}


def demande_factory(type: str, demandeur: Profile, data: dict, **args: dict) -> Demande:
    demande_cls = _REGISTRY.get(type)
    if not demande_cls:
        raise RuntimeError(f"Type de demande illégal: {type}")

    demande = demande_cls(**args)
    demande.update_data(data)
    demande.log_creation(demandeur)
    return demande


class Validation:
    def __init__(
        self, obj: Demande, errors: list[Any], extra_errors: list[str]
    ) -> None:
        self.obj = obj
        self.errors = errors
        self.extra_errors = extra_errors

    @property
    def ok(self) -> bool:
        return (not self.errors) and (not self.extra_errors)


class DemandeRepository(Repository):
    def get_all(self) -> Collection[Demande]:
        raise NotImplementedError


@singledispatch
def get_bureau_dri(demande) -> ContactType:
    raise NotImplementedError


@get_bureau_dri.register
def get_bureau_dri_convention(demande: DemandeConvention):
    return _get_bureau_dri_convention(demande)


@get_bureau_dri.register
def get_bureau_dri_avenant_convention(demande: DemandeAvenantConvention):
    return _get_bureau_dri_convention(demande)


def _get_bureau_dri_convention(demande: Demande):
    """Le choix dans cette liste et la case à cocher "Le projet intègre-t-
    il une entreprise ? " pour ANR détermine le destinataire des infos du
    formulaire:

    - Si "ANR" est choisi et "non " coché = bureau des contrats publics
    - Si "ANR" est choisi et "oui " coché = bureau Entreprises
    - Si "Commission européenne" est choisi = bureau Europe
    - Si "Entreprise" est choisi = bureau Entreprises
    - Si "Financement public national" est choisi = bureau des contrats publics
    - Si "FUI" est choisi  = bureau Entreprises
    - Si "Institution européenne et internationale" est choisi = bureau des contrats publics
    - Si "Autre" est choisi  et "oui " coché = bureau Entreprises
    - Si "Autre" est choisi  et "non " coché = référent du laboratoire

    +

    Champ Type de financeur : il y a un problème d'adressage du formulaire
    quand Type de financeur=ANR.
    Si Type de financeur=ANR ET "Le projet intègre-t-il une entreprise=non"
    le formulaire est à envoyer au bureau Contrats publics
    Mais si Type de financeur=ANR ET "Le projet intègre-t-il une entreprise=oui",
    le formulaire est à envoyer au bureau Entreprises et transfert de technologie
    """

    type_financeur = demande.data.get("type_financeur")
    if not type_financeur:
        return

    integre_entreprise = demande.data.get("integre_entreprise")
    if integre_entreprise == "non":
        integre_entreprise = False

    bureau = None
    if type_financeur == "ANR":
        if integre_entreprise:
            bureau = ContactType.CONTACT_ENTREPRISES
        else:
            bureau = ContactType.CONTACT_CONTRATS_PUBLICS
    elif type_financeur == "Commission Européenne":
        bureau = ContactType.CONTACT_EUROPE
    elif type_financeur == "Entreprise":
        bureau = ContactType.CONTACT_ENTREPRISES
    elif type_financeur == "Financement public national":
        bureau = ContactType.CONTACT_CONTRATS_PUBLICS
    elif type_financeur == "FUI":
        bureau = ContactType.CONTACT_ENTREPRISES
    elif type_financeur == "Institution européenne et internationale":
        bureau = ContactType.CONTACT_CONTRATS_PUBLICS
    elif type_financeur == "Fondation":
        bureau = ContactType.CONTACT_CONTRATS_PUBLICS
    elif type_financeur == "Autre":
        if integre_entreprise:
            bureau = ContactType.CONTACT_ENTREPRISES
        else:
            bureau = ContactType.CDP

    assert bureau
    return bureau


@get_bureau_dri.register
def get_bureau_dri_pi(demande: DemandePiMixin):
    return ContactType.CONTACT_PI


@get_bureau_dri.register
def get_bureau_dri_rh(demande: DemandeRH):
    return ContactType.CONTACT_RH


@get_bureau_dri.register
def get_bureau_dri_autre(demande: DemandeAutre):
    return ContactType.CONTACT_DRV


def get_contact_labco(structure: Structure, type: ContactType) -> Profile | None:
    from labster.di import injector

    contact_service = injector.get(ContactService)
    return contact_service.get_contact(structure, type)
