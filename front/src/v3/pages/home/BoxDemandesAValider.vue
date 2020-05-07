<template>
  <div class="col-md-4">
    <router-link :to="`/demandes_a_valider/${tag}`">
      <div class="info-box">
        <span :class="'info-box-icon ' + bgColor"
          ><i class="far fa-briefcase"
        /></span>
        <div class="info-box-content">
          <span class="info-box-text">{{ name }}</span>
          <span class="info-box-number">{{ nb }}</span>
        </div>
      </div>
    </router-link>
  </div>
</template>

<script>
export default {
  props: ["name", "color", "nb", "tag"],

  computed: {
    bgColor() {
      if (this.nb) {
        return this.color;
      } else {
        return "bg-gray";
      }
    },
  },
};
</script>
