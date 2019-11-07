<template>
  <aside class="main-sidebar sidebar-dark-primary">
    <div style="background-color: white;" class="p-3">
      <img src="/static/img/logo-su.svg" alt="Home" typeof="foaf:Image" />
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
          <a class="d-block">{{ user.name }}</a>
        </div>
      </div>

      <!-- search form -->
      <!--      <div class="sidebar-form">-->
      <!--        <div class="input-group">-->
      <!--          <input-->
      <!--              type="text"-->
      <!--              name="q"-->
      <!--              class="form-control"-->
      <!--              placeholder="Search..."-->
      <!--              v-model="q"-->
      <!--              @keydown.enter="search"-->
      <!--          />-->

      <!--          <span class="input-group-btn"-->
      <!--          ><button-->
      <!--              type="submit"-->
      <!--              name="search"-->
      <!--              id="search-btn"-->
      <!--              class="btn btn-flat"-->
      <!--              @click="search"-->
      <!--          >-->
      <!--              <i class="far fa-search"></i>-->
      <!--            </button>-->
      <!--          </span>-->
      <!--        </div>-->
      <!--      </div>-->
      <!-- /.search form -->

      <nav class="mt-2">
        <ul
          v-for="subMenu in menu"
          class="nav nav-pills nav-sidebar flex-column"
        >
          <li class="nav-header text-uppercase">{{ subMenu.label }}</li>

          <li v-for="entry in subMenu.entries" class="nav-item">
            <template v-if="entry.to">
              <router-link v-bind:to="entry.to" class="nav-link">
                <i class="nav-icon far" v-bind:class="['fa-' + entry.icon]"></i>
                {{ entry.label }}
              </router-link>
            </template>
            <template v-else="">
              <a href="#" class="nav-link"
                ><i
                  class="nav-icon far"
                  v-bind:class="['fa-' + entry.icon]"
                ></i>
                {{ entry.label }}
              </a>
            </template>
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
      return this.$storage.get("user");
    },
    menu() {
      return this.$storage.get("menu");
    },
  },
};
</script>

<style scoped>
i.far {
  width: 1.3em;
}
</style>
