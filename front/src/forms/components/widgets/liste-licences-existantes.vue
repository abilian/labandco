<template>
  <table class="table table-condensed table-bordered" style="width: 100%;">
    <thead>
      <tr class="personnel">
        <th width="25">
          <a class="btn btn-default" @click.prevent="add_line()">
            +
          </a>
        </th>
        <th width="45%">
          Type de la licence
        </th>
        <th width="45%">
          Nom et version de la licence
        </th>
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
          <input v-model="line.type_licence" class="form-control" type="text" />
        </td>

        <td>
          <input
            v-model="line.nom_version_licence"
            class="form-control"
            type="text"
          />
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import { add_line, remove_line } from "./common";

export default {
  name: "ListeLicencesExistantesWidget",
  props: ["field", "model"],
  methods: { add_line, remove_line },
};
</script>
