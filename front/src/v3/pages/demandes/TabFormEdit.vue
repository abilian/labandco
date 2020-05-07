<template>
  <div>
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
          Sauver la demande
        </button>
        &nbsp;
        <button
          id="cancel"
          type="submit"
          class="btn btn-danger"
          @click="onCancel"
        >
          Annuler
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import FieldSet from "../../components/forms/FieldSet";
import update_form from "../../components/forms/update_form";
import EventBus from "../../../event-bus";

export default {
  props: { demande: Object, form: Object },

  components: { FieldSet },

  data: function() {
    return {
      salaires_indicatifs: {},
    };
  },

  computed: {
    model() {
      if (this.demande) {
        return this.demande.form_data;
      } else {
        return {};
      }
    },
  },

  created() {
    this.modelUpdated();
    EventBus.$on("model-changed", this.modelUpdated);
  },

  methods: {
    modelUpdated(e) {
      update_form(this.form, this.model, this.salaires_indicatifs);
    },

    onCancel: function(e) {
      e.preventDefault();
      this.$parent.$parent.$parent.goToTab(0);
    },

    onSubmit(e) {
      e.preventDefault();

      const args = [this.demande.id, this.model, this.form];
      this.$root.rpc("update_demande", args).then(result => {
        for (let msg of result) {
          this.$root.$bvToast.toast(msg[0], {
            title: "",
            variant: msg[1],
            solid: true,
          });
        }

        this.$parent.$parent.$parent.refresh();
        this.$parent.$parent.$parent.goToTab(0);
      });

      // let url = "/demandes/post";
      // if (this.calculette) {
      //   url = "/calculettes/devis_rh";
      // }
      // const data = {
      //   action: this.form.mode,
      //   model: this.model,
      //   form: this.form,
      // };
      // axios
      //   .post(url, data)
      //   .then(result => {
      //     if (result.data.length > 100) {
      //       window.location = "/";
      //     } else {
      //       window.location = result.data;
      //     }
      //   })
      //   .catch(error => {
      //     console.error("error submitting the devis: ", error);
      //   });
    },
  },
};
</script>
