<template>
  <textarea
    v-model="model[field.name]"
    :name="field.name"
    :readonly="!field.editable"
    rows="5"
    class="form-control "
  />
</template>

<script>
export default {
  name: "TextAreaWidget",
  props: ["field", "model"],
};
</script>
