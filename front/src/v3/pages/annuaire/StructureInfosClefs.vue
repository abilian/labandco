<template>
  <div v-if="ou" @keydown.esc="cancel" tabindex="0">
    <b-table-simple striped condensed outlined class="mt-4">
      <tbody>
        <tr>
          <td class="text-muted text-right w-30">Type</td>
          <td class="w-70">
            {{ ou.type_name }}
          </td>
        </tr>

        <tr>
          <td class="text-muted text-right">Nom</td>
          <td>
            <template v-if="editing"
              ><input v-model="model.nom" class="w-100"
            /></template>
            <a v-else @dblclick="makeEditable">{{ ou.nom }}</a>
          </td>
        </tr>

        <tr>
          <td class="text-muted text-right">Sigle</td>
          <td>
            <template v-if="editing"
              ><input v-model="model.sigle" class="w-100"
            /></template>
            <a v-else @dblclick="makeEditable">{{ ou.sigle }}</a>
          </td>
        </tr>

        <tr>
          <td class="text-muted text-right">ID LDAP</td>
          <td>
            <template v-if="editing"
              ><input v-model="model.dn" class="w-100"
            /></template>
            <a v-else @dblclick="makeEditable">{{ ou.dn }}</a>
          </td>
        </tr>

        <tr>
          <td class="text-muted text-right">Adresse email</td>
          <td>
            <template v-if="editing"
              ><input v-model="model.email" class="w-100"
            /></template>
            <a v-else @dblclick="makeEditable">{{ ou.email }}</a>
          </td>
        </tr>

        <tr>
          <td class="text-muted text-right">
            Permettre aux gestionnaires de répondre directement au contact
            Lab&amp;Co
          </td>
          <td>
            <b-form-checkbox
              v-if="editing"
              v-model="model.permettre_reponse_directe"
            />
            <a v-else @dblclick="makeEditable">
              <i
                v-if="ou.permettre_reponse_directe"
                class="far fa-check-square"
              />
            </a>
          </td>
        </tr>

        <tr>
          <td class="text-muted text-right">
            Permettre aux gestionnaires de soumettre au contact Lab&amp;Co
          </td>
          <td>
            <b-form-checkbox
              v-if="editing"
              v-model="model.permettre_soummission_directe"
            />
            <a v-else @dblclick="makeEditable">
              <i
                v-if="ou.permettre_soummission_directe"
                class="far fa-check-square"
              />
            </a>
          </td>
        </tr>
      </tbody>
    </b-table-simple>

    <template v-if="editing">
      <button class="btn btn-primary mr-3" @click="save">Enregistrer</button>
      <button class="btn btn-danger" @click="cancel">Annuler</button>
    </template>
    <button
      v-else-if="ou.permissions.P1"
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
      model: {},
      editing: false,
    };
  },
  methods: {
    makeEditable() {
      if (!this.ou.permissions.P1) {
        return;
      }
      this.model.nom = this.ou.nom;
      this.model.sigle = this.ou.sigle;
      this.model.dn = this.ou.dn;
      this.model.email = this.ou.email;
      this.model.permettre_reponse_directe = this.ou.permettre_reponse_directe;
      this.model.permettre_soummission_directe =
        this.ou.permettre_soummission_directe;
      this.editing = true;
    },

    cancel() {
      this.editing = false;
    },

    save() {
      const args = {
        id: this.ou.id,
        model: this.model,
      };
      const msg = "Structure mise à jour.";
      this.$root.rpc("sg_update_structure", args, msg).then((result) => {
        EventBus.$emit("refresh-structure");
        this.editing = false;
      });
    },
  },
};
</script>
