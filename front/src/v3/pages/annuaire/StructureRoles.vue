<template>
  <div>
    <div v-if="ou && ready">
      <b-table-simple striped hover outlined class="mt-4">
        <tbody v-if="editing">
          <tr v-for="selector in selectors">
            <td class="w-30 text-muted text-right ">{{ selector.label }}</td>

            <td class="w-70">
              <multiselect
                v-model="selector.value"
                :options="selector.options"
                :multiple="selector.multiple"
                track-by="id"
                label="label"
              />
            </td>
          </tr>
        </tbody>

        <tbody v-else>
          <tr v-for="role in roles">
            <td class="w-30 text-muted text-right">{{ role.label }}</td>

            <td class="w-70">
              <ul class="mb-0 pl-0" style="list-style-type: none;">
                <li v-for="user in role.users" class="w-100 ml-0">
                  <router-link :to="{ name: 'user', params: { id: user.id } }"
                    >{{ user.name }}
                  </router-link>
                </li>
              </ul>
            </td>
          </tr>
        </tbody>
      </b-table-simple>

      <template v-if="editing">
        <button class="btn btn-primary mr-3" @click="save">Enregistrer</button>
        <button class="btn btn-danger" @click="cancel">Annuler</button>
      </template>
      <button
        v-else-if="selectors.length > 0"
        class="btn btn-default"
        @click="makeEditable"
      >
        Modifier
      </button>
    </div>

    <div v-else>Chargement en cours...</div>
  </div>
</template>

<script>
import EventBus from "../../../event-bus";

export default {
  props: {
    ou: Object,
  },

  data() {
    return {
      ready: false,
      roles: [],

      // For multiselect
      selectors: [],
      editing: false,
    };
  },

  watch: {
    $route: "fetchData",
    ou: "fetchData",
  },

  methods: {
    fetchData() {
      if (!this.ou) {
        this.roles = [];
        // Multi
        this.selectors = [];
        return;
      }

      const args = [this.ou.id];
      this.$root.rpc("get_roles", args).then(result => {
        this.roles = result;
        this.ready = true;
      });

      this.$root.rpc("get_role_selectors", args).then(result => {
        this.selectors = result;
      });
    },

    // Edit
    makeEditable() {
      if (this.selectors.length === 0) {
        return;
      }
      this.editing = true;
    },

    cancel() {
      this.editing = false;
    },

    save() {
      const values = {};
      for (let e of this.selectors) {
        values[e.key] = e.value;
      }
      const args = [this.ou.id, values];
      const msg = "Rôles mis à jour";
      this.$root.rpc("update_roles", args, msg).then(result => {
        this.ready = false;
        this.editing = false;
        EventBus.$emit("refresh-structure");
      });
    },
  },
};
</script>
