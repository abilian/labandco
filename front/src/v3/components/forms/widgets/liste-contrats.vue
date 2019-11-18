<template>
  <table class="table table-condensed table-bordered" style="width: 100%;">
    <thead>
      <tr class="personnel">
        <th width="30">
          <a class="btn btn-default" @click.prevent="add_line()">
            +
          </a>
        </th>
        <th width="30%">
          Contrat/Partenariat de recherche
        </th>
        <th width="30%" style="vertical-align:top;">
          Date de signature du contrat
        </th>
        <th width="30%" style="vertical-align:top;">
          Référence du contrat (N° - Nom du partenaire)
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
          <input v-model="line.contrat" class="form-control" type="text" />
        </td>

        <td>
          <input
            v-model="line.date_signature"
            class="form-control"
            type="text"
          />
        </td>

        <td>
          <input v-model="line.reference" class="form-control" type="text" />
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import { add_line, remove_line } from "./common";

export default {
  name: "ListeContratsWidget",
  props: ["field", "model"],
  methods: { add_line, remove_line },
};
</script>
