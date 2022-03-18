<template>
  <div class="card faq-index">
    <div class="card-header">
      <h2 class="card-title">FAQ: {{ entry.title }}</h2>
    </div>

    <div class="card-body">
      <b-form @submit="onSubmit" @reset="onReset">
        <b-form-group id="input-group-1" label="Question:" label-for="input-1">
          <b-form-input
            id="input-1"
            v-model="entry.title"
            type="text"
            required
          ></b-form-input>
        </b-form-group>

        <b-form-group id="input-group-3" label="Catégorie:" label-for="input-3">
          <b-form-select
            id="input-3"
            v-model="entry.category"
            :options="categories"
            required
          ></b-form-select>
        </b-form-group>

        <b-form-group id="input-group-4" label="Réponse:" label-for="input-4">
          <quill-editor v-model="entry.body" />
        </b-form-group>

        <b-button type="submit" variant="primary">Submit</b-button>
        <b-button type="reset" variant="default">Reset</b-button>
        <b-button variant="danger" @click="onDelete">Delete</b-button>
      </b-form>
    </div>
  </div>
</template>

<script>
import EventBus from "../../../event-bus";

export default {
  props: {
    entry: Object,
    categories: Array,
  },

  methods: {
    onSubmit() {
      const args = [this.entry];
      const msg = "Question mise à jour";
      this.$root.rpc("update_faq_entry", args, msg).then((result) => {
        EventBus.$emit("faq-list");
      });
    },

    onReset() {
      EventBus.$emit("faq-list");
    },

    onDelete() {
      const args = [this.entry];
      const msg = "Question supprimée";
      this.$root.rpc("delete_faq_entry", args, msg).then((result) => {
        EventBus.$emit("faq-list");
      });
    },
  },
};
</script>
