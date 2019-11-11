<template>
  <div>
    <breadcrumbs title="Questions & Suggestions"></breadcrumbs>

    <div class="card faq-index">
      <div class="card-header">
        <h2 class="card-title">Questions &amp; suggestions</h2>
      </div>

      <div class="card-body">
        <template v-if="ready">
          <div v-for="category in category_names" class="mb-5">
            <h3 class="mt-3 mb-3">{{ category }}</h3>

            <div v-for="entry in entriesForCategory(category)">
              <h4 class="mt-3" v-b-toggle="'accordion-' + entry.id">
                <b-button variant="default">
                  <span class="when-closed"><i class="far fa-eye"></i></span>
                  <span class="when-opened"
                    ><i class="far fa-eye-slash"></i
                  ></span>
                </b-button>

                {{ entry.title }}
              </h4>

              <b-collapse
                :id="'accordion-' + entry.id"
                accordion="my-accordion"
                role="tabpanel"
              >
                <div v-html="entry.body" class="faq-body"></div>
              </b-collapse>
            </div>
          </div>

          <hr />

          <h3>Vous n'avez pas trouvé la réponse à votre question ?</h3>

          <p>
            <router-link to="/faq/message" class="btn btn-primary">
              <i class="far fa-question"></i> Poser votre question ou faire
              votre suggestion à la DR&I.
            </router-link>
          </p>
        </template>
        <p v-else>
          Chargement en cours...
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import fp from "lodash/fp";
import { ContextFetcher } from "../../mixins";

export default {
  mixins: [ContextFetcher],

  data() {
    return {
      categories: [],
      category_names: [],
      entries: [],
    };
  },

  methods: {
    whenReady() {
      this.categories = fp.groupBy("category", this.entries);
      this.category_names = fp.keys(this.categories);
    },

    entriesForCategory(category) {
      return this.categories[category];
    },
  },
};
</script>

<style scoped>
i.far {
  width: 18px;
}

.collapsed > .when-opened,
:not(.collapsed) > .when-closed {
  display: none;
}

/*.faq-index h2 {*/
/*  font-size: 26px;*/
/*  font-weight: 600;*/
/*  margin-top: 0;*/
/*}*/

.faq-index h3 {
  font-size: 22px;
  font-weight: 600;
}

.faq-index h4 {
  font-size: 20px;
  font-style: italic;
}

.faq-body {
  margin-left: 1.3em;
  border-left: solid 1px #1e282c;
  padding-left: 1em;
}
</style>
