<template>
  <div>
    <div class="box mt-4 mb-3">
      <div class="box-header with-border">
        <h3 class="box-title">Déposer une nouvelle demande</h3>
      </div>

      <div class="box-body">
        <div class="row">
          <div v-for="button in buttons" class="col-md-6 col-lg-4">
            <a :href="button.url">
              <div class="info-box">
                <span class="info-box-icon" :class="'bg-' + button.color"
                  ><i class="far fa-briefcase" :class="'fa-' + button.icon"></i
                ></span>

                <div class="info-box-content">
                  <span class="info-box-text" v-html="button.text"></span>
                </div>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
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
    url: "#/faq",
  },
];

export default {
  name: "BlocDeposerDemande",

  computed: {
    buttons() {
      const types_demandes = Vue.$storage.get("user_context").types_demandes;

      const makeUrl = button => {
        if (button.url) {
          return button.url;
        } else {
          const location = {
            name: "demande.new",
            params: { type: button.type },
          };
          return this.$router.resolve(location).href;
        }
      };
      return fp.pipe(
        fp.filter(b => types_demandes.includes(b.type)),
        fp.map(b => ({ url: makeUrl(b), ...b }))
      )(BUTTONS);
    },
  },
};
</script>
