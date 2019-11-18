<template>
  <input
    v-model="model[field.name]"
    type="email"
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
