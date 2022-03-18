<template>
  <form class="form-horizontal" @change="modelUpdated" @submit="onSubmit">
    <div v-for="field_set in form.fieldsets">
      <field-set :field-set="field_set" :form="form" :model="model" />
    </div>

    <div v-if="!calculette" style="text-align: center">
      <button
        v-if="form.mode === 'create'"
        id="creer-demande"
        type="submit"
        class="btn btn-primary"
        @click="onCreate"
      >
        Créer la demande
      </button>

      <button
        v-if="form.mode === 'edit'"
        id="sauver-demande"
        type="submit"
        class="btn btn-primary"
        @click="onSave"
      >
        Sauver la demande
      </button>

      <button
        id="cancel"
        type="submit"
        class="btn btn-danger"
        @click="onCancel"
      >
        Annuler
      </button>
    </div>

    <div v-else style="text-align: center">
      <button id="calculer" type="submit" class="btn btn-primary">
        Lancer le calcul
      </button>
    </div>
  </form>
</template>

<script>
import FieldSet from "./FieldSet";
import update_form from "./update_form";
import EventBus from "../../../event-bus";

export default {
  props: {
    form: { type: Object, required: true },
    model: { type: Object, required: true },
    calculette: { type: Boolean },
  },

  components: { FieldSet },

  data: function () {
    return {
      salaires_indicatifs: {},
    };
  },

  created() {
    update_form(this.form, this.model, this.salaires_indicatifs);
    EventBus.$on("model-changed", this.modelUpdated);
  },

  methods: {
    modelUpdated(e) {
      update_form(this.form, this.model, this.salaires_indicatifs);
    },

    onSubmit(e) {
      e.preventDefault();
    },

    onCancel(e) {
      this.$router.push("/");
      this.$root.$bvToast.toast("Action annulée", {
        title: "OK",
        variant: "success",
        solid: true,
      });
    },

    onSave(e) {
      const args = [this.model.id, this.model, this.form];
      this.$root.rpc("update_demande", args).then((result) => {
        const id = result.id;
        const messages = result.messages;

        for (let msg of messages) {
          this.$root.$bvToast.toast(msg[0], {
            title: "",
            variant: msg[1],
            solid: true,
          });
        }

        this.$router.push(`/demandes/${id}`);
      });
    },

    onCreate(e) {
      const args = [this.model, this.form];
      this.$root.rpc("create_demande", args).then((result) => {
        const id = result.id;
        const messages = result.messages;

        for (let msg of messages) {
          this.$root.$bvToast.toast(msg[0], {
            title: "",
            variant: msg[1],
            solid: true,
          });
        }

        this.$router.push(`/demandes/${id}`);
      });
    },
  },
};
</script>
