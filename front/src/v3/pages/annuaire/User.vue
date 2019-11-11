<template>
  <div>
    <div>
      <breadcrumbs :path="path" :title="title"></breadcrumbs>

      <div v-if="ready && user.active" class="alert alert-danger" role="alert">
        Attention, cet utilisateur a été désactivé (il n'est plus dans
        l'annuaire de l'université ou n'a plus de rôle actif dans l'application
        Lab&amp;Co).
      </div>

      <div class="card">
        <div class="card-header">
          <h3 v-if="ready" class="card-title">
            Profil: {{ user.prenom }} {{ user.nom }}
          </h3>
          <h3 v-else class="card-title">Chargement en cours...</h3>
        </div>

        <div class="card-body table-responsive p-0 m-0">
          <table v-if="ready" class="table table-striped">
            <tbody>
              <tr>
                <td class="text-muted text-right w-25">Nom</td>
                <td class="w-75">{{ user.nom }}</td>
              </tr>

              <tr>
                <td class="text-muted text-right">Prénom</td>
                <td>{{ user.prenom }}</td>
              </tr>

              <tr>
                <td class="text-muted text-right">Email</td>
                <td>{{ user.email }}</td>
              </tr>

              <tr v-if="user.telephone">
                <td class="text-muted text-right">Téléphone</td>
                <td>+{{ user.telephone }}</td>
              </tr>

              <tr>
                <td class="text-muted text-right">
                  Structures d'affectaction
                </td>
                <td>
                  <router-link
                    v-if="structure_affectation"
                    :to="{
                      name: 'structure',
                      params: { id: structure_affectation.id },
                    }"
                    >{{ structure_affectation.name }}
                  </router-link>
                </td>
              </tr>

              <tr v-if="user.adresse">
                <td class="text-muted text-right">Adresse</td>
                <td class="">{{ user.adresse | nl2br }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Info LDAP</h3>
        </div>

        <div class="card-body table-responsive p-0 m-0">
          <table v-if="ready" class="table table-striped">
            <tbody>
              <tr>
                <td class="text-muted text-right w-25">uid</td>
                <td class="w-75">{{ user.uid }}</td>
              </tr>

              <tr>
                <td class="text-muted text-right">Affectation</td>
                <td>{{ user.affectation }}</td>
              </tr>

              <tr>
                <td class="text-muted text-right">Fonctions</td>
                <td>{{ user.fonctions.join(", ") }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Rôles</h3>
        </div>

        <div v-if="roles.length > 0" class="card-body table-responsive p-0">
          <table class="table table-striped">
            <thead>
              <tr>
                <th class="w-50">Structure</th>
                <th class="w-50">Rôles</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="role in roles">
                <td class="w-50">
                  <router-link
                    :to="{
                      name: 'structure',
                      params: { id: role.structure.id },
                    }"
                    >{{ role.structure.name }} ({{ role.structure.type }})
                  </router-link>
                </td>
                <td class="w-50">
                  <role-list :roles="role.roles"></role-list>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Périmètre DR&amp;I / DRV</h3>
        </div>

        <div v-if="ready" class="card-body table-responsive p-0">
          <table v-if="perimetre.length > 0" class="table table-striped">
            <thead>
              <tr>
                <th class="w-50">Structure</th>
                <th class="w-50">Rôles</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="entree in perimetre">
                <td class="w-50">
                  <router-link
                    :to="{
                      name: 'structure',
                      params: { id: entree.structure.id },
                    }"
                    >{{ entree.structure.name }} ({{ entree.structure.type }})
                  </router-link>
                </td>
                <td class="w-50">
                  {{ entree.types.join(", ") }}
                </td>
              </tr>
            </tbody>
          </table>

          <div v-else class="card-body">
            L'utilisateur n'a actuellement aucun rôle comme contact DR&amp;I.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import RoleList from "./components/RoleList";
import { ContextFetcher } from "../../mixins";

export default {
  props: { id: String },

  mixins: [ContextFetcher],

  components: { RoleList },

  data() {
    return {
      path: [["Utilisateurs", "/annuaire/users"]],
      user: { active: true },
      structure_affectation: null,
      roles: [],
      perimetre: [],
      title: "Chargement en cours...",
    };
  },

  computed: {
    debug() {
      // eslint-disable-next-line
      return DEBUG;
    },
  },

  methods: {
    whenReady() {
      this.title = this.user.prenom + " " + this.user.nom;
      this.ready = true;
    },
  },
};
</script>
