<template>
  <div>
    <b-navbar toggleable="lg" type="dark" class="main-header navbar-secondary">
      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

      <b-collapse id="nav-collapse" is-nav>
        <!-- SEARCH FORM -->
        <form class="form-inline ml-3">
          <div class="input-group input-group-sm">
            <input
              class="form-control form-control-navbar"
              type="search"
              placeholder="Search"
              aria-label="Search"
              v-model="q"
              @keydown.enter="onSearch"
            />
            <div class="input-group-append">
              <button class="btn btn-navbar" type="submit" @click="onSearch">
                <i class="far fa-search"></i>
              </button>
            </div>
          </div>
        </form>

        <!-- Right aligned nav items -->
        <b-navbar-nav class="ml-auto">
          <b-nav-item to="/contacts" title="Mes contacts">
            <i class="far fa-lg fa-heart"></i>
          </b-nav-item>

          <b-nav-item to="/demandes_en_retard" title="Mes demandes en retard">
            <i class="far fa-lg fa-exclamation-triangle"></i>
            <span
              v-if="user.nb_taches_retard"
              class="badge badge-danger navbar-badge"
              >{{ user.nb_taches_retard }}</span
            >
          </b-nav-item>

          <b-nav-item href="#" title="Mes tâches">
            <i class="far fa-lg fa-check-square"></i>
            <span
              v-if="user.nb_taches"
              class="badge badge-warning navbar-badge"
              >{{ user.nb_taches }}</span
            >
          </b-nav-item>

          <li class="nav-item">
            <router-link
              to="/timeline"
              title="Mes notifications"
              class="nav-link"
            >
              <i class="far fa-lg fa-bullhorn"></i>
              <span
                v-if="user.nb_notifications_non_vues"
                class="badge badge-success navbar-badge"
                >{{ user.nb_notifications_non_vues }}</span
              >
            </router-link>
          </li>

          <b-nav-item-dropdown right>
            <!-- Using 'button-content' slot -->
            <template slot="button-content"
              ><i class="far far-user"></i> {{ user.name }}
            </template>

            <b-dropdown-item :to="{ name: 'user', params: { id: user.id } }"
              >Mon profil utilisateur</b-dropdown-item
            >

            <b-dropdown-item to="/preferences">Préférences</b-dropdown-item>

            <b-dropdown-divider></b-dropdown-divider>

            <b-dropdown-item v-if="user.is_admin" href="/switch"
              >Changer d'utilisateur</b-dropdown-item
            >
            <b-dropdown-item href="#" @click="onLogout()"
              >Déconnexion</b-dropdown-item
            >
          </b-nav-item-dropdown>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      q: "",
    };
  },

  computed: {
    user() {
      return this.$storage.get("user");
    },
  },

  methods: {
    onSearch() {
      this.$router.push({ path: "/search", query: { q: this.q } });
    },

    onLogout() {
      this.$storage.clear();
      axios.post("/login").then(response => {
        window.location.href = "/";
      });
    },
  },
};
</script>
