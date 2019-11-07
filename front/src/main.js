// import "../sass/overrides.scss";

/* eslint-disable no-new, no-undef, import/first */
// Fix this later (if you can figure out what it means!):
/* eslint-disable vue/no-dupe-keys */

import "@fortawesome/fontawesome-pro/css/fontawesome.css";

import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue/dist/bootstrap-vue.css";

// import "select2/dist/css/select2.css";

import "../sass/adminlte.css";
import "../sass/main.scss";

import Vue from "vue";
import "./plugins/element.js";

import Toasted from "vue-toasted";

Vue.use(Toasted, {
  position: "top-center",
  duration: 5000,
  fullWidth: true,
  action: {
    text: "X",
    onClick: (e, toastObject) => {
      toastObject.goAway(0);
    },
  },
});

//
// v3
//
import router from "./v3/router";
import BootstrapVue from "bootstrap-vue";
import Multiselect from "vue-multiselect";
import { Vue2Storage } from "vue2-storage";

// Register plugins
Vue.use(BootstrapVue);
Vue.component("multiselect", Multiselect);
Vue.use(Vue2Storage, {
  prefix: "app_",
  driver: "local",
  ttl: 60 * 60 * 24 * 1000,
});

// My own components
import Breadcrumbs from "./v3/components/visual/Breadcrumbs";
import MyForm from "./forms/components/my-form.vue";

Vue.component("breadcrumbs", Breadcrumbs);
Vue.component("my-form", MyForm);

// My stuff
import rpc from "./v3/rpc";

// My apps
import App from "./v3/App";
import LoginApp from "./v3/LoginApp";

if (document.getElementById("app-v3")) {
  /* eslint-disable no-new */
  new Vue({
    el: "#app-v3",
    router,
    render: h => h(App),
    methods: {
      rpc: rpc,
    },
  });
}

if (document.getElementById("login")) {
  /* eslint-disable no-new */
  new Vue({
    el: "#login",
    router,
    render: h => h(LoginApp),
  });
}

// // Filters
// import accounting from "accounting";
//
// Vue.filter("currency", function(val, symbol) {
//   return accounting.formatMoney(val, symbol);
// });
//
// // Feuille de coût
// import FeuilleCout from "./feuille_cout/components/feuille-cout.vue";
//
// if (document.getElementById("feuille-cout")) {
//   const model = MODEL;
//   new Vue({
//     el: "#feuille-cout",
//     components: { FeuilleCout },
//     data: { model },
//   });
// }
//
// // Tables & formulaire demande
// import BoxDemandes from "./grids/box-demandes.vue";
//
// if (document.getElementById("boxes-demandes")) {
//   new Vue({
//     el: "#boxes-demandes",
//     components: { BoxDemandes },
//   });
// }
//
// // import MyForm from "./forms/components/my-form.vue";
// //
// // if (document.getElementById("vue-newform")) {
// //   new Vue({
// //     el: "#vue-newform",
// //     components: { MyForm },
// //     data: {
// //       form: FORM,
// //       model: MODEL,
// //     },
// //   });
// // }
//
// // Constants Editor
// import ConstantsEditor from "./admin2/constantsEditor.vue";
// import VueQuillEditor from "vue-quill-editor";
// import "quill/dist/quill.core.css";
// import "quill/dist/quill.snow.css";
// import "quill/dist/quill.bubble.css";
//
// if (document.getElementById("constants-editor")) {
//   new Vue({
//     el: "#constants-editor",
//     components: { ConstantsEditor, VueQuillEditor },
//   });
//   Vue.use(VueQuillEditor);
// }
//
// //
// // ckeditor (widget provided by Abilian-Core currently)
// //
//
// // import 'ckeditor/ckeditor';
//
// window.onload = function() {
//   const CKEDITOR = window.CKEDITOR;
//   const widgets = $(".js-widget");
//
//   for (let widget of widgets) {
//     widget = $(widget);
//     const widget_type = widget.data("init-with");
//     if (widget_type !== "richtext") {
//       continue;
//     }
//
//     // var name = widget.attr['name'];
//     // var allowed_tags = widget.data('allowed-tags');
//
//     CKEDITOR.replace(widget.get(0));
//   }
// };
