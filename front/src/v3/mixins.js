import _ from "lodash";

export const ContextFetcher = {
  data() {
    return {
      ready: false,
    };
  },

  watch: {
    ready: "whenReady",
  },

  methods: {
    fetchContext() {
      const route = this.$route;
      const args = { name: route.name, params: route.params };
      return this.$root.rpc("get_context", args).then((result) => {
        _.assign(this, result);
        this.ready = true;
      });
    },
  },

  beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.fetchContext();
    });
  },

  beforeRouteUpdate(to, from, next) {
    this.fetchContext();
  },

  whenReady() {},
};
