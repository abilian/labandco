<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title">Résultat de la recherche "{{ q }}"</h3>
    </div>

    <div class="card-body">
      <div class="search-results">
        <template v-if="demandes.length || faqs.length">
          <template v-if="faqs.length">
            <h3>FAQ ({{ faqs.length }})</h3>

            <div v-for="faq in faqs" class="search-result">
              <div class="search-title">
                <router-link :to="{ name: 'faq', params: { id: faq.id } }">{{
                  faq.title
                }}</router-link>
                {{ faq.title }}
              </div>
            </div>
          </template>

          <template v-if="demandes.length">
            <h3>Demandes ({{ demandes.length }})</h3>

            <div v-for="demande in demandes" class="search-result">
              <div class="search-title">
                <router-link
                  :to="{ name: 'demande', params: { id: demande.id } }"
                  >{{ demande.nom }}</router-link
                >
                [{{ demande.type }}]
              </div>

              <div class="metadata">
                <span v-if="demande.porteur">
                  <i>Porteur:</i> {{ demande.porteur.full_name }}.
                </span>

                <span v-if="demande.gestionnaire">
                  {{ demande.gestionnaire.full_name }}.
                </span>

                <span v-if="demande.laboratoire">
                  <i>Laboratoire:</i>
                  {{ demande.laboratoire.nom }}.
                </span>

                <i>Créée le:</i>
                <!--                {{ demande.created_at | dateformat("medium") }}.-->
                {{ demande.created_at }}.
              </div>
            </div>
          </template>
        </template>

        <template v-else>
          <p>Pas de résultats.</p>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

const URL = "/v3/api/search";

export default {
  name: "Search",

  props: {
    q: String,
  },

  data() {
    return {
      faqs: [],
      demandes: [],
    };
  },

  watch: {
    q() {
      this.update();
    },
  },

  created() {
    this.update();
  },

  methods: {
    update() {
      axios.get(URL, { params: { q: this.q } }).then(response => {
        const data = response.data;
        this.faqs = data.faqs;
        this.demandes = data.demandes;
      });
    },
  },
};
</script>
