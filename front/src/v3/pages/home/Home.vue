<template>
  <div class="pt-3">
    <message-dgrtt />

    <bloc-deposer-demande />

    <bloc-demandes-a-valider
      v-if="user.is_responsable && !(user.is_membre_dri || user.is_membre_drv)"
    />

    <box-demandes
      v-for="(box, index) in boxes"
      :id="'home-' + index"
      :title="box.title"
      :scope="box.scope"
      :archives="box.archives"
      :key="index"
    />

    <bloc-demandes-a-valider
      v-if="user.is_responsable && (user.is_membre_dri || user.is_membre_drv)"
    />
  </div>
</template>

<script>
import Vue from "vue";
import MessageDgrtt from "../../components/navigation/MessageDgrtt";
import BoxDemandes from "../../components/grids/box-demandes";
import BlocDeposerDemande from "./BlocDeposerDemande";
import BlocDemandesAValider from "./BlocDemandesAValider";

export default {
  components: {
    MessageDgrtt,
    BoxDemandes,
    BlocDeposerDemande,
    BlocDemandesAValider,
  },

  computed: {
    user() {
      return Vue.$storage.get("user_context") || {};
    },
    boxes() {
      return Vue.$storage.get("user_context").home_boxes;
    },
  },
};
</script>
