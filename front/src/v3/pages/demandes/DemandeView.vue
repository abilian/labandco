<template>
  <div>
    <breadcrumbs :path="path" :title="title" />

    <bloc-infos-clefs :demande="demande" />

    <!-- temp: this should appear even if demande is not defined -->
    <bloc-workflow v-if="demande" :demande="demande" />

    <b-card v-if="demande">
      <b-tabs v-model="tabIndex">
        <b-tab title="Détails de la demande">
          <tab-form-view :demande="demande" :form="form" />
        </b-tab>

        <b-tab v-if="demande.is_editable" title="Formulaire">
          <tab-form-edit :demande="demande" :form="form" />
        </b-tab>

        <b-tab
          v-if="demande.type === 'Convention de recherche'"
          title="Feuille de coût"
        >
          <a
            v-if="demande.feuille_cout_editable"
            class="btn btn-primary mt-4"
            :href="`/feuille_cout/${demande.id}`"
            >Editer la feuille de coût</a
          >
          <a
            v-else
            class="btn btn-primary mt-4"
            :href="`/feuille_cout/${demande.id}`"
            >Consulter la feuille de coût</a
          >
        </b-tab>

        <b-tab v-if="!demande.acces_restreint" title="Pièces à joindre">
          <tab-pieces-jointes :demande="demande" />
        </b-tab>

        <b-tab v-if="!demande.acces_restreint" title="Documents générés">
          <tab-documents-generes :demande="demande" />
        </b-tab>

        <b-tab title="Historique">
          <tab-historique :demande="demande" />
        </b-tab>
      </b-tabs>
    </b-card>
  </div>
</template>

<script>
import _ from "lodash";

import BlocInfosClefs from "./BlocInfosClefs";
import BlocWorkflow from "./BlocWorkflow";

import TabFormView from "./TabFormView";
import TabFormEdit from "./TabFormEdit";
import TabPiecesJointes from "./TabPiecesJointes";
import TabHistorique from "./TabHistorique";
import TabDocumentsGeneres from "./TabDocumentsGeneres";

export default {
  props: { id: String },

  components: {
    BlocInfosClefs,
    BlocWorkflow,
    //
    TabFormView,
    TabFormEdit,
    TabPiecesJointes,
    TabHistorique,
    TabDocumentsGeneres,
  },

  data() {
    return {
      ready: false,
      tabIndex: 0,
      path: [["Demandes", "/demandes"]],
      title: "",
      demande: null,
      form: {},
    };
  },

  created() {
    const args = [this.id];
    this.$root.rpc("get_demande", args).then(result => {
      _.assign(this, result);
      this.ready = true;
      this.title = this.demande.name;
    });
  },

  methods: {
    goToTab(n) {
      this.tabIndex = n;
    },
  },
};
</script>
