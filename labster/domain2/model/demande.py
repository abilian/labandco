from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum, unique
from typing import Any, Collection, Dict, List, Optional, Type

import dateutil
import sqlalchemy as sa
from abilian.app import db
from abilian.core.models.blob import Blob
from flask_sqlalchemy import SQLAlchemy
from iso8601 import iso8601
from sqlalchemy import JSON, Boolean, Column, Date, DateTime, ForeignKey, \
    Integer, String
from sqlalchemy.orm import relationship

from labster.domain2.model.base import Repository
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure
from labster.domain2.model.util import parse_date
from labster.domain2.services.calculs_couts import cout_total_charge
from labster.domain2.services.workflow import EN_EDITION, LabsterWorkflow
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

    _type: DemandeType = DemandeType.ILLEGAL

    id = Column(Integer, primary_key=True)
    old_id = Column(Integer)
    type = Column(
        sa.Enum(*types_demande, name="type_demande"), nullable=False, index=True,
    )
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    #
    nom = Column(String)
    name = Column(String)
    active = Column(Boolean)
    editable = Column(Boolean)
    no_infolab = Column(String)
    no_eotp = Column(String)

    # Relations
    contact_labco_id = Column(String(36), ForeignKey(Profile.id))
    gestionnaire_id = Column(String(36), ForeignKey(Profile.id))
    porteur_id = Column(String(36), ForeignKey(Profile.id))
    structure_id = Column(String(36), ForeignKey(Structure.id))

    #
    data = Column(JSON)
    past_versions = Column(JSON)
    form_state = Column(JSON)
    attachments = Column(JSON)
    feuille_cout = Column(JSON)
    documents_generes = Column(JSON)

    # Workflow
    # wf_state = Column(WF_ENUM, default=EN_EDITION.id, nullable=False, index=True)
    wf_state = Column(String)
    wf_date_derniere_action = Column(DateTime)
    wf_retard = Column(Integer)
    wf_history = Column(JSON)
    wf_data = Column(JSON)
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
        nouvelle_demande = Demande(
            nom=self.nom,
            type=self.type,
            wf_state=EN_EDITION.id,
            porteur=self.porteur,
            gestionnaire=self.gestionnaire,
        )
        nouvelle_demande.data = self.data.copy()
        nouvelle_demande.form_state = self.form_state.copy()
        return nouvelle_demande

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

    def has_same_data(self, data: Dict[str, Any]) -> bool:
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
        if self.laboratoire and self.laboratoire.directeur:
            return self.laboratoire.directeur.full_name
        return ""

    # @property
    # def laboratoire(self) -> OrgUnit:
    #     structure = self.structure
    #     if not structure:
    #         if self.porteur:
    #             self.structure = self.porteur.structure
    #         elif self.gestionnaire:
    #             self.structure = self.gestionnaire.laboratoire
    #         structure = self.structure
    #
    #     return structure.laboratoire

    @property
    def owners(self) -> List[Profile]:
        owners = []
        if self.gestionnaire:
            owners.append(self.gestionnaire)
        if self.porteur:
            owners.append(self.porteur)
        return owners

    @property
    def contributeurs(self) -> Collection[Profile]:
        return []

    def is_editable_by(self, user: Profile) -> bool:
        return self.editable and user in [self.gestionnaire, self.porteur]

    def is_duplicable_by(self, user: Profile) -> bool:
        return user in [self.gestionnaire, self.porteur]

    def feuille_cout_is_editable_by(self, user: Profile) -> bool:
        if not self.active:
            return False

        if user in [self.gestionnaire, self.porteur]:
            return True
        if user == self.contact_labco:
            return True

        return False

    #
    # Workflow
    #
    def get_workflow(self, user: Optional[Profile] = None) -> LabsterWorkflow:
        return LabsterWorkflow(self, user)

    def get_state(self, user: Optional[Profile] = None) -> State:
        workflow = self.get_workflow(user)
        return workflow.current_state()

    def current_owners(self) -> List[Profile]:
        return self.get_workflow().current_owners()

    @property
    def date_soumission(self) -> Optional[date]:
        for entry in self.wf_history:
            if entry.get("transition") == "SOUMETTRE":
                return dateutil.parser.parse(entry["date"]).date()

        return None

    @property
    def date_finalisation(self) -> Optional[date]:
        final_states = ["CONFIRMER_FINALISATION_DGRTT", "ABANDONNER", "REJETER_DGRTT"]
        for entry in self.wf_history:
            if entry.get("transition") in final_states:
                return dateutil.parser.parse(entry["date"]).date()

        return None

    #
    # Data validation / manipulation
    #
    def validate(self) -> Validation:
        return Validation(self, self.get_errors(), self.get_extra_errors())

    def get_errors(self) -> List[Any]:
        errors = []
        form_state = self.form_state
        fields = form_state.get("fields", [])
        for field_name, field_value in self.data.items():
            if field_name not in fields:
                continue
            field: Dict[str, Any] = fields[field_name]

            visible: bool = field.get("visible")
            required: bool = field.get("required")

            if visible and required and not field_value:
                errors.append(field["name"])

        return errors

    def get_extra_errors(self):
        return []

    def is_valid(self) -> bool:
        validation = self.validate()
        return validation.ok

    @property
    def errors(self):
        return self.validate().errors

    def update_data(self, data: Dict) -> None:
        self.increase_version()
        self.data.update(data)

        self.update_nom()
        self.post_update()

    # new_name = data.get('nom', None)
    # if new_name is not None and new_name != self.name:
    #     self.name = new_name

    def post_update(self) -> None:
        # TODO: remove
        from labster.di import injector

        db = injector.get(SQLAlchemy)

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
            self.past_versions.append(
                (self.data, datetime.utcnow().strftime("%d %b %Y %H:%M:%S"))
            )

    # Pièces jointes
    @property
    def pieces_jointes(self) -> List[Dict]:
        # TODO: remove
        from labster.di import injector

        db = injector.get(SQLAlchemy)

        result = []
        for k, v in sorted(self.attachments.items()):
            if isinstance(v, dict):
                creator = db.session.query(Profile).get_by_uid(v["creator"])
                d = {"id": v["id"], "name": k, "creator": creator}

                date_str = v.get("date")
                if date_str:
                    d["date"] = iso8601.parse_date(date_str)
                else:
                    d["date"] = None
            else:
                d = {"id": v, "name": k, "creator": None, "date": None}
            id = d["id"]
            blob = Blob.query.get(id)
            if blob:
                result.append(d)
        return result


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

    def assigne_contact_labco(self):
        self.contact_labco = get_contact_labco(self.laboratoire, "CT")

    @property
    def date_debut(self) -> Optional[date]:
        return parse_date(self.data.get("date_debut"))

    @property
    def date_fin(self) -> Optional[date]:
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

    def get_extra_errors(self) -> List[str]:
        errors: List[str] = []
        if not self.pieces_jointes:
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

    def assigne_contact_labco(self):
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
        # Rappel des bureaux
        # BureauDgrtt("ETT", "Entreprises et transfert de technologie"),
        # BureauDgrtt("CFE", "Contrats et financements européens"),
        # BureauDgrtt("CP", "Contrats publics"),
        # BureauDgrtt("CT", "Contrats de travail"),
        # BureauDgrtt("PIJ", "Propriété intellectuelle (juriste)"),
        # BureauDgrtt("PI2", "Propriété intellectuelle 2"),

        type_financeur = self.data.get("type_financeur")
        if not type_financeur:
            return

        integre_entreprise = self.data.get("integre_entreprise")
        if integre_entreprise == "non":
            integre_entreprise = False

        bureau = None
        if type_financeur == "ANR":
            if integre_entreprise:
                bureau = "ETT"
            else:
                bureau = "CP"
        elif type_financeur == "Commission Européenne":
            bureau = "CFE"
        elif type_financeur == "Entreprise":
            bureau = "ETT"
        elif type_financeur == "Financement public national":
            bureau = "CP"
        elif type_financeur == "FUI":
            bureau = "ETT"
        elif type_financeur == "Institution européenne et internationale":
            bureau = "CP"
        elif type_financeur == "Fondation":
            bureau = "CP"
        elif type_financeur == "Autre":
            if integre_entreprise:
                bureau = "ETT"
            else:
                bureau = "REF"

        assert bureau
        self.contact_labco = get_contact_labco(self.laboratoire, bureau)

    def get_extra_errors(self):
        if self.appel_a_projets == "oui":
            if self.pieces_jointes:
                return []
            return ["Vous devez renseigner la liste des partenaires en pièce-jointe."]

        if self.partenaires:
            return []
        return ["Vous devez saisir au moins un partenaire dans le formulaire."]


class DemandeAvenantConvention(DemandeConvention):
    _type = DemandeType.AVENANT_CONVENTION.value
    icon_class = "far fa-briefcase"

    __mapper_args__ = {"polymorphic_identity": _type}

    def update_nom(self):
        nom_ou_acronyme = self.data.get("nom_projet")
        if nom_ou_acronyme:
            self.nom = nom_ou_acronyme
        else:
            self.nom = self.nom_par_defaut()

    def get_extra_errors(self):
        return []

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

    def assigne_contact_labco(self):
        bureau = "PI2"
        self.contact_labco = get_contact_labco(self.laboratoire, bureau)


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


_REGISTRY: Dict[str, Type[Demande]] = {
    "rh": DemandeRH,
    "convention": DemandeConvention,
    "avenant_convention": DemandeAvenantConvention,
    "pi_logiciel": DemandePiLogiciel,
    "pi_invention": DemandePiInvention,
    "autre": DemandeAutre,
}


def demande_factory(type: str, demandeur: Profile, data: Dict, **args: Dict) -> Demande:
    demande_cls = _REGISTRY.get(type)
    if not demande_cls:
        raise RuntimeError(f"Type de demande illégal: {type}")

    demande = demande_cls(**args)
    demande.update_data(data)
    demande.log_creation(demandeur)
    return demande


class Validation:
    def __init__(
        self, obj: Demande, errors: List[Any], extra_errors: List[str]
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


def get_contact_labco(structure: Structure, type: str):
    from labster.domain2.services.contacts import ContactService
    from labster.di import injector

    contact_service = injector.get(ContactService)
    # FIXME
    return contact_service.get_contact(structure, type)
