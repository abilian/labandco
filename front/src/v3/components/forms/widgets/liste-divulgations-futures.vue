<template>
  <table class="table table-condensed table-bordered" style="width: 100%">
    <thead>
      <tr class="personnel">
        <th width="30">
          <a class="btn btn-default" @click.prevent="add_line()"> + </a>
        </th>
        <th width="45%">
          Type de divulgation (résumé de congrès, article, communication
          orale,…)<br />
          <em>
            Joindre le document avec l'onglet Pièces à joindre, une fois que
            vous aurez enregistré le formulaire
          </em>
        </th>
        <th width="45%" style="vertical-align: top">Date envisagée</th>
      </tr>
    </thead>

    <tbody>
      <tr v-for="(line, index) in model[field.name]">
        <td>
          <button class="btn btn-danger" @click.prevent="remove_line(line)">
            -
          </button>
        </td>
        <td>
          <input
            v-model="line.type_divulgation"
            class="form-control"
            type="text"
          />
        </td>

        <td>
          <input v-model="line.date" class="form-control" type="text" />
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import { add_line, remove_line } from "./common";

export default {
  name: "ListeDivulgationsFuturesWidget",
  props: ["field", "model"],
  methods: { add_line, remove_line },
};
</script>
