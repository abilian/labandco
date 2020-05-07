<template>
  <div>
    <div class="form-check form-check-inline">
      <input
        :id="field.name + '-yes'"
        v-model="model[field.name]"
        type="radio"
        :name="field.name"
        value="oui"
        class="form-check-input"
      />

      <label class="form-check-label" :for="field.name">
        Oui
      </label>
    </div>

    <div class="form-check form-check-inline">
      <input
        :id="field.name + '-no'"
        v-model="model[field.name]"
        type="radio"
        :name="field.name"
        value="non"
        class="form-check-input"
      />

      <label class="form-check-label" :for="field.name">
        Non
      </label>
    </div>
  </div>
</template>

<script>
export default {
  name: "YesNoWidget",
  props: ["field", "model"],
};
</script>
