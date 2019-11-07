import axios from "axios";

const DEBUG = true;

export function call(methodName, args, cb = null, msg = null) {
  this.id = this.id || 0;
  if (DEBUG) {
    console.log(`rpc call (${this.id}):`, methodName, args);
  }

  axios
    .post("/rpc/", {
      jsonrpc: "2.0",
      method: methodName,
      params: args,
      id: this.id++,
    })
    .then(response => {
      const data = response.data;
      if (DEBUG) {
        if (data.result) {
          console.log(`rpc result (${response.data.id}):`, data.result);
        } else {
          console.log(`rpc error (${response.data.id}):`, data.error);
        }
      }
      if (cb) {
        cb(data.result);
      }
      if (msg) {
        this.$root.$bvToast.toast(msg, {
          title: "OK",
          variant: "success",
          solid: true,
        });
      }
    })
    .catch(error => {
      console.log(error);
      const msg = `Désolé, une erreur est survenue: ${error}`;
      this.$root.$bvToast.toast(msg, {
        title: "Oups",
        variant: "danger",
        solid: true,
        noAutoHide: true,
      });
    });
}

export default call;
