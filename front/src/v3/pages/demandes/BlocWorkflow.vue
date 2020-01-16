<template>
  <b-card no-body>
    <div class="card-header">
      <h3 class="card-title">Actions possibles</h3>
    </div>

    <div v-if="demande" class="card-body">
      <!-- TODO -->
      <button
        v-if="demande.is_editable"
        id="action-modifier"
        v-on:click="onClick"
        class="btn btn-primary m-2"
      >
        Modifier la demande
      </button>

      <!-- TODO -->
      <a v-if="demande.is_duplicable" href="#" class="btn btn-default m-2"
        >Dupliquer la demande</a
      >

      <button
        v-for="transition in transitions"
        type="submit"
        :class="`btn btn-${transition.category} m-2`"
        :value="transition.id"
        v-on:click="onClick"
        name="action"
      >
        {{ transition.label }}
      </button>
    </div>
  </b-card>
</template>

<script>
export default {
  props: { demande: Object },

  data() {
    const demande = this.demande;
    const workflow = demande.workflow;

    return {
      workflow: workflow,
      state: workflow.state,
      transitions: workflow.transitions,
    };
  },

  methods: {
    onClick(e) {
      const button = e.path[0];
      const buttonId = button.id;

      if (buttonId === "action-modifier") {
        this.$parent.goToTab(1);
      } else if (button.name === "action") {
        const action = button.value;
        const args = { demande_id: this.demande.id, action: action };
        this.$root.rpc("wf_transition", args).then(result => {
          const msg = result;
          this.$root.$bvToast.toast(msg[0], {
            title: "",
            variant: msg[1],
            solid: true,
          });
          this.$router.go();
        });
      }
    },
  },
};
</script>
