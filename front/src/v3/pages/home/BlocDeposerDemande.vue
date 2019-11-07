<template>
  <div>
    <div class="box mt-4 mb-3">
      <div class="box-header with-border">
        <h3 class="box-title">Déposer une nouvelle demande</h3>
      </div>

      <div v-if="ready" class="box-body">
        <div class="row">
          <div v-for="button in buttons" class="col-md-6 col-lg-4">
            <router-link
              :to="{ name: 'nouvelle_demande', params: { type: button.type } }"
            >
              <div class="info-box">
                <span class="info-box-icon" :class="'bg-' + button.color"
                  ><i class="far fa-briefcase" :class="'fa-' + button.icon"></i
                ></span>

                <div class="info-box-content">
                  <span class="info-box-text" v-html="button.text"></span>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </div>
      <div v-else>Chargement en cours...</div>
    </div>
  </div>
</template>

<script>
import fp from "lodash/fp";

const BUTTONS = [
  {
    type: "convention",
    icon: "briefcase",
    text: "Convention de recherche",
    color: "pink",
  },
  {
    type: "avenant_convention",
    icon: "briefcase",
    text: "Convention de recherche<br />Avenant",
    color: "pink",
  },
  { type: "rh", icon: "user", text: "Recrutement / RH", color: "red" },
  {
    type: "pi_invention",
    icon: "rocket",
    text: "PI &amp; Transfert<br />Invention",
    color: "green",
  },
  {
    type: "pi_logiciel",
    icon: "save",
    text: "PI &amp; Transfert<br />Logiciel",
    color: "green",
  },
  { type: "autre", icon: "briefcase", text: "Autre", color: "blue" },
  {
    type: "faq",
    icon: "question-circle",
    text: "Questions &amp; suggestions",
    color: "yellow",
  },
];

export default {
  name: "BlocDeposerDemande",

  data() {
    return {
      ready: false,
      buttons: [],
    };
  },

  created() {
    this.fetchData();
  },

  methods: {
    fetchData() {
      this.$root.rpc("get_home_data", [], result => {
        const demande_types = result.demande_types;
        this.buttons = fp.filter(b => demande_types.includes(b.type))(BUTTONS);
        this.ready = true;
      });
    },
  },
};
</script>
