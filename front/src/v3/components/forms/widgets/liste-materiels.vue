<template>
  <table class="table table-condensed table-bordered" style="width: 100%;">
    <thead>
      <tr class="personnel">
        <th width="30">
          <a class="btn btn-default" @click.prevent="add_line()">
            +
          </a>
        </th>
        <th width="90%">
          Précisez le matériel concerné
          <em>
            Joindre une copie de l’accord de transfert de matériel (MTA)
            correspondant avec l’onglet Pièces à joindre, une fois que vous
            aurez enregistré le formulaire
          </em>
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
          <input v-model="line.materiel" class="form-control" type="text" />
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import { add_line, remove_line } from "./common";

export default {
  name: "ListeMaterielssWidget",
  props: ["field", "model"],
  methods: { add_line, remove_line },
};
</script>
