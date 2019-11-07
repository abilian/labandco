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
import BoxDemandes from "../../components/grids/box-demandes";

export default {
  components: { BoxDemandes },

  data() {
    return {
      boxes: [],
    };
  },

  created() {
    this.$root.rpc("get_boxes", { archives: true }, result => {
      this.boxes = result;
    });
  },
};
</script>
