<template>
  <div>
    <breadcrumbs title="Mes demandes en retard"></breadcrumbs>

    <div id="boxes-demandes">
      <box-demandes
        title="Mes demandes en retard"
        id="index"
        url="/v3/api/mes_demandes_en_retard"
      >
      </box-demandes>
    </div>
  </div>
</template>

<script>
import BoxDemandes from "../../components/grids/box-demandes";

export default {
  name: "DemandesEnRetard",

  components: { BoxDemandes },
};
</script>
