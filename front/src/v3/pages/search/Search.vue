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
                <i :class="demande.icon_class" />&nbsp;
                <router-link
                  :to="{ name: 'demande', params: { id: demande.id } }"
                  >{{ demande.nom }}</router-link
                >
              </div>

              <div class="metadata">
                <span v-if="demande.porteur">
                  <i>Porteur:</i>&nbsp;
                  <router-link
                    :to="{ name: 'user', params: { id: demande.porteur.id } }"
                    >{{ demande.porteur.full_name }}</router-link
                  >.
                </span>

                <span v-if="demande.gestionnaire">
                  <i>Gestionnaire:</i>&nbsp;
                  <router-link
                    :to="{
                      name: 'user',
                      params: { id: demande.gestionnaire.id },
                    }"
                    >{{ demande.gestionnaire.full_name }}</router-link
                  >.
                </span>

                <span v-if="demande.structure">
                  <i>Structure:</i>&nbsp;
                  <router-link
                    :to="{
                      name: 'structure',
                      params: { id: demande.structure.id },
                    }"
                    >{{ demande.structure.nom }}</router-link
                  >.
                </span>

                <span v-if="demande.wf_state">
                  <i>Etat:</i>&nbsp; {{ demande.wf_state }}.
                </span>

                <i>Créée le:</i>
                {{ demande.created_at | moment("DD MMMM YYYY") }}.
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
export default {
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
      const args = { q: this.q, page: 1 };
      this.$root.rpc("search_api", args).then((result) => {
        this.faqs = result.faqs;
        this.demandes = result.demandes;
      });
    },
  },
};
</script>
