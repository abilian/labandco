from __future__ import annotations

from collections.abc import Collection
from enum import Enum, unique
from typing import Any

from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure


@unique
class Role(Enum):
    # Rôles locaux (à une structure)
    MEMBRE = "Membre"
    MEMBRE_AFFECTE = "Membre affecté"
    MEMBRE_RATTACHE = "Membre rattaché"
    MEMBRE_AFFILIE = "Membre affilié"

    RESPONSABLE = "Responsable"
    GESTIONNAIRE = "Gestionnaire Lab&Co"
    PORTEUR = "Porteur Lab&Co"
    SIGNATAIRE = "Signataire"
    ADMIN_LOCAL = "Administrateur Lab&Co local"

    # Rôles locaux (à une demande)
    CONTRIBUTEUR = "Contributeur"

    # Rôle globaux
    ADMIN_CENTRAL = "Administrateur central"
    FAQ_EDITOR = "Editeur de la FAQ"

    CONTACT = "Contact Lab&Co"


ROLE_MAP = {
    "porteur": Role.PORTEUR,
    "responsable": Role.RESPONSABLE,
    "gestionnaire": Role.GESTIONNAIRE,
    "admin_local": Role.ADMIN_LOCAL,
}


class RoleService:
    def is_empty(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def grant_role(self, user: Profile, role: Role, context: Any = None):
        raise NotImplementedError

    def ungrant_role(self, user: Profile, role: Role, context: Any = None):
        raise NotImplementedError

    def has_role(self, user: Profile, role: Role, context: Any = None):
        raise NotImplementedError

    def get_users_with_role(self, role: Role, context: Any = None):
        raise NotImplementedError

    def get_users_with_role_on(self, context: Structure) -> dict[Role, set[Profile]]:
        raise NotImplementedError

    def get_users_with_given_role(
        self, role: Role, context: Structure
    ) -> Collection[Profile]:
        raise NotImplementedError

    def get_roles_for_user(self, user: Profile) -> dict[Role, set[Structure]]:
        raise NotImplementedError

    def update_roles(self, user: Profile):
        roles = self.get_roles_for_user(user)

        structures: set[Structure]

        structures = roles[Role.MEMBRE]
        for structure in structures:
            self.ungrant_role(user, Role.MEMBRE, structure)

        structures = roles[Role.MEMBRE_AFFILIE]
        for structure in structures:
            self.ungrant_role(user, Role.MEMBRE_AFFILIE, structure)

        structures = roles[Role.MEMBRE_AFFECTE] | roles[Role.MEMBRE_RATTACHE]

        for structure in structures:
            self.grant_role(user, Role.MEMBRE, structure)

        ancestors = set()
        for structure in structures:
            if structure:
                ancestors.update(structure.ancestors)

        for structure in ancestors:
            self.grant_role(user, Role.MEMBRE_AFFILIE, structure)
            self.grant_role(user, Role.MEMBRE, structure)
