<template>
  <form
    class="form-horizontal"
    method="POST"
    action=""
    @change="model_updated"
    @submit="on_submit"
  >
    <div v-for="field_set in form.fieldsets">
      <field-set :field-set="field_set" :form="form" :model="model" />
    </div>

    <div v-if="!calculette" style="text-align: center;">
      <button
        v-if="form.mode === 'create'"
        id="creer-demande"
        type="submit"
        class="btn btn-primary"
      >
        Créer la demande
      </button>
      <button
        v-if="form.mode === 'edit'"
        id="sauver-demande"
        type="submit"
        class="btn btn-primary"
      >
        Sauver la demande
      </button>
      <button
        id="cancel"
        type="submit"
        class="btn btn-danger"
        @submit="on_cancel"
      >
        Annuler
      </button>
    </div>

    <div v-if="calculette" style="text-align: center;">
      <button id="calculer" type="submit" class="btn btn-primary">
        Lancer le calcul
      </button>
    </div>
  </form>
</template>

<script>
import axios from "axios";
// Renamed to FieldSet2 because the vuejs compiler complains otherwise:
// "Do not use built-in or reserved HTML elements as component id: FieldSet".
import FieldSet from "./field-set.vue";
import update_form from "../visibility";

export default {
  name: "MyForm",

  components: { FieldSet },
  props: {
    form: { type: Object, required: true },
    model: { type: Object, required: true },
    action: { type: String },
    calculette: { type: Boolean },
  },

  data: function() {
    return {
      salaires_indicatifs: {},
    };
  },

  methods: {
    model_updated: function(e) {
      update_form(this.form, this.model, this.salaires_indicatifs);
    },

    on_cancel: function(e) {
      e.preventDefault();
      const url = "/demandes/post";
      const data = {
        action: "cancel",
        model: this.model,
        form: this.form,
      };
      axios
        .post(url, data)
        .then(result => {
          if (result.data.length > 100) {
            window.location = "/";
          } else {
            window.location = result.data;
          }
        })
        .catch(error => {
          console.error("error saving the form: ", error);
        });
    },

    on_submit: function(e) {
      e.preventDefault();
      let url = "/demandes/post";
      if (this.calculette) {
        url = "/calculettes/devis_rh";
      }
      const data = {
        action: this.form.mode,
        model: this.model,
        form: this.form,
      };
      axios
        .post(url, data)
        .then(result => {
          if (result.data.length > 100) {
            window.location = "/";
          } else {
            window.location = result.data;
          }
        })
        .catch(error => {
          console.error("error submitting the devis: ", error);
        });
    },
  },
};
</script>
