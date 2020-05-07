<template>
  <div>
    <breadcrumbs title="Mes demandes en retard" />

    <box-demandes
      title="Mes demandes en retard"
      id="mes_demandes"
      scope="mes demandes en retard"
    />
  </div>
</template>

<script>
import BoxDemandes from "../../components/grids/box-demandes";

export default {
  components: { BoxDemandes },
};
</script>
