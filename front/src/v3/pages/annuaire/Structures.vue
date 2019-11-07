<template>
  <div>
    <breadcrumbs title="Structures"></breadcrumbs>

    <table-structures url="/v3/api/structures"></table-structures>
  </div>
</template>

<script>
import TableStructures from "./components/TableStructures";

export default {
  components: { TableStructures },
};
</script>
