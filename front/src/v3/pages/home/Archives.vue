<template>
  <div>
    <breadcrumbs title="Demandes archivées"></breadcrumbs>

    <div id="boxes-demandes">
      <template v-for="(box, index) in boxes">
        <box-demandes
          id="archives"
          :title="box.title"
          :url="box.api_url"
          :key="index"
        >
        </box-demandes>
      </template>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import BoxDemandes from "../../components/grids/box-demandes";

export default {
  components: { BoxDemandes },

  computed: {
    boxes() {
      return Vue.$storage.get("user_context").archives_boxes;
    },
  },
};
</script>
