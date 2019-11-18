<template>
  <input
    v-model="model[field.name]"
    type="text"
    :name="field.name"
    :readonly="!field.editable"
    class="form-control"
  />
</template>

<script>
export default {
  name: "StringWidget",
  props: ["field", "model"],
};
</script>
