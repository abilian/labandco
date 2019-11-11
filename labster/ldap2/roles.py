from __future__ import annotations

from dataclasses import dataclass

from tqdm import tqdm

from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.roles import Role, RoleService

profile_repo = injector.get(ProfileRepository)
structure_repo = injector.get(StructureRepository)
role_service = injector.get(RoleService)


@dataclass
class RolesUpdater:
    def update_roles(self):
        profiles = profile_repo.get_all()
        print("nbre de profils", len(profiles))
        for profile in tqdm(profiles):
            if not profile.active:
                continue
            self.update_role(profile)

    def update_role(self, user: Profile):
        self.update_role_membre_affecte(user)
        role_service.update_roles(user)

        # TODO
        # self.update_role_porteur(user)

    def update_role_membre_affecte(self, user: Profile):
        roles = role_service.get_roles_for_user(user)
        structures_actuelles = roles.get(Role.MEMBRE_AFFECTE, [])
        if (
            len(structures_actuelles) == 1
            and structures_actuelles[0].dn == user.affectation
        ):
            return

        for structure in structures_actuelles:
            role_service.ungrant_role(user, Role.MEMBRE_AFFECTE, structure)

        structure = structure_repo.get_by_dn(user.affectation)
        role_service.grant_role(user, Role.MEMBRE_AFFECTE, structure)

    # def update_role_porteur(self, user: Profile):
    #     if "researcher" in user.fonctions or "faculty" in user.fonctions:
    #         self.remove_role_porteur(user)
    #         structure = self.structure_repository.get_by_dn(user.affectation)
    #         self.role_service.grant_role(user, Role.PORTEUR, structure)
    #
    #     else:
    #         self.remove_role_porteur(user)
    #
    # def remove_role_porteur(self, user: Profile):
    #     roles = self.role_service.get_roles_for_user(user)
    #     structures = roles.get(Role.PORTEUR, [])
    #     for structure in structures:
    #         self.role_service.ungrant_role(user, Role.PORTEUR, structure)
