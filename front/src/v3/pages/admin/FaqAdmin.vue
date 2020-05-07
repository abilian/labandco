<template>
  <div>
    <breadcrumbs title="Questions & Suggestions" />

    <faq-admin-list v-if="!editing" :entries="entries" />
    <faq-admin-edit v-if="editing" :entry="entry" :categories="categories" />
  </div>
</template>

<script>
import { ContextFetcher } from "../../mixins";
import EventBus from "../../../event-bus";

import FaqAdminList from "./FaqAdminList";
import FaqAdminEdit from "./FaqAdminEdit";

export default {
  mixins: [ContextFetcher],

  data() {
    return {
      editing: false,
      entries: [],
      categories: [],
    };
  },

  components: {
    FaqAdminList,
    FaqAdminEdit,
  },

  created() {
    EventBus.$on("faq-entry-edit", this.editEntry);
    EventBus.$on("faq-entry-new", this.newEntry);
    EventBus.$on("faq-list", this.listEntries);
  },

  methods: {
    whenReady() {},

    editEntry(entry) {
      this.entry = entry;
      this.editing = true;
    },

    newEntry(entry) {
      this.entry = { title: "", category: "", body: "" };
      this.editing = true;
    },

    listEntries() {
      this.editing = false;
      this.fetchContext();
    },
  },
};
</script>
