<template>
  <div>
    <breadcrumbs title="Nouvelle demande"></breadcrumbs>

    <div id="vue-newform" class="wrapper">
      <div class="card box-primary">
        <div class="card-header">
          <h3 class="card-title">{{ title }}</h3>
        </div>

        <div class="card-body">
          <template v-if="ready">
            <p>
              NB: Les champs suivis d'un astérisque (<span class="text-red"
                >*</span
              >) sont obligatoires. Vous pourrez néanmoins sauvegarder une
              demande incomplète et la compléter ultérieurement si vous le
              souhaitez.
            </p>

            <div v-if="form.name === 'convention'">
              <p>
                Vous pouvez (et, probablement, devez) joindre à ce formulaire
                des documents complémentaires : canevas d’appel à projets,
                annexe scientifique, annexe financière… en utilisant l’onglet
                <b>Pièces à joindre</b>.
              </p>

              <p>
                <b
                  >Pour un avenant à un contrat en cours, choisissez le
                  formulaire "Avenant"</b
                >.
              </p>
            </div>

            <div id="form-demande">
              <my-form :form="form" :model="model"></my-form>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ContextFetcher } from "../../mixins";

export default {
  props: { type: String },

  mixins: [ContextFetcher],

  data() {
    return {
      title: "Chargement du formulaire en cours...",
      form: {},
      model: {},
    };
  },

  methods: {
    whenReady() {
      this.title = `Nouvelle demande de type: ${this.form.label}`;
    },
  },
};
</script>
