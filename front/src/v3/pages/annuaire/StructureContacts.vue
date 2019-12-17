<template>
  <div v-if="ou" @dblclick="makeEditable" @keydown.esc="cancel" tabindex="0">
    <b-table-simple striped hover outlined class="mt-4">
      <tbody>
        <tr>
          <th class="w-30">Bureau</th>
          <th class="w-70">Correspondant</th>
        </tr>
        <tr v-for="contact in contacts">
          <td>{{ contact.type_value }}</td>
          <td>
            <router-link
              v-if="contact.id && !editing"
              :to="{ name: 'user', params: { id: contact.id } }"
              >{{ contact.name }}
            </router-link>
            <select
              v-if="editing"
              :name="contact.type_name"
              v-model="selected[contact.type_name]"
            >
              <option value="">(Aucun)</option>
              <option v-for="m of membresDgrtt" :value="m.uid">
                {{ m.nom }}, {{ m.prenom }}
              </option>
            </select>
          </td>
        </tr>
      </tbody>
    </b-table-simple>

    <template v-if="editing">
      <button class="btn btn-primary mr-3" @click="save">Enregistrer</button>
      <button class="btn btn-danger" @click="cancel">Annuler</button>
    </template>
    <button
      v-else-if="ou.editable"
      class="btn btn-default"
      @click="makeEditable"
    >
      Modifier
    </button>
  </div>
  <div v-else>Chargement en cours...</div>
</template>

<script>
import EventBus from "../../../event-bus";

export default {
  props: {
    ou: Object,
  },

  data() {
    return {
      editing: false,
      contacts: [],
      membresDgrtt: [],
      selected: {},
    };
  },

  watch: {
    $route: "fetchData",
    ou: "fetchData",
  },

  methods: {
    fetchData() {
      this.$root.rpc("get_contacts", [this.ou.id]).then(result => {
        this.contacts = result;

        for (let contact of this.contacts) {
          this.$set(this.selected, contact.type_name, contact.uid);
        }
      });
    },

    // Edit
    makeEditable() {
      if (!this.ou.editable) {
        return;
      }
      this.$root.rpc("get_membres_dri", []).then(result => {
        this.membresDgrtt = result;
        this.editing = true;
      });
    },

    cancel() {
      this.editing = false;
    },

    save() {
      const args = [this.ou.id, this.selected];
      const msg = "Contacts mis à jour";
      this.$root
        .rpc(
          "update_contacts",
          args,

          msg
        )
        .then(result => {
          EventBus.$emit("refresh-structure");
        });
    },
  },
};
</script>
