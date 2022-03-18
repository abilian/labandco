<template>
  <div v-if="demande" class="mt-4">
    <h3>Documents générés</h3>

    <template
      v-if="
        demande.is_valid &&
        !demande.acces_restreint &&
        demande.type === 'Recrutement'
      "
    >
      <ul>
        <li><a :href="`/demandes/${demande.id}/devis_rh`">Devis RH</a></li>
        <li>
          <a :href="`/demandes/${demande.id}/lettre_commande_rh`"
            >Lettre de commande RH</a
          >
        </li>
      </ul>
    </template>

    <template v-if="demande.type !== 'Recrutement'">
      <template
        v-if="
          !demande.documents_generes || demande.documents_generes.length === 0
        "
      >
        <p>Aucun document généré.</p>
      </template>
      <template v-else>
        <p v-for="pj in demande.documents_generes">
          <a :href="`/blob/${demande.id}/${pj.blob_id}`"
            >{{ pj.name }}, {{ pj.date }}</a
          >
        </p>
      </template>
    </template>
  </div>
</template>

<script>
export default {
  props: { demande: Object },
};
</script>
