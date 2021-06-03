from __future__ import annotations

from tqdm import tqdm

from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.roles import Role, RoleService


class RolesUpdater:
    def __init__(self):
        self.profile_repo = injector.get(ProfileRepository)
        self.structure_repo = injector.get(StructureRepository)
        self.role_service = injector.get(RoleService)

    def update_roles(self, max=0):
        profiles = self.profile_repo.get_all()
        print("nbre de profils", len(profiles))
        if max:
            profiles = list(profiles)[0:max]
        for profile in tqdm(profiles, disable=None):
            if not profile.active:
                continue
            self.update_roles_for(profile)

    def update_roles_for(self, user: Profile):
        self.update_role_membre_affecte(user)
        self.role_service.update_roles(user)

        # TODO
        # self.update_role_porteur(user)

    def update_role_membre_affecte(self, user: Profile):
        roles = self.role_service.get_roles_for_user(user)
        structures_actuelles = list(roles.get(Role.MEMBRE_AFFECTE, []))
        if (
            len(structures_actuelles) == 1
            and structures_actuelles[0].dn == user.affectation
        ):
            return

        for structure in structures_actuelles:
            self.role_service.ungrant_role(user, Role.MEMBRE_AFFECTE, structure)

        structure = self.structure_repo.get_by_dn(user.affectation)
        if structure:
            self.role_service.grant_role(user, Role.MEMBRE_AFFECTE, structure)

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
