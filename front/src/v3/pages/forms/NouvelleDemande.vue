<template>
  <div>
    <breadcrumbs title="Nouvelle demande" />

    <div class="wrapper">
      <div class="card box-primary">
        <div class="card-header">
          <h3 class="card-title">{{ title }}</h3>
        </div>

        <div class="card-body">
          <template v-if="ready">
            <template v-if="form.conditions && !conditions_acceptees">
              <div v-html="form.conditions" />

              <p>&nbsp;</p>

              <div class="text-center">
                <p>
                  <b
                    >J’ai pris connaissance des informations de cette page et
                    j'accepte les conditions ci-dessus:</b
                  >
                </p>

                <button
                  @click="conditions_acceptees = true"
                  class="btn btn-default"
                >
                  J'accepte
                </button>
              </div>
            </template>

            <template v-else>
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

              <formulaire-demande :form="form" :model="model" />
            </template>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ContextFetcher } from "../../mixins";
import FormulaireDemande from "../../components/forms/FormulaireDemande";

export default {
  props: { type: String },

  mixins: [ContextFetcher],

  components: { FormulaireDemande },

  data() {
    return {
      title: "Chargement du formulaire en cours...",
      form: {},
      model: {},
      conditions_acceptees: false,
    };
  },

  methods: {
    whenReady() {
      this.title = `Nouvelle demande de type: ${this.form.label}`;
    },
  },
};
</script>
