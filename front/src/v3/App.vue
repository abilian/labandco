<template>
  <div>
    <app-navbar />

    <app-sidebar />

    <div class="content-wrapper">
      <section class="content">
        <div class="row">
          <div class="col-md-12">
            <router-view />
          </div>
        </div>
      </section>
    </div>

    <app-footer />
  </div>
</template>

<script>
import AppNavbar from "./components/navigation/AppNavbar";
import AppSidebar from "./components/navigation/AppSidebar";
import AppFooter from "./components/navigation/AppFooter";

export default {
  components: { AppFooter, AppSidebar, AppNavbar },
};
</script>
