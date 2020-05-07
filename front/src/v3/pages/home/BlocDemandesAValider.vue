<template>
  <div class="box box-warning mb-4">
    <div class="box-header with-border">
      <h3 class="box-title">Demandes à valider ({{ total_demandes }})</h3>
    </div>

    <div class="box-body">
      <div class="row">
        <box-demandes-a-valider
          name="Convention"
          color="bg-pink"
          tag="conventions"
          :nb="nb_conventions_a_valider"
        />
        <box-demandes-a-valider
          name="Recrutements"
          color="bg-red"
          tag="rh"
          :nb="nb_recrutements_a_valider"
        />
        <box-demandes-a-valider
          name="PI et transfert"
          color="bg-green"
          tag="pi"
          :nb="nb_pi_a_valider"
        />
        <box-demandes-a-valider
          name="Autres"
          color="bg-green"
          tag="autres"
          :nb="nb_autres_a_valider"
        />
      </div>
    </div>
  </div>
</template>

<script>
import _ from "lodash";

import BoxDemandesAValider from "./BoxDemandesAValider";

export default {
  data() {
    return {
      total_demandes: 0,
      nb_pi_a_valider: 0,
      nb_recrutements_a_valider: 0,
      nb_conventions_a_valider: 0,
      nb_autres_a_valider: 0,
    };
  },

  components: { BoxDemandesAValider },

  created() {
    this.$root.rpc("get_nb_demandes_a_valider", []).then(result => {
      _.assign(this, result);
    });
  },
};
</script>
