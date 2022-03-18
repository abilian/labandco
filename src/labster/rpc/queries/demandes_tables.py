from __future__ import annotations

import traceback
from datetime import date, timedelta

import ramda as r
from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from labster.di import injector
from labster.domain2.model.demande import Demande, DemandeAutre, \
    DemandeAvenantConvention, DemandeConvention, DemandePiMixin, DemandeRH
from labster.domain2.model.profile import Profile
from labster.domain2.services.contacts import ContactService
from labster.domain2.services.roles import Role, RoleService
from labster.domain2.services.workflow.states import EN_EDITION, EN_VALIDATION
from labster.rbac import get_drv_membership, is_membre_dri, is_membre_drv
from labster.rpc.queries.cache import memoize
from labster.rpc.util import owner_sorter
from labster.security import get_current_profile
from labster.types import JSON, JSONDict, JSONList
from labster.util import url_for


def base_query():
    db = injector.get(SQLAlchemy)

    return db.session.query(Demande).options(
        joinedload(Demande.structure),
        joinedload(Demande.contact_labco),
        joinedload(Demande.gestionnaire),
        joinedload(Demande.porteur),
    )


@method
def get_demandes(scope="all", archives=False, tag="") -> JSONList:
    archives = bool(archives)
    profile = get_current_profile()

    view = get_table_view(scope, profile, archives)
    if not view:
        return []

    demandes: list[Demande] = view.get_demandes_for(profile)

    def make_pred(tag):
        def pred(demande):
            if tag == "rh":
                return isinstance(demande, DemandeRH)
            elif tag == "conventions":
                return isinstance(
                    demande, (DemandeConvention, DemandeAvenantConvention)
                )
            elif tag == "pi":
                return isinstance(demande, DemandePiMixin)
            elif tag == "autres":
                return isinstance(demande, DemandeAutre)
            else:
                raise RuntimeError()

        return pred

    if tag:
        demandes = r.filter(make_pred(tag), demandes)

    demandes.sort(key=lambda d: d.created_at, reverse=True)
    return demandes_to_json(demandes, profile)


def get_table_view(
    scope: str, user: Profile, archives: bool = False
) -> TableView | None:
    all_table_views = [
        cls()
        for cls in globals().values()
        if isinstance(cls, type) and issubclass(cls, TableView)
    ]

    view = None
    for x in all_table_views:
        if x.scope != scope or x.archives != archives:
            continue

        view = x
        break

    if not view:
        return None

    if not view.is_visible_for(user):
        return None

    return view


#
# Demandes actives
#
class TableView:
    scope = ""
    title = ""
    archives = False

    def is_visible_for(self, user: Profile):
        return False

    def get_demandes_for(self, user: Profile):
        return []


#
# Scopes génériques
#
class MesDemandesTableView(TableView):
    scope = "mes demandes"

    def is_visible_for(self, user: Profile):
        return True

    def get_demandes_for(self, user: Profile):
        return mes_demandes(user)


class MesTachesTableView(TableView):
    scope = "mes tâches"

    def is_visible_for(self, user: Profile):
        return True

    def get_demandes_for(self, user: Profile):
        return mes_taches(user)


class MesDemandesEnRetardTableView(TableView):
    scope = "mes demandes en retard"

    def is_visible_for(self, user: Profile):
        return True

    def get_demandes_for(self, user: Profile):
        return mes_taches_en_retard(user)


class DemandesAValiderTableView(TableView):
    scope = "demandes à valider"

    def is_visible_for(self, user: Profile):
        return True

    def get_demandes_for(self, user: Profile):
        demandes = mes_taches(user)
        demandes = [d for d in demandes if d.wf_state == EN_VALIDATION.id]
        return demandes


def mes_demandes(
    user: Profile, archived: bool = False, all: bool = False
) -> list[Demande]:
    query = (
        base_query()
        .filter(
            or_(
                (Demande.porteur == user),
                (Demande.contact_labco == user),
                (Demande.gestionnaire == user),
            )
        )
        .filter_by(active=(not archived))
        .order_by(Demande.created_at.desc())
    )
    return query.all()


@memoize()
def mes_taches(user: Profile) -> list[Demande]:
    """Retourne la liste des demandes pour lesquels l'utilisateur a une action
    à réaliser."""
    query = (
        base_query().filter(Demande.active == True).order_by(Demande.created_at.desc())
    )

    demandes = query.all()

    def is_task(demande):
        workflow = demande.get_workflow(user)
        state = workflow.current_state()
        owners = state.task_owners(workflow)
        return user.id in (o.id for o in owners)

    demandes = [d for d in demandes if is_task(d)]
    return demandes


def mes_taches_en_retard(user: Profile) -> list[Demande]:
    demandes = mes_taches(user)

    def en_retard(d) -> bool:
        return (d.wf_retard or 0) > 0

    demandes = list(filter(en_retard, demandes))
    demandes = sorted(demandes, key=lambda d: d.wf_retard, reverse=True)
    return demandes


#
# Scopes "recherche"
#
class PorteurTableView(TableView):
    scope = "porteur"
    title = "Demandes dont je suis porteur"

    def is_visible_for(self, user: Profile):
        return user.has_role(Role.PORTEUR, "*")

    def get_demandes_for(self, user: Profile):
        demandes_comme_porteur = (
            base_query()
            .filter(Demande.porteur == user)
            .filter_by(active=(not self.archives))
            .order_by(Demande.created_at.desc())
            .all()
        )
        toutes_les_demandes = (
            base_query()
            .filter_by(active=(not self.archives))
            .order_by(Demande.created_at.desc())
            .all()
        )

        demandes_comme_contributeur = []
        for demande in toutes_les_demandes:
            contributeurs_raw = demande.data.get("contributeurs", [])
            for dd in contributeurs_raw:
                contributeur_id = dd["value"]
                if contributeur_id == user.id:
                    demandes_comme_contributeur += [demande]

        def sorter(d):
            return d.created_at

        return sorted(
            set(demandes_comme_porteur + demandes_comme_contributeur), key=sorter
        )


class GestionnaireTableView(TableView):
    scope = "gestionnaire"
    title = "Demandes dont je suis gestionnaire"

    def is_visible_for(self, user: Profile):
        return user.has_role(Role.GESTIONNAIRE, "*")

    def get_demandes_for(self, user: Profile):
        return (
            base_query()
            .filter(Demande.gestionnaire == user)
            .filter_by(active=(not self.archives))
            .order_by(Demande.created_at.desc())
            .all()
        )


class MesStructuresTableView(TableView):
    scope = "mes structures"
    title = "Demandes des structures dont je suis un responsable/gestionnaire"

    def is_visible_for(self, user: Profile):
        return user.has_role(Role.GESTIONNAIRE, "*") or user.has_role(
            Role.RESPONSABLE, "*"
        )

    def get_demandes_for(self, user: Profile):
        role_service = injector.get(RoleService)
        roles = role_service.get_roles_for_user(user)
        structures = set(roles[Role.GESTIONNAIRE]) | set(roles[Role.RESPONSABLE])
        for s in set(structures):
            structures |= s.descendants

        structure_ids = {s.id for s in structures}

        toutes_les_demandes = (
            base_query()
            .filter_by(active=(not self.archives))
            .order_by(Demande.created_at.desc())
            .all()
        )

        result = []
        for demande in toutes_les_demandes:
            if demande.structure_id in structure_ids:
                result.append(demande)
                continue

            for d in demande.data.get("structures_concernees", []):
                structure_id = d["value"]
                if structure_id in structure_ids:
                    result.append(demande)

        return result


#
# Archives recherche
#
class ArchivesPorteurTableView(PorteurTableView):
    title = "Demandes archivées dont j'ai été porteur"
    archives = True


class ArchivesGestionnaireTableView(GestionnaireTableView):
    title = "Demandes archivées dont j'ai été gestionnaire"
    archives = True


class ArchivesMesStructuresTableView(MesStructuresTableView):
    title = "Demandes archivées des structures dont je suis un responsable/gestionnaire"
    archives = True


#
# DRI et DRV
#
class DriTableView(TableView):
    scope = "dri"
    title = "Demandes en cours à la DR&I et dans les DRV"

    def is_visible_for(self, user: Profile):
        return is_membre_dri(user)

    def get_demandes_for(self, user: Profile):
        query = (
            base_query()
            .filter_by(active=(not self.archives))
            .filter(Demande.contact_labco != None)
            .order_by(Demande.created_at.desc())
        )
        return filter_on_state_for_dri(query.all())


class DrvTableView(TableView):
    scope = "drv"
    title = "Demandes en cours dans ma DRV"

    def is_visible_for(self, user: Profile):
        return is_membre_drv(user)

    def get_demandes_for(self, user: Profile):
        query = (
            base_query()
            .filter_by(active=(not self.archives))
            .filter(Demande.contact_labco != None)
            .order_by(Demande.created_at.desc())
        )
        demandes = query.all()

        drv = get_drv_membership(user)
        if not drv:
            return []

        fac = drv.parent
        assert fac
        structures_possibles = {fac} | fac.descendants
        ids_structures_possibles = {s.id for s in structures_possibles}

        demandes = [
            demande
            for demande in demandes
            if demande.structure and demande.structure.id in ids_structures_possibles
        ]
        return filter_on_state_for_dri(demandes)


class ContactTableView(TableView):
    scope = "contact"
    title = "Demandes dont je suis contact"

    def is_visible_for(self, user: Profile):
        return is_membre_dri(user) or is_membre_drv(user)

    def get_demandes_for(self, user: Profile):
        return filter_on_state_for_dri(
            base_query()
            .filter(Demande.contact_labco == user)
            .filter_by(active=(not self.archives))
            .order_by(Demande.created_at.desc())
            .all()
        )


@memoize()
def get_mapping():
    contact_service = injector.get(ContactService)
    return contact_service.get_mapping()


class MesStructuresDriOuDrvTableView(TableView):
    scope = "mes structures dri"
    title = "Demandes des structures dont je suis un contact Lab&Co"

    def is_visible_for(self, user: Profile):
        mapping = get_mapping()
        return (is_membre_dri(user) or is_membre_drv(user)) and mapping

    def get_demandes_for(self, user: Profile):
        mapping = get_mapping()
        structures = {s for s, d in mapping.items() if user in d.values()}
        structure_ids = {s.id for s in structures}
        return filter_on_state_for_dri(
            base_query()
            .filter(Demande.structure_id.in_(structure_ids))
            .filter(Demande.contact_labco != None)
            .filter_by(active=(not self.archives))
            .order_by(Demande.created_at.desc())
            .all()
        )


#
# Archives DR&I
#
class ArchivesDriTableView(DriTableView):
    title = "Demandes archivées à la DR&I"
    archives = True


class ArchivesDrvTableView(DrvTableView):
    title = "Demandes archivées dans ma DRV"
    archives = True


class ArchivesContactTableView(ContactTableView):
    title = "Demandes archivées dont j'ai été le contact"
    archives = True


class ArchivesMesStructuresDriOuDrvTableView(MesStructuresDriOuDrvTableView):
    title = "Demandes archivées des structures dont je suis un contact"
    archives = True


#
# Util
#
def filter_on_state_for_dri(demandes: list[Demande]) -> list[Demande]:
    result = []
    for demande in demandes:
        wf_states = {
            state["new_state"] for state in demande.wf_history if "new_state" in state
        }

        if wf_states != {EN_EDITION.id}:
            result.append(demande)

    return result


#
# Serialization
#
def demandes_to_json(demandes: list[Demande], user: Profile) -> JSONList:
    result: list[JSON] = []

    for demande in demandes:
        try:
            row = demande_to_json(demande, user)
            result.append(row)
        except Exception:
            traceback.print_exc()

    return result


def demande_to_json(demande: Demande, user: Profile) -> JSONDict:
    row: JSONDict = {
        "created_at": format_date(demande.created_at),
        "__created_at__": isoformat_date(demande.created_at),
        "icon_class": demande.icon_class,
        "type": demande.type,
        "url": url_for(demande),
        "nom": demande.nom or demande.titre,
        "age": demande.age,
        "date_debut": format_date(demande.date_debut),
        "__date_debut__": isoformat_date(demande.date_debut),
    }

    date_soumission = demande.date_soumission
    if date_soumission:
        duree_traitement: timedelta = date.today() - date_soumission
        row["date_soumission"] = (
            format_date(date_soumission) + f" ({duree_traitement.days}j)"
        )
        row["__date_soumission__"] = isoformat_date(date_soumission)
    else:
        row["date_soumission"] = ""
        row["__date_soumission__"] = ""

    row["retard"] = demande.retard
    row["no_infolab"] = demande.no_infolab

    for k in ("porteur", "gestionnaire", "contact_labco"):
        profile = getattr(demande, k)
        if profile:
            row[k] = profile.full_name
            row[k + "_url"] = url_for(profile)
            nom = getattr(profile, "nom", "")
            prenom = getattr(profile, "prenom", "")
            # helps sorting in JS
            row[k + "_nom"] = f"{nom}, {prenom}"
        else:
            row[k] = ""
            row[k + "_url"] = ""
            row[k + "_nom"] = ""

    structure = demande.structure
    if structure:
        row["structure"] = structure.sigle_ou_nom
        row["structure_url"] = url_for(structure)
        # laboratoire = structure.laboratoire
        # row["laboratoire"] = laboratoire.sigle_ou_nom
        # row["laboratoire_url"] = url_for(laboratoire)
    else:
        row["structure"] = ""
        row["structure_url"] = ""
    # TODO: remove
    row["laboratoire"] = ""
    row["laboratoire_url"] = ""

    # Workflow
    workflow = demande.get_workflow(user)
    state = demande.get_state()
    row["etat"] = state.label_short
    row["prochaine_action"] = state.next_action
    owners = list(workflow.current_owners())
    owners.sort(key=owner_sorter)
    if owners:
        row["owner"] = f"{owners[0].nom}, {owners[0].prenom}"
    else:
        row["owner"] = ""

    row["owners"] = [
        {
            "name": f"{owner.nom}, {owner.prenom}",
            "id": owner.id,
        }
        for owner in owners
    ]

    return row


def format_date(d: date | None) -> str:
    if d:
        return d.strftime("%d/%m/%Y")
    else:
        return ""


def isoformat_date(d: date | None) -> str:
    if d:
        return d.isoformat()
    else:
        return ""
