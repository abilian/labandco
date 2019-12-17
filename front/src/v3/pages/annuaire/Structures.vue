<template>
  <div>
    <breadcrumbs title="Structures" />

    <table-structures url="/v3/api/structures" />
  </div>
</template>

<script>
import TableStructures from "./components/TableStructures";

export default {
  components: { TableStructures },
};
</script>
