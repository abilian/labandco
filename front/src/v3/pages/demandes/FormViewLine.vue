<template>
  <tr v-if="visible">
    <td v-if="field.type === 'HTML'" colspan="2" v-html="field.label" />

    <template v-else>
      <td
        v-if="has_error"
        v-html="field.label"
        class="w-30 text-danger text-right"
      />
      <td v-else v-html="field.label" class="w-30 text-muted text-right" />

      <td v-if="field.scalar" class="w-70">
        <span v-if="value" v-html="displayValue()" />
      </td>

      <list-line v-else :field="field" :value="value" />
    </template>
  </tr>
</template>

<script>
import fp from "lodash/fp";
import ListLine from "./ListLine";

export default {
  props: {
    field: Object,
    value: [Object, String, Number, Array],
    has_error: Boolean,
    visible: Boolean,
  },

  components: {
    ListLine,
  },

  methods: {
    displayValue() {
      const value = this.value;
      if (Array.isArray(value)) {
        if (value[0].label) {
          return fp.map((x) => x.label, value).join(", ");
        } else {
          return value;
        }
      }
      if (value.label) {
        return value.label;
      }
      return value;
    },
  },
};
</script>
