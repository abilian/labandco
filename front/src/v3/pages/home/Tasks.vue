<template>
  <div>
    <breadcrumbs title="Mes tâches" />

    <box-demandes title="Mes tâches" id="tasks" scope="mes tâches" />
  </div>
</template>

<script>
import BoxDemandes from "../../components/grids/box-demandes";

export default {
  components: { BoxDemandes },
};
</script>
