<template>
  <fieldset v-if="fieldSet.visible && !fieldSet.hidden">
    <legend>{{ fieldSet.label }}</legend>

    <template v-for="field_name in fieldSet.fields">
      <form-group
        v-if="
          form.fields[field_name].visible && !form.fields[field_name].hidden
        "
        :field-name="field_name"
        :model="model"
        :form="form"
        :key="'fg-' + field_name"
      />

      <span class="clearfix" />
    </template>
  </fieldset>
</template>

<script>
import FormGroup from "./FormGroup.vue";

export default {
  components: { FormGroup },
  props: {
    form: { type: Object, required: true },
    fieldSet: { type: Object, required: true },
    model: { type: Object, required: true },
  },
};
</script>
