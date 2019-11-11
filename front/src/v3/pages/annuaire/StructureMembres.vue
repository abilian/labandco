<template>
  <div>
    <template v-if="!editing">
      <b-container class="mt-4 mb-2">
        <b-row>
          <b-col lg="6" class="my-1">
            <b-form-checkbox v-model="filter.montrerSousStructures">
              Montrer les membres des sous-structures.
            </b-form-checkbox>
          </b-col>
          <b-col lg="6" class="my-1">
            <b-form-group
              label="Filter"
              label-cols-sm="3"
              label-align-sm="right"
              label-size="sm"
              label-for="filterInput"
              class="mb-0"
            >
              <b-input-group size="sm">
                <b-form-input
                  v-model="filter.q"
                  type="search"
                  id="filterInput"
                  placeholder="Type to Search"
                ></b-form-input>
                <b-input-group-append>
                  <b-button :disabled="!filter.q" @click="filter.q = ''"
                    >Clear</b-button
                  >
                </b-input-group-append>
              </b-input-group>
            </b-form-group>
          </b-col>
        </b-row>
      </b-container>

      <!-- Main table element -->
      <b-table
        id="table-membres"
        show-empty
        responsive="md"
        outlined
        hover
        :items="provider"
        :fields="fields"
        :current-page="currentPage"
        :per-page="perPage"
        :filter="filter"
        :filter-included-fields="['prenom', 'nom']"
        :filter-function="myFilter"
        :no-provider-paging="true"
        :no-provider-filtering="true"
        :busy.sync="isBusy"
        @filtered="onFiltered"
      >
        <template v-slot:cell(nom)="row">
          <router-link :to="{ name: 'user', params: { id: row.item.id } }"
            >{{ row.item.nom }}
          </router-link>
        </template>

        <template v-slot:cell(prenom)="row">
          <router-link :to="{ name: 'user', params: { id: row.item.id } }"
            >{{ row.item.prenom }}
          </router-link>
        </template>

        <template v-slot:cell(roles)="row">
          <div v-for="entry in row.item.roles">
            <router-link
              :to="{ name: 'structure', params: { id: entry.structure.id } }"
              >{{ entry.structure.name }} ({{ entry.structure.type }})
            </router-link>
            :
            <role-list :roles="entry.roles"></role-list>
          </div>
        </template>

        <template v-slot:table-busy>
          <div class="text-center my-2">
            <b-spinner class="align-middle"></b-spinner>
            <strong>Chargement en cours...</strong>
          </div>
        </template>
      </b-table>

      <b-container>
        <b-row class="text-right">
          <b-col md="8" class="my-1"> </b-col>
          <b-col md="4" class="my-1 text-right">
            <b-pagination
              v-model="currentPage"
              :total-rows="totalRows"
              :per-page="perPage"
            ></b-pagination>
          </b-col>
        </b-row>
      </b-container>

      <button
        v-if="!editing && !isBusy"
        class="btn btn-default mt-3"
        @click="makeEditable"
      >
        Modifier
      </button>
    </template>

    <template v-if="editing">
      <h4 class="mt-5 mb-4">Editer les membres rattachés</h4>

      <div v-if="editing && selector">
        <multiselect
          v-model="selector.value"
          :options="selector.options"
          :multiple="true"
          track-by="id"
          label="label"
        />
      </div>

      <div v-if="editing" class="mt-3">
        <button class="btn btn-primary mr-3" @click="save">
          Enregistrer
        </button>
        <button class="btn btn-danger" @click="cancel">Annuler</button>
      </div>
    </template>
  </div>
</template>

<script>
import EventBus from "../../../event-bus";
import RoleList from "./components/RoleList";

export default {
  props: {
    ou: Object,
  },

  components: { RoleList },

  data() {
    return {
      editing: false,

      // Edit mode
      selector: null,

      // View mode
      fields: [
        {
          key: "nom",
          label: "Nom",
        },
        {
          key: "prenom",
          label: "Prénom",
        },
        {
          key: "roles",
          label: "Structure d'appartenance & rôle(s)",
        },
      ],
      isBusy: false,
      totalRows: 1,
      currentPage: 1,
      perPage: 25,

      // Filtering
      filter: {
        q: "",
        montrerSousStructures: false,
      },
    };
  },

  watch: {
    $route: "refresh",
    ou: "refresh",
  },

  methods: {
    refresh() {
      this.$root.$emit("bv::refresh::table", "table-membres");
    },

    provider(ctx, callback) {
      if (!this.ou) {
        this.totalRows = 0;
        // const result = [];
        // callback(result);
      }

      const args = [this.ou.id];
      this.$root.rpc("get_membres", args).then(result => {
        this.totalRows = result.length;
        callback(result);
      });
    },

    myFilter(row, filter) {
      if (!filter.montrerSousStructures && !row.membre_direct) {
        return false;
      }
      if (filter.q) {
        const fn = s => s.toLowerCase().startsWith(filter.q.toLowerCase());
        return fn(row.prenom) || fn(row.nom);
      }
      return true;
    },

    onFiltered(filteredItems) {
      // Trigger pagination to update the number of buttons/pages due to filtering
      this.totalRows = filteredItems.length;
      this.currentPage = 1;
    },

    // Edit
    makeEditable() {
      if (!this.ou.editable) {
        return;
      }
      const args = [this.ou.id];
      this.$root.rpc("get_membres_rattaches_selector", args).then(result => {
        this.selector = result.selector;
        this.editing = true;
      });
    },

    cancel() {
      this.editing = false;
    },

    save() {
      const args = [this.ou.id, this.selector.value];
      const msg = "Rattachements mis à jour";
      this.$root.rpc("update_membres_rattaches", args, msg).then(() => {
        EventBus.$emit("refresh-structure");
      });
    },
  },
};
</script>
