<template>
  <table class="table table-condensed table-bordered" style="width: 100%;">
    <thead>
      <tr class="personnel">
        <th>
          <a class="btn btn-default" @click.prevent="add_line()">
            +
          </a>
        </th>
        <th>
          Nom de l'entreprise<br />
          <em>
            Joindre la copie de l'accord de secret avec l'onglet Pièces à
            joindre, une fois que vous aurez enregistré le formulaire
          </em>
        </th>
        <th>Contact dans l'entreprise</th>
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
          <input v-model="line.contact" class="form-control" type="text" />
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import { add_line, remove_line } from "./common";

export default {
  name: "ListePartenairesContactesWidget",
  props: ["field", "model"],
  methods: { add_line, remove_line },
};
</script>
