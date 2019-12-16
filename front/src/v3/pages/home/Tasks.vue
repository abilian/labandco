<template>
  <div>
    <breadcrumbs title="Mes tâches"></breadcrumbs>

    <box-demandes title="Mes tâches" id="tasks" scope="mes tâches" />
  </div>
</template>

<script>
import BoxDemandes from "../../components/grids/box-demandes";

export default {
  name: "Tasks",

  components: { BoxDemandes },
};
</script>
