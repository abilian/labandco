<template>
  <div>
    <breadcrumbs title="Mes demandes"></breadcrumbs>

    <div id="boxes-demandes">
      <box-demandes title="Mes demandes" id="index" url="/v3/api/mes_demandes">
      </box-demandes>
    </div>
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
