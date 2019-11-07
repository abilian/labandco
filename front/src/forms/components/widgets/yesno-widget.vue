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

    <!--
      <label class="checkbox-inline">
        <input v-bind:id="field.name"
               v-bind:name="field.name" type="checkbox" value="y">&nbsp;
      </label>
    -->
  </div>
</template>

<script>
export default {
  name: "YesNoWidget",
  props: ["field", "model"],
};
</script>
