<template>
  <div>
    <breadcrumbs :path="path" :title="title"></breadcrumbs>

    <infos-clefs :demande="demande"></infos-clefs>

    <demande-actions />

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

        <b-tab title="Pièces à joindre">
          <h3>Pièces-jointes</h3>

          <pieces-jointes :demande="demande"></pieces-jointes>

          <h3>Ajouter une ou des pièce-jointes</h3>

          <form
            method="POST"
            enctype="multipart/form-data"
            action="/demandes/2643/pj"
          >
            <input type="file" name="file" multiple="" />

            <br />

            <input type="submit" class="btn btn-primary" name="Envoyer" />
          </form>
        </b-tab>

        <b-tab title="Documents générés"></b-tab>

        <b-tab title="Historique">
          <tab-historique />
        </b-tab>
      </b-tabs>
    </b-card>
  </div>
</template>

<script>
import _ from "lodash";
import InfosClefs from "./InfosClefs";
import DemandeActions from "./DemandeActions";
import DemandeFormView from "./DemandeFormView";
import PiecesJointes from "./PiecesJointes";
import TabHistorique from "./TabHistorique";

export default {
  props: { id: String },

  components: {
    TabHistorique,
    DemandeActions,
    InfosClefs,
    PiecesJointes,
    DemandeFormView,
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
    this.$root.rpc("get_demande", args, result => {
      _.assign(this, result);
      this.ready = true;
    });
  },
};
</script>
