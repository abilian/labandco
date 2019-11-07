<template>
  <div>
    <breadcrumbs title="Poser une question"></breadcrumbs>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">
          Poser une question ou formuler une suggestion
        </h3>
      </div>

      <div class="card-body">
        <p>
          Vous avez une question ou une suggestion pour la DR&I? Utilisez le
          formulaire ci-dessous.
        </p>

        <div class="form-group">
          <b-form-textarea
            :state="message.length > 0"
            v-model="message"
            id="message"
            placeholder="Question"
            rows="10"
          />
        </div>

        <button class="btn btn-primary mr-2" @click="submit">Envoyer</button>

        <button class="btn btn-default" @click="cancel">Annuler</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      message: "",
    };
  },

  methods: {
    submit() {
      const payload = {
        message: this.message,
      };
      axios
        .post("/v3/api/faq", payload)
        .then(() => {
          this.$bvToast.toast("Votre message a été transmis à la DR&I", {
            title: "Succès",
            variant: "success",
          });
          this.$router.push("/faq");
        })
        .catch(() => {
          this.$bvToast.toast("Une erreur est survenue, désolé.", {
            title: "Une erreur est survenue, désolé.",
            variant: "danger",
          });
        });
    },

    cancel() {
      this.$router.push("/faq");
    },
  },
};
</script>
