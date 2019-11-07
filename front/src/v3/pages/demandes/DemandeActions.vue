<template>
  <b-card no-body>
    <div class="card-header">
      <h3 class="card-title">Actions possibles</h3>
    </div>

    <div class="card-body">
      <form action="/wf/transition" method="POST">
        <input
          type="hidden"
          name="csrf_token"
          value="1562073852##17b80a5aaeb913091ee6c1f50b9ffae5aca8f89d"
        />

        <input type="hidden" name="id" value="2643" />

        <button
          type="submit"
          class="btn btn-danger"
          name="action"
          value="PRENDRE_LA_MAIN_DGRTT"
        >
          Prendre la main sur la demande
        </button>

        <button
          type="submit"
          class="btn btn-danger"
          name="action"
          value="REJETER_DGRTT"
        >
          Rejeter / abandonner demande
        </button>
      </form>
    </div>
  </b-card>
</template>

<script>
export default {
  name: "DemandeActions",
};
</script>
