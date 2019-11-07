<template>
  <div>
    <label class="checkbox-inline">
      <input
        :id="field.name"
        v-model="model[field.name]"
        type="radio"
        :name="field.name"
        value="oui"
      />
      Oui
    </label>

    <label class="checkbox-inline">
      <input
        :id="field.name"
        v-model="model[field.name]"
        type="radio"
        :name="field.name"
        value="non"
      />
      Non
    </label>

    <label class="checkbox-inline">
      <input
        :id="field.name"
        v-model="model[field.name]"
        type="radio"
        :name="field.name"
        value="?"
      />
      Ne sait pas
    </label>
  </div>
</template>

<script>
export default {
  name: "TriStateWidget",
  props: ["field", "model"],
};
</script>
