<template>
  <div>
    <breadcrumbs title="Mes demandes" />
    <box-demandes title="Mes demandes" id="demandes" scope="mes demandes" />
  </div>
</template>

<script>
import BoxDemandes from "../../components/grids/box-demandes";

export default {
  components: { BoxDemandes },
};
</script>
