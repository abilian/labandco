from __future__ import annotations

import traceback
from datetime import date, timedelta
from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import Forbidden

from labster.di import injector
from labster.domain2.model.demande import Demande
from labster.domain2.model.profile import Profile
from labster.domain2.services.contacts import ContactService
from labster.domain2.services.roles import Role, RoleService
from labster.rbac import get_drv_membership, is_membre_dri, is_membre_drv
from labster.security import get_current_profile
from labster.types import JSON, JSONDict, JSONList
from labster.util import url_for

db = injector.get(SQLAlchemy)

QUERY = db.session.query(Demande).options(
    joinedload(Demande.structure),
    joinedload(Demande.contact_labco),
    joinedload(Demande.gestionnaire),
    joinedload(Demande.porteur),
)


@method
def get_demandes(scope="all", archives=False) -> JSONList:
    archives = bool(archives)
    profile = get_current_profile()

    view = get_table_view(scope, profile, archives)
    if not view:
        raise Forbidden()

    demandes: List[Demande] = view.get_demandes_for(profile)
    demandes.sort(key=lambda d: d.created_at, reverse=True)
    return demandes_to_json(demandes, profile)


def get_table_view(
    scope: str, user: Profile, archives: bool = False
) -> Optional[TableView]:
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


def mes_demandes(
    user: Profile, archived: bool = False, all: bool = False
) -> List[Demande]:
    query = (
        QUERY.filter(
            or_(
                (Demande.porteur == user),
                (Demande.contact_labco == user),
                (Demande.gestionnaire == user),
            )
        )
        .filter_by(active=(not archived))
        .order_by(Demande.created_at.desc())  # type: ignore
    )
    return query.all()


def mes_taches(user: Profile) -> List[Demande]:
    """Retourne la liste des demandes pour lesquels l'utilisateur a une
    action à réaliser."""
    return []
    # FIXME
    # query = QUERY.filter(Demande.active == True).order_by(Demande.created_at.desc())
    #
    # if user.has_role("directeur"):
    #     assert user.stucture_dont_je_suis_le_directeur
    #     ma_structure = user.stucture_dont_je_suis_le_directeur
    #     mes_structures = [ma_structure] + ma_structure.descendants()
    #     ids = [l.id for l in mes_structures]
    #     query = query.filter(Demande.structure_id.in_(ids))
    #
    # elif user.has_role("porteur"):
    #     query = query.filter(Demande.porteur == user)
    #
    # elif user.has_role("gestionnaire"):
    #     query = query.filter(Demande.gestionnaire == user)
    #
    # else:
    #     return []
    #
    # demandes = query.all()
    #
    # def is_task(demande):
    #     workflow = demande.get_workflow(user)
    #     state = workflow.current_state()
    #     return user in state.task_owners(workflow)
    #
    # demandes = [d for d in demandes if is_task(d)]
    # return demandes


def mes_taches_en_retard(user: Profile) -> List[Demande]:
    demandes = mes_taches(user)
    demandes = list(filter(lambda d: d.wf_retard > 0, demandes))
    demandes = sorted(demandes, key=lambda d: d.wf_retard, reverse=True)
    return demandes


#
# Scopes "recherche"
#
class PorteurTableView(TableView):
    scope = "porteur"
    title = "Mes demandes comme porteur"

    def is_visible_for(self, user: Profile):
        return user.has_role(Role.PORTEUR, "*")

    def get_demandes_for(self, user: Profile):
        return (
            QUERY.filter(Demande.porteur == user)
            .filter_by(active=(not self.archives))
            .order_by(Demande.created_at.desc())  # type: ignore
            .all()
        )


class GestionnaireTableView(TableView):
    scope = "gestionnaire"
    title = "Mes demandes comme gestionnaire"

    def is_visible_for(self, user: Profile):
        return user.has_role(Role.GESTIONNAIRE, "*")

    def get_demandes_for(self, user: Profile):
        return (
            QUERY.filter(Demande.gestionnaire == user)
            .filter_by(active=(not self.archives))
            .order_by(Demande.created_at.desc())  # type: ignore
            .all()
        )


class MesStructuresTableView(TableView):
    scope = "mes structures"
    title = "Les demandes de mes structures"

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
        return (
            QUERY.filter(Demande.structure_id.in_({s.id for s in structures}))  # type: ignore
            .filter_by(active=(not self.archives))
            .order_by(Demande.created_at.desc())  # type: ignore
            .all()
        )


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
    title = "Demandes archivées de mes structures"
    archives = True


#
# DRI et DRV
#
class DriTableView(TableView):
    scope = "dri"
    title = "Toutes les demandes à la DR&I et dans les DRV"

    def is_visible_for(self, user: Profile):
        return is_membre_dri(user)

    def get_demandes_for(self, user: Profile):
        query = (
            QUERY.filter_by(active=(not self.archives))
            .filter(Demande.contact_labco != None)
            .order_by(Demande.created_at.desc())  # type: ignore
        )
        return query.all()


class DrvTableView(TableView):
    scope = "drv"
    title = "Toutes les demandes dans ma DRV"

    def is_visible_for(self, user: Profile):
        return is_membre_drv(user)

    def get_demandes_for(self, user: Profile):
        query = (
            QUERY.filter_by(active=(not self.archives))
            .filter(Demande.contact_labco != None)
            .order_by(Demande.created_at.desc())  # type: ignore
        )
        demandes = query.all()

        drv = get_drv_membership(user)
        if drv:
            fac = drv.parent
            assert fac
            structures_possibles = {fac} | fac.descendants
            demandes = [
                demande
                for demande in demandes
                if demande.laboratoire in structures_possibles
            ]
            return demandes

        return []


class ContactTableView(TableView):
    scope = "contact"
    title = "Mes demandes comme contact Lab&Co"

    def is_visible_for(self, user: Profile):
        return is_membre_dri(user) or is_membre_drv(user)

    def get_demandes_for(self, user: Profile):
        return (
            QUERY.filter(Demande.contact == user)
            .filter_by(active=(not self.archives))
            .order_by(Demande.created_at.desc())  # type: ignore
            .all()
        )


class MesStructuresDriOuDrvTableView(TableView):
    scope = "mes structures dri"
    title = "Les demandes de mes structures"

    def is_visible_for(self, user: Profile):
        contact_service = injector.get(ContactService)
        mapping = contact_service.get_mapping()
        return (is_membre_dri(user) or is_membre_drv(user)) and mapping

    def get_demandes_for(self, user: Profile):
        contact_service = injector.get(ContactService)
        mapping = contact_service.get_mapping()
        structures = {s for s, d in mapping.items() if user in d.items()}
        for s in set(structures):
            structures |= s.descendants

        return (
            QUERY.filter(Demande.structure_id.in_({s.id for s in structures}))  # type: ignore
            .filter_by(active=(not self.archives))
            .order_by(Demande.created_at.desc())  # type: ignore
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
    title = "Demandes archivées de mes structures"
    archives = True


#
# Serialization
#
def demandes_to_json(demandes: List[Demande], user: Profile) -> JSONList:
    result: List[JSON] = []

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
    owners = workflow.current_owners()
    if owners:
        row["owner"] = f"{owners[0].nom}, {owners[0].prenom}"
    else:
        row["owner"] = ""

    return row


def format_date(d: Optional[date]) -> str:
    if d:
        return d.strftime("%d/%m/%Y")
    else:
        return ""


def isoformat_date(d: Optional[date]) -> str:
    if d:
        return d.isoformat()
    else:
        return ""
