// import "../sass/overrides.scss";

/* eslint-disable no-new, no-undef, import/first */
// Fix this later (if you can figure out what it means!):
/* eslint-disable vue/no-dupe-keys */

import "../vendor/fontawesome-pro/css/all.css";

// Remove ?
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue/dist/bootstrap-vue.css";

// import "select2/dist/css/select2.css";
import "vue-select/dist/vue-select.css";

import "../sass/adminlte.css";
import "../sass/main.scss";

import Vue from "vue";
import "./plugins/element";

//
// v3
//
import router from "./v3/router";
import BootstrapVue from "bootstrap-vue";
import Multiselect from "vue-multiselect";
import { Vue2Storage } from "vue2-storage";
import VueMoment from "vue-moment";
import moment from "moment";
import accounting from "accounting";
import vSelect from "vue-select";
import VueQuillEditor from "vue-quill-editor";
import "quill/dist/quill.core.css";
import "quill/dist/quill.snow.css";
import "quill/dist/quill.bubble.css";

//
// Register plugins & filters
//
Vue.use(BootstrapVue);

Vue.component("multiselect", Multiselect);
Vue.component("v-select", vSelect);

Vue.use(Vue2Storage, {
  prefix: "app_",
  driver: "local",
  ttl: 60 * 60 * 24 * 1000,
});

moment.locale("fr");
Vue.use(VueMoment, { moment });

Vue.filter("currency", function(val, symbol) {
  return accounting.formatMoney(val, symbol);
});

Vue.use(VueQuillEditor);

//
// Our own components & libraries
//
import Breadcrumbs from "./v3/components/navigation/Breadcrumbs";
// import MyForm from "./forms/components/my-form.vue";
import rpc from "./v3/rpc";

Vue.component("breadcrumbs", Breadcrumbs);

//
// Our apps
//
import App from "./v3/App";
import LoginApp from "./v3/LoginApp";
import FeuilleCout from "./v3/components/FeuilleCout.vue";

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

if (document.getElementById("feuille-cout")) {
  const model = MODEL;
  new Vue({
    el: "#feuille-cout",
    components: { FeuilleCout },
    data: { model },
    methods: {
      rpc: rpc,
    },
  });
}

// if (document.getElementById("constants-editor")) {
//   new Vue({
//     el: "#constants-editor",
//     components: { ConstantsEditor, VueQuillEditor },
//   });
//   Vue.use(VueQuillEditor);
// }

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
