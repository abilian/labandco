<template>
  <form class="form-horizontal" @change="model_updated" @submit="on_submit">
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
import FieldSet from "./FieldSet";
import update_form from "./update_form";

export default {
  props: {
    form: { type: Object, required: true },
    model: { type: Object, required: true },
    action: { type: String },
    calculette: { type: Boolean },
  },

  components: { FieldSet },

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

      const args = [this.model, this.form];
      const msg = "Demande créée";
      this.$root.rpc("create_demande", args).then(result => {
        const id = result;
        const msg = `Demande créée avec l'id: ${id}`;

        this.$root.$bvToast.toast(msg, {
          title: "OK",
          variant: "success",
          solid: true,
        });

        this.$router.push(`/demandes/${id}`);
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
