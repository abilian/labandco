<template>
  <td class="w-70">
    <table class="table" style="width: 100%; margin-bottom: 0;">
      <tr>
        <th
          v-for="l in field.specs"
          class="text-muted"
          style="font-weight: normal;"
        >
          {{ l[1] }}
        </th>
      </tr>
      <template v-if="value">
        <tr v-for="item in value">
          <td v-for="l in field.specs">{{ item[l[0]] }}</td>
        </tr>
      </template>
    </table>
  </td>
</template>

<script>
export default {
  props: ["field", "value"],
  // FIXME
  // props: {
  //   field: Object,
  //   value: Array,
  // },
};
</script>
