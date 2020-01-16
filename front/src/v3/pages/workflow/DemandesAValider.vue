<template>
  <div class="box">
    <div class="box-header box-primary">
      <h3 class="box-title">Demandes à valider ({{ demandes.length }})</h3>
    </div>

    <div class="box-body table-responsive">
      <table class="table table-hover">
        <tbody>
          <tr>
            <th width="10%">Date</th>
            <th width="10%">Type</th>
            <th width="20%">Demandeur</th>
            <th width="60%">Intitulé</th>
          </tr>

          <tr v-for="demande in demandes">
            <a href="{{ url_for(demande) }}">
              <td>{{ demande.created_at.strftime("%d/%m/%Y") }}</td>
              <td><i class="{{ demande.icon_class }}" /></td>
              <td>{{ demande.porteur.full_name }}</td>
              <td>
                <a href="{{ url_for(demande) }}">{{ demande.nom }}</a>
              </td>
            </a>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: "DemandesAValider",

  data() {
    return {
      demandes: [],
    };
  },

  // components: { BoxDemandes },
};
</script>
