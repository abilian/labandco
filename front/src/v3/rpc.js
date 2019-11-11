import axios from "axios";

const DEBUG = true;

export function call(methodName, args, msg = null) {
  console.log("this (in rpc) = ", this);

  let id;
  if (this) {
    id = this.id = (this.id || 0) + 1;
    if (DEBUG) {
      console.log(`rpc call (${this.id}):`, methodName, args);
    }
  } else {
    id = Math.floor(Math.random() * Number.MAX_SAFE_INTEGER);
  }

  const data = {
    jsonrpc: "2.0",
    method: methodName,
    params: args,
    id: id,
  };
  return axios
    .post("/rpc/", data)
    .then(response => {
      const data = response.data;
      if (DEBUG) {
        if (data.result) {
          console.log(`rpc result (${response.data.id}):`, data.result);
        } else {
          console.log(`rpc error (${response.data.id}):`, data.error);
        }
      }
      return data.result;
    })
    .then(result => {
      if (this && msg) {
        this.$root.$bvToast.toast(msg, {
          title: "OK",
          variant: "success",
          solid: true,
        });
      }
      return result;
    })
    .catch(error => {
      console.log(error);
      if (this) {
        const msg = `Désolé, une erreur est survenue: ${error}`;
        this.$root.$bvToast.toast(msg, {
          title: "Oups",
          variant: "danger",
          solid: true,
          noAutoHide: true,
        });
      }
    });
}

export default call;
