<template>
  <div>
    <breadcrumbs title="Calculette RH" />

    <div class="card">
      <div class="card-header with-border">
        <h3 class="card-title">Calculette RH</h3>
      </div>

      <div class="card-body">
        <form class="form-horizontal" @change="modelUpdated">
          <div v-for="field_set in form.fieldsets">
            <field-set :field-set="field_set" :form="form" :model="model" />
          </div>

          <div class="text-center">
            <button
              id="sauver-demande"
              type="submit"
              class="btn btn-primary"
              @click="onSubmit"
            >
              Lancer le calcul
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import FieldSet from "../../components/forms/FieldSet";
import update_form from "../../components/forms/update_form";
import axios from "axios";
import FileSaver from "file-saver";
import EventBus from "../../../event-bus";

// var FileSaver = require('file-saver');

const URL = "/calculettes/devis_rh";

export default {
  components: { FieldSet },

  data: function() {
    return {
      form: {},
      model: {},
      salaires_indicatifs: {},
      ready: false,
    };
  },

  created() {
    this.$root.rpc("get_new").then(result => {
      this.form = result.form;
      this.model = result.model;
      this.ready = true;
      update_form(this.form, this.model, this.salaires_indicatifs);
      EventBus.$on("model-changed", this.modelUpdated);
    });
  },

  methods: {
    modelUpdated(e) {
      update_form(this.form, this.model, this.salaires_indicatifs);
    },

    onSubmit(e) {
      e.preventDefault();

      const data = { form: this.form, model: this.model };
      const headers = {
        "Content-Type": "application/json",
        Accept: "application/pdf",
      };
      axios
        .post(URL, data, { responseType: "arraybuffer", headers })
        .then(response => {
          const blob = new Blob([response.data], { type: "application/pdf" });
          FileSaver.saveAs(blob, "devis-rh.pdf");
        });
    },
  },
};
</script>
