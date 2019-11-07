<template>
  <span>
    <template v-for="(role, index) in roles">
      <span v-if="role === 'Membre affecté'" class="text-bold">Membre</span>
      <span v-else-if="role === 'Membre rattaché'">Membre</span>
      <span v-else-if="role === 'Membre affilié'" class="text-gray"
        >Membre</span
      >
      <span v-else>{{ role }}</span>
      <span v-if="index !== roles.length - 1">, </span>
    </template>
  </span>
</template>

<script>
export default {
  name: "RoleList",

  props: {
    roles: Array,
  },
};
</script>
