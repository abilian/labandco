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

import Vue from "vue";
import rpc from "./rpc";
import EventBus from "../event-bus";

export default {
  components: { AppFooter, AppSidebar, AppNavbar },

  created() {
    function refresh() {
      rpc("get_user_context", []).then((data) => {
        console.log("get_user_context ->", data);
        if (data) {
          Vue.$storage.set("user_context", data);
          EventBus.$emit("user-updated");
        }
      });
    }

    window.setInterval(refresh, 300000);
  },
};
</script>
