<template>
  <select
    v-model="model[field.name]"
    :name="field.name"
    :readonly="!field.editable"
    class="form-control"
  >
    <template v-for="item in field.choices">
      <option :selected="model[field.name] === item[0]" :value="item[0]">
        {{ item[1] }}
      </option>
    </template>
  </select>
</template>

<script>
export default {
  name: "SelectWidget",
  props: ["field", "model"],
};
</script>
