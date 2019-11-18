<template>
  <b-card no-body>
    <div class="card-header">
      <h3 class="card-title">Actions possibles</h3>
    </div>

    <div v-if="demande" class="card-body">
      <a v-if="demande.is_editable" href="#" class="btn">Modifier la demande</a>

      <!--          href="{{ url_for(".demande_edit", id=demande.id) }}"-->
      <!--            class="btn {% if form.errors %}btn-primary{% else %}btn-default{% endif %}">-->
      <!--          Modifier la demande</a>-->

      <!--        {% if g.current_user in [demande.porteur, demande.gestionnaire] %}-->
      <!--          <button name="action" value="dupliquer"-->
      <!--              formaction="{{ url_for(".demande_post", id=demande.id) }}"-->
      <!--              class="btn btn-default">Dupliquer la demande-->
      <!--          </button>-->
      <!--        {% endif %}-->

      <!--        {% set transitions = workflow.possible_transitions() %}-->
      <!--        {% if transitions %}-->
      <!--          {% if csrf_token is defined %}-->
      <!--            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">-->
      <!--          {% endif %}-->

      <!--          <input type="hidden" name="id" value="{{ demande.id }}">-->

      <button
        v-for="transition in transitions"
        type="submit"
        :class="`btn btn-${transition.category}`"
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
