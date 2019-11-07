<template>
  <input
    v-model="model[field.name]"
    :name="field.name"
    :readonly="!field.editable"
    class="form-control"
  />
</template>

<script>
export default {
  name: "IntegerWidget",
  props: ["field", "model"],
};
</script>
