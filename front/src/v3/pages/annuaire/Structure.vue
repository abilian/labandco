<template>
  <div>
    <breadcrumbs :path="path" :title="title"></breadcrumbs>

    <b-card>
      <b-card-title class="p-0 m-0 mb-4">
        <h2 v-if="ou">{{ title }}</h2>
        <h2 v-else>Chargement en cours...</h2>
      </b-card-title>

      <b-card-text>
        <b-tabs>
          <b-tab title="Informations clefs" class="pt-4 pb-3">
            <h3>Informations clefs</h3>

            <structure-infos-clefs :ou="ou"></structure-infos-clefs>

            <div v-if="ou && ou.can_be_deleted" class="mt-5">
              <button class="btn btn-danger" @click="remove">
                <i class="far fa-trash"></i> Supprimer la structure
              </button>
            </div>
          </b-tab>

          <b-tab title="Hiérarchie" class="pt-4 pb-3">
            <h3>Hiérarchie</h3>

            <structure-hierarchie :ou="ou"></structure-hierarchie>
          </b-tab>

          <b-tab title="Membres" class="pt-4 pb-3">
            <h3>Membres</h3>

            <structure-membres :ou="ou"></structure-membres>
          </b-tab>

          <b-tab title="Rôles" class="pt-4 pb-3">
            <h3>Rôles au sein de la structure</h3>

            <structure-roles :ou="ou"></structure-roles>
          </b-tab>

          <b-tab title="Contacts Lab&amp;Co" class="pt-4 pb-3">
            <h3>Contacts Lab&amp;Co</h3>

            <structure-contacts :ou="ou"></structure-contacts>
          </b-tab>

          <b-tab v-if="debug" title="Debug" class="pt-4 pb-3">
            <h3>Debug</h3>

            <pre>{{ ou }}</pre>
          </b-tab>
        </b-tabs>
      </b-card-text>
    </b-card>
  </div>
</template>

<script>
import _ from "lodash";

import StructureInfosClefs from "./StructureInfosClefs";
import StructureRoles from "./StructureRoles";
import StructureHierarchie from "./StructureHierarchie";
import StructureContacts from "./StructureContacts";
import StructureMembres from "./StructureMembres";

import EventBus from "../../../event-bus";

export default {
  props: { id: String },

  components: {
    StructureInfosClefs,
    StructureContacts,
    StructureRoles,
    StructureHierarchie,
    StructureMembres,
  },

  data() {
    return {
      ou: null,
      title: "",
      path: [["Structures", "/annuaire/structures"]],
      num_membres: 0,
    };
  },

  computed: {
    debug() {
      // eslint-disable-next-line
      return DEBUG;
    },
  },

  watch: {
    $route: "fetchData",
  },

  created() {
    this.fetchData();
  },

  mounted() {
    EventBus.$on("refresh-structure", this.fetchData);
  },

  methods: {
    fetchData() {
      // FIXME: load data before routing instead
      this.ou = null;

      const args = [this.id];
      this.$root.rpc("sg_get_structure", args, result => {
        this.ou = {};
        _.assign(this.ou, result);
        const ou = this.ou;

        if (ou.sigle) {
          this.title = `${ou.type_name} : ${ou.nom} (${ou.sigle})`;
        } else {
          this.title = `${ou.type_name} : ${ou.nom}`;
        }

        const path = ou.ancestors.map(x => [
          x.type + " : " + x.name,
          "/annuaire/structures/" + x.id,
        ]);
        path.push(["Structures", "/annuaire/structures/"]);
        path.reverse();
        this.path = path;
      });
    },

    remove() {
      const message = `Voulez-vous vraiment supprimer la structure "${this.ou.nom}"?`;
      if (confirm(message)) {
        const args = [this.ou.id];
        const msg = `La structure "${this.ou.nom}" a bien été supprimée.`;
        this.$root.rpc(
          "sg_delete_structure",
          args,
          result => {
            this.$router.push("/annuaire/structures");
          },
          msg
        );
      }
    },
  },
};
</script>
