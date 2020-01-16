<template>
  <div>
    <breadcrumbs title="Poser une question" />

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
export default {
  data() {
    return {
      message: "",
    };
  },

  methods: {
    submit() {
      const args = {
        message: this.message,
      };

      // FIXME
      const msg = "Votre message a été transmis à la DR&I";
      this.$root
        .rpc("send_message", args, msg)
        .then(() => this.$router.push("/faq"));
    },

    cancel() {
      this.$router.push("/faq");
    },
  },
};
</script>
