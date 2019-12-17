<template>
  <div>
    <breadcrumbs title="Utilisateurs" />

    <table-users title="Utilisateurs Lab&Co" url="/v3/api/users" />
  </div>
</template>

<script>
import TableUsers from "./components/TableUsers";

export default {
  components: { TableUsers },
};
</script>
