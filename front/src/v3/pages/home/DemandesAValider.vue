<template>
  <div>
    <breadcrumbs title="Mes tâches" />

    <box-demandes
      title="Demandes à valider"
      id="demandes_a_valider"
      scope="demandes à valider"
    />
  </div>
</template>

<script>
import BoxDemandes from "../../components/grids/box-demandes";

export default {
  components: { BoxDemandes },
};
</script>
