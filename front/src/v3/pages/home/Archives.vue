<template>
  <div>
    <breadcrumbs title="Demandes archivées"></breadcrumbs>

    <box-demandes
      v-for="(box, index) in boxes"
      :id="'archives-' + index"
      :title="box.title"
      :scope="box.scope"
      :archives="true"
      :key="index"
    />
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
