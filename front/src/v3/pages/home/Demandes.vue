<template>
  <div>
    <breadcrumbs title="Mes demandes"></breadcrumbs>

    <box-demandes title="Mes demandes" id="demandes" scope="mes demandes" />
  </div>
</template>

<script>
import BoxDemandes from "../../components/grids/box-demandes";

export default {
  name: "Demandes",

  // TODO
  //   if user.has_role("porteur"):
  //       title = "Demandes dont je suis le porteur"
  //   else:
  //       title = "Mes demandes"

  components: { BoxDemandes },
};
</script>
