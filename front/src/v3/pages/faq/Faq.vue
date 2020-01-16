<template>
  <div>
    <breadcrumbs title="Questions & Suggestions" />

    <div class="card faq-index">
      <div class="card-header">
        <h2 class="card-title">Questions &amp; suggestions</h2>
      </div>

      <div v-if="ready" class="card-body">
        <div
          v-for="([category, entries], category_index) in categories"
          class="card faq-index"
        >
          <div class="card-header">
            <h3 v-b-toggle="'category-' + category_index" class="card-title">
              <i class="far fa-chevron-right" />
              &nbsp;
              {{ category }}
            </h3>
          </div>

          <div class="card-body">
            <b-collapse :id="'category-' + category_index">
              <div v-for="entry in entries">
                <h4 v-b-toggle="'entry-' + entry.id">
                  <i class="far fa-chevron-right" />
                  &nbsp;
                  {{ entry.title }}
                  <span v-if="isAdmin"> ({{ entry.view_count }} vues) </span>
                </h4>

                <b-collapse
                  :id="'entry-' + entry.id"
                  entry="my-entry"
                  role="tabpanel"
                  :accordion="'category-' + category_index"
                >
                  <div v-html="entry.body" class="faq-body"></div>
                </b-collapse>
              </div>
            </b-collapse>
          </div>
        </div>

        <div class="card faq-index">
          <div class="card-header">
            <h2 class="card-title">
              Vous n'avez pas trouvé la réponse à votre question ?
            </h2>
          </div>

          <div class="card-body">
            <p>
              <router-link to="/faq/message" class="btn btn-primary">
                <i class="far fa-question" /> Poser votre question ou faire
                votre suggestion à la DR&I.
              </router-link>
            </p>
          </div>
        </div>
      </div>

      <div v-else class="card-body">
        Chargement en cours...
      </div>
    </div>
  </div>
</template>

<script>
import { ContextFetcher } from "../../mixins";

export default {
  mixins: [ContextFetcher],

  data() {
    return {
      categories: [],
    };
  },

  computed: {
    isAdmin() {
      return this.$storage.get("user_context").is_admin;
    },
  },

  mounted() {
    this.$root.$on("bv::collapse::state", (collapseId, isJustShown) => {
      if (isJustShown) {
        if (collapseId.startsWith("entry-")) {
          const id = Number(collapseId.slice("entry-".length));
          this.$root.rpc("view_entry", { id });
        }
      }
    });
  },

  methods: {
    whenReady() {},
  },
};
</script>

<style scoped>
i.far {
  width: 18px;
}

.collapsed > .fa-chevron-right {
  transition: all linear 0.3s;
}

:not(.collapsed) > .fa-chevron-right {
  transform: rotate(90deg) translate(0.25em, 0.25em);
  transition: all linear 0.3s;
}

.faq-index h3 {
  cursor: pointer;
  font-weight: 600;
}

.faq-index h4 {
  margin-top: 0;
  font-size: 1.2rem;
  font-style: italic;
  cursor: pointer;
}

.faq-body {
  margin-left: 1.3em;
  border-left: solid 1px #1e282c;
  padding-left: 1em;
}
</style>
