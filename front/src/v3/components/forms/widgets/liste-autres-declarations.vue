<template>
  <table class="table table-condensed table-bordered" style="width: 100%">
    <thead>
      <tr class="personnel">
        <th width="30">
          <a class="btn btn-default" @click.prevent="add_line()"> + </a>
        </th>
        <th width="30%">Type de protection</th>
        <th width="30%" style="vertical-align: top">
          Organisme ayant fait le dépôt
        </th>
        <th width="30%" style="vertical-align: top">
          Exploitation industrielle
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
          <select v-model="line.type_protection" class="form-control">
            <template
              v-for="item in [
                'Brevet',
                'Savoir faire',
                'Logiciel',
                'Marque',
                'Base de données',
              ]"
            >
              <option :selected="line.type_protection === item" :value="item">
                {{ item }}
              </option>
            </template>
          </select>
        </td>

        <td>
          <input v-model="line.organisme" class="form-control" type="text" />
        </td>

        <td>
          <input v-model="line.exploitation" class="form-control" type="text" />
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import { add_line, remove_line } from "./common";

export default {
  name: "ListeAutresDeclarationsWidget",
  props: ["field", "model"],
  methods: { add_line, remove_line },
};
</script>
