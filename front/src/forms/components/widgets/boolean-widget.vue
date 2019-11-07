<template>
  <label class="checkbox-inline">
    <input
      :id="field.name"
      v-model="model[field.name]"
      :name="field.name"
      type="checkbox"
      value="y"
      :readonly="!field.editable"
    />&nbsp;
  </label>
</template>

<script>
export default {
  name: "BooleanWidget",
  props: ["field", "model"],
};
</script>
