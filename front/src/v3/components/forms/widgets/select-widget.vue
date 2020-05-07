<template>
  <v-select
    :name="field.name"
    :value="value"
    :options="options"
    @input="setSelected"
  />

  <!--  <select-->
  <!--    v-model="model[field.name]"-->
  <!--    :name="field.name"-->
  <!--    :readonly="!field.editable"-->
  <!--    class="form-control"-->
  <!--    multiple-->
  <!--  >-->
  <!--    <template v-for="item in field.choices">-->
  <!--      <option :selected="model[field.name] === item[0]" :value="item[0]">-->
  <!--        {{ item[1] }}-->
  <!--      </option>-->
  <!--    </template>-->
  <!--  </select>-->
</template>

<script>
import EventBus from "../../../../event-bus";

export default {
  name: "SelectWidget",
  props: ["field", "model"],

  computed: {
    options() {
      return this.field.choices;
    },

    value() {
      return this.model[this.field.name];
    },
  },

  methods: {
    setSelected(value) {
      this.$set(this.model, this.field.name, value);
      EventBus.$emit("model-changed");
    },
  },
};
</script>
