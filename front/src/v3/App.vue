<template>
  <div>
    <app-navbar-vue></app-navbar-vue>

    <app-sidebar></app-sidebar>

    <div class="content-wrapper">
      <section class="content">
        <div class="row">
          <div class="col-md-12">
            <router-view></router-view>
          </div>
        </div>
      </section>
    </div>

    <app-footer></app-footer>
  </div>
</template>

<script>
import AppNavbarVue from "./components/visual/AppNavbarVue";
import AppSidebar from "./components/visual/AppSidebar";
import AppFooter from "./components/visual/AppFooter";

export default {
  components: { AppFooter, AppSidebar, AppNavbarVue },
};
</script>
