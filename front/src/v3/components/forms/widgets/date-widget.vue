<template>
  <input
    v-model="model[field.name]"
    type="date"
    class="form-control"
    placeholder="JJ/MM/AAAA"
    :readonly="!field.editable"
    :name="field.name"
  />
</template>

<script>
export default {
  name: "DateWidget",
  props: ["field", "model"],
};
</script>
