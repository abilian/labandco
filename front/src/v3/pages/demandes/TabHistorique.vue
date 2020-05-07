<template>
  <div class="mt-4">
    <h3>État actuel</h3>

    <p>
      Etat de workflow actuel: <b>{{ state.label }}</b> (workflow
      {{ demande.active ? "en cours" : "terminé" }})
    </p>

    <p>
      Prochaine action: <b>{{ state.next_action }}</b>
    </p>

    <p v-if="owners.length">
      Tâche entre les mains de:
      <span v-for="owner in owners">
        <b>
          <router-link :to="{ name: 'user', params: { id: owner.id } }">
            {{ owner.full_name }}
          </router-link>
          <!--  TODO      {%- if not loop.last -%}, {% endif -%}-->
        </b>
      </span>
    </p>

    <p v-if="demande.wf_retard">
      Nombre de jours de retard dans le traitement:
      <b>{{ demande.wf_retard }}</b>
    </p>
    <p v-else>Pas de retard.</p>

    <hr />

    <h3>Historique des actions</h3>

    <div v-for="entry in workflow_history">
      <p>{{ entry.date }}: <span v-html="entry.message" /></p>
      <blockquote v-if="entry.note">
        {{ entry.note }}
      </blockquote>
    </div>

    <hr />

    <h3>Historique des versions</h3>

    <h4>Version courante</h4>

    <p>
      Version: <b>{{ past_versions.length + 1 }}</b
      >, sauvegardée le
      <b>{{ demande.updated_at | moment("DD MMMM YYYY à h:mm:ss") }}</b
      >.
    </p>

    <h4>Versions antérieures</h4>

    <ul>
      <li v-for="(v, i) in past_versions">
        Version: <b>{{ i }}</b
        >, sauvegardée le {{ v[1] | moment("DD MMMM YYYY à h:mm:ss") }}.

        <!-- TODO -->
        <!--            <a-->
        <!--              href="{{ url_for(" .demande_compare", id=demande.id, version=loop.index) }}">Comparer-->
        <!--            à la version courante</a></li>-->
        <!--          {% endfor %}-->
      </li>
    </ul>
  </div>
</template>

<script>
import fp from "lodash/fp";

export default {
  props: { demande: Object },

  data() {
    const demande = this.demande;
    const workflow = demande.workflow;

    const result = {
      workflow: workflow,
      owners: workflow.owners,
      state: workflow.state,
      workflow_history: fp.reverse(demande.workflow_history), // TODO: reverse
      past_versions: demande.past_versions,
    };
    return result;
  },
};
</script>
