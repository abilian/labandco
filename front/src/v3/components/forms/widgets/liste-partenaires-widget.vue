<template>
  <table class="table table-condensed table-bordered" style="width: 100%">
    <thead>
      <tr class="personnel">
        <th>
          <a class="btn btn-default" @click.prevent="add_line()"> + </a>
        </th>
        <th>Nom du partenaire</th>
        <th>Prénom et nom du contact administratif / juridique</th>
        <th>Téléphone</th>
        <th>Mail</th>
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
            v-model="line.nom_partenaire"
            class="form-control"
            type="text"
          />
        </td>

        <td>
          <input
            v-model="line.prenom_nom_contact"
            class="form-control"
            type="text"
          />
        </td>

        <td>
          <input
            v-model="line.telephone_contact"
            class="form-control"
            type="text"
          />
        </td>

        <td>
          <input v-model="line.mail_contact" class="form-control" type="text" />
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import { add_line, remove_line } from "./common";

export default {
  name: "ListePartenairesWidget",
  props: ["field", "model"],

  methods: { add_line, remove_line },
};
</script>
