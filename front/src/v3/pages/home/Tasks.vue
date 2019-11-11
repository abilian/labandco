<template>
  <div>
    <breadcrumbs title="Mes tâches"></breadcrumbs>

    <div id="boxes-demandes">
      <box-demandes title="Mes tâches" id="index" scope="mes tâches">
      </box-demandes>
    </div>
  </div>
</template>

<script>
import BoxDemandes from "../../components/grids/box-demandes";

export default {
  name: "Tasks",

  components: { BoxDemandes },
};
</script>
