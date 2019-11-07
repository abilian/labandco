<template>
  <div id="boxes-demandes">
    <message-dgrtt></message-dgrtt>

    <bloc-deposer-demande></bloc-deposer-demande>

    <div>
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
import MessageDgrtt from "../../components/visual/MessageDgrtt";
import BoxDemandes from "../../components/grids/box-demandes";
import BlocDeposerDemande from "./BlocDeposerDemande";

export default {
  components: { MessageDgrtt, BoxDemandes, BlocDeposerDemande },

  data() {
    return {
      boxes: [],
    };
  },

  created() {
    this.$root.rpc("get_boxes", [], result => {
      this.boxes = result;
      console.log(this.boxes);
    });
  },
};
</script>
