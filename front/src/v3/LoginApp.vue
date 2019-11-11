<template>
  <div>
    Please wait a bit.
  </div>
</template>

<script>
import Vue from "vue";
import rpc from "./rpc";

export default {
  created() {
    Vue.$storage.clear();

    rpc("get_user_context", []).then(data => {
      Vue.$storage.set("user_context", data);
      window.location.replace("/");
    });
  },
};
</script>
