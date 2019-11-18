<template>
  <aside class="main-sidebar sidebar-dark-primary">
    <div style="background-color: white;" class="p-3">
      <a href="/">
        <img src="/static/img/logo-su.svg" alt="Home" typeof="foaf:Image" />
      </a>
    </div>

    <!-- sidebar: style can be found in sidebar.less -->
    <div class="sidebar">
      <!-- Sidebar user panel -->
      <div class="user-panel mt-3 pb-3 mb-3 d-flex">
        <div class="image">
          <img
            src="/static/img/anonymous2.png"
            class="img-circle"
            alt="User Image"
          />
        </div>
        <div class="info">
          <a class="d-block">{{ user.prenom }} {{ user.nom }}</a>
        </div>
      </div>

      <nav class="mt-2">
        <ul
          v-for="subMenu in menu"
          class="nav nav-pills nav-sidebar flex-column"
        >
          <li class="nav-header text-uppercase">{{ subMenu.label }}</li>

          <li v-for="entry in subMenu.entries" class="nav-item">
            <router-link v-if="entry.to" :to="entry.to" class="nav-link">
              <i class="nav-icon far" v-bind:class="['fa-' + entry.icon]"></i>
              {{ entry.label }}
            </router-link>
            <a
              v-else-if="entry.url"
              :href="entry.url"
              target="_blank"
              class="nav-link"
            >
              <i class="nav-icon far" v-bind:class="['fa-' + entry.icon]"></i>
              {{ entry.label }}
            </a>
            <a v-else href="#" class="nav-link"
              ><i class="nav-icon far" v-bind:class="['fa-' + entry.icon]"></i>
              {{ entry.label }}
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </aside>
</template>

<script>
export default {
  computed: {
    user() {
      return this.$storage.get("user_context").user;
    },
    menu() {
      return this.$storage.get("user_context").menu;
    },
  },
};
</script>

<style scoped>
i.far {
  width: 1.3em;
}
</style>
