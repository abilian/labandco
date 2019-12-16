<template>
  <b-card no-body>
    <div class="card-header">
      <h3 class="card-title">Actions possibles</h3>
    </div>

    <div v-if="demande" class="card-body">
      <!-- TODO -->
      <a v-if="demande.is_editable" href="#" class="btn btn-primary m-2"
        >Modifier la demande</a
      >

      <!--          href="{{ url_for(".demande_edit", id=demande.id) }}"-->
      <!--            class="btn {% if form.errors %}btn-primary{% else %}btn-default{% endif %}">-->
      <!--          Modifier la demande</a>-->

      <a v-if="demande.is_duplicable" href="#" class="btn btn-default m-2"
        >Dupliquer la demande</a
      >

      <!--        {% if g.current_user in [demande.porteur, demande.gestionnaire] %}-->
      <!--          <button name="action" value="dupliquer"-->
      <!--              formaction="{{ url_for(".demande_post", id=demande.id) }}"-->
      <!--              class="btn btn-default">Dupliquer la demande-->
      <!--          </button>-->
      <!--        {% endif %}-->

      <button
        v-for="transition in transitions"
        type="submit"
        :class="`btn btn-${transition.category} m-2`"
        name="action"
        :value="transition.id"
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
};
</script>
