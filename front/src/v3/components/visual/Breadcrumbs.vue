<template>
  <section class="content-header">
    <ol class="breadcrumb">
      <li class="breadcrumb-item">
        <a href="/"><i class="far fa-home"></i> Accueil</a>
      </li>
      <li v-for="crumb in path" class="breadcrumb-item">
        <router-link :to="crumb[1]">
          {{ crumb[0] }}
        </router-link>
      </li>
      <li class="breadcrumb-item active">{{ title }}</li>
    </ol>
  </section>
</template>

<script>
export default {
  props: { title: String, path: Array },
};
</script>

<style scoped>
.content-header {
  padding: 0;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}
.breadcrumb {
  padding-left: 0;
}
</style>
