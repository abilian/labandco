<template>
  <div class="card faq-index">
    <div class="card-header">
      <h2 class="card-title">Questions &amp; suggestions</h2>
    </div>

    <div class="card-body">
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <td width="5%">Id</td>
            <td width="55%">Titre</td>
            <td width="25%">Categorie</td>
            <td width="15%">Action</td>
          </tr>
        </thead>

        <tbody>
          <tr v-for="entry in entries">
            <td>{{ entry.id }}</td>
            <td>{{ entry.title }}</td>
            <td>{{ entry.category }}</td>
            <td>
              <b-button @click="editEntry(entry)" size="sm" variant="primary"
                >Edit</b-button
              >
            </td>
          </tr>
        </tbody>
      </table>

      <p style="margin-top: 1em; margin-left: 8px">
        <b-button @click="newEntry()" size="sm" variant="primary">
          <i class="far fa-plus" />
          Edit</b-button
        >
      </p>
    </div>
  </div>
</template>

<script>
import EventBus from "../../../event-bus";

export default {
  props: { entries: Array },

  methods: {
    editEntry(entry) {
      EventBus.$emit("faq-entry-edit", entry);
    },

    newEntry() {
      EventBus.$emit("faq-entry-new");
    },
  },
};
</script>
