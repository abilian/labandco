<template>
  <div>
    <breadcrumbs :path="path" :title="title" />

    <bloc-infos-clefs :demande="demande" />

    <!-- temp: this should appear even if demande is not defined -->
    <bloc-workflow v-if="demande" :demande="demande" />

    <b-card v-if="demande">
      <b-tabs>
        <b-tab title="Détails de la demande">
          <demande-form-view
            :demande="demande"
            :form="form"
          ></demande-form-view>
        </b-tab>

        <b-tab title="Formulaire"></b-tab>

        <b-tab title="Feuille de coût">
          <a class="btn btn-primary" href="/demandes/2643/feuille_cout"
            >Consulter la feuille de coût</a
          >
        </b-tab>

        <b-tab v-if="!acces_restreint" title="Pièces à joindre">
          <tab-pieces-jointes :demande="demande" />
        </b-tab>

        <b-tab v-if="!acces_restreing" title="Documents générés">
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
import DemandeFormView from "./DemandeFormView";
import BlocInfosClefs from "./BlocInfosClefs";
import BlocWorkflow from "./BlocWorkflow";
import TabPiecesJointes from "./TabPiecesJointes";
import TabHistorique from "./TabHistorique";

export default {
  props: { id: String },

  components: {
    BlocInfosClefs,
    BlocWorkflow,
    DemandeFormView,
    TabPiecesJointes,
    TabHistorique,
  },

  data() {
    return {
      ready: false,
      path: [["Demandes", "/demandes"]],
      title: "",
      form: {},
      demande: null,
    };
  },

  created() {
    const args = [this.id];
    this.$root.rpc("get_demande", args).then(result => {
      _.assign(this, result);
      this.ready = true;
    });
  },
};
</script>
