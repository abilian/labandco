<template>
  <div id="boxes-demandes">
    <message-dgrtt></message-dgrtt>

    <bloc-deposer-demande></bloc-deposer-demande>

    <div>
      <template v-for="(box, index) in boxes">
        <box-demandes
          id="archives"
          :title="box.title"
          :scope="box.scope"
          :archives="box.archives"
          :key="index"
        >
        </box-demandes>
      </template>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import MessageDgrtt from "../../components/visual/MessageDgrtt";
import BoxDemandes from "../../components/grids/box-demandes";
import BlocDeposerDemande from "./BlocDeposerDemande";

export default {
  components: { MessageDgrtt, BoxDemandes, BlocDeposerDemande },

  computed: {
    boxes() {
      return Vue.$storage.get("user_context").home_boxes;
    },
  },
};
</script>
