<template>
  <div>
    <breadcrumbs title="Préférences"></breadcrumbs>

    <div class="card">
      <div class="card-header with-border">
        <h3 class="card-title">Préférences utilisateur</h3>
      </div>

      <div class="card-body">
        <h4 class="mb-4">Recevoir les notifications</h4>

        <b-form-radio
          v-for="choice in choices"
          v-model="selected"
          :value="choice[0]"
          v-bind:key="choice[0]"
          >{{ choice[1] }}</b-form-radio
        >

        <h4 class="mt-5 mb-3">Notification pour les contacts Lab&Co</h4>

        <p>
          Choisissez le nombre de jours (maximum 30) au-delà duquel vous serez
          notifié lorsqu'une demande dont vous êtes le contact n'a donné lieu à
          aucune activité.
        </p>

        <b-form-input
          v-model="nbJours"
          type="range"
          min="0"
          max="30"
        ></b-form-input>

        <p>{{ nbJours }}</p>

        <div>
          <button
            type="submit"
            @click="onSubmit()"
            class="btn btn-primary mt-3"
          >
            Valider
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

const URL = "/v3/api/user/preferences";

export default {
  name: "Preferences",

  data() {
    return {
      choices: null,
      selected: null,
      nbJours: 0,
    };
  },

  created() {
    this.update();
  },

  methods: {
    update() {
      axios.get(URL).then(response => {
        const data = response.data;

        this.choices = data.choices;
        this.selected = data.preferences_notifications;
        this.nbJours = data.nb_jours_notification;
      });
    },

    onSubmit() {
      const data = {
        preferences_notifications: this.selected,
        nb_jours_notification: Number(this.nbJours),
      };
      axios.post(URL, data).then(response => {
        this.$bvToast.toast("Préférences mises à jour", {
          title: "Préférences mises à jour",
          solid: true,
          variant: "success",
        });
      });
    },
  },
};
</script>
