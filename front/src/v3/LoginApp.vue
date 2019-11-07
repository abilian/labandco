<template>
  <div>
    Please wait a bit.
  </div>
</template>

<script>
import axios from "axios";

export default {
  created() {
    const url = "/v3/api/ui-context";
    axios.get(url).then(response => {
      const data = response.data;

      this.$storage.set("user", data.user);
      this.$storage.set("menu", data.menu);

      window.location.replace("/");
    });
  },
};
</script>
