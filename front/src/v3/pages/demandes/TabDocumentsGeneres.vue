<template>
  <div class="mt-4">
    <h3>Documents générés</h3>

    <p v-for="pj in demande.documents_generes">
      <a :href="`/blob/${demande.id}/${pj.blob_id}`"
        >{{ pj.name }}, {{ pj.date }}</a
      >
    </p>

    <p v-if="demande.type === 'Recrutement' && !demande.is_valid">
      Cette demande est encore incomplète, le devis et la lettre de commande
      n'ont pas encore été générés.
    </p>
  </div>
</template>

<script>
export default {
  props: { demande: Object },
};
</script>
