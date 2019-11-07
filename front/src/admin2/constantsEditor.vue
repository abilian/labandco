<template>
  <div>
    <div
      class="input-group input-group-sm float-right"
      style="max-width: 200px;"
    >
      <input
        v-model="filterKey"
        type="text"
        name="editor_search"
        class="form-control"
        placeholder="Filtrer"
      />

      <div class="input-group-btn">
        <button type="submit" class="btn btn-default float-right">
          <i class="far fa-search" />
        </button>
      </div>
    </div>

    <table class="table table-hover">
      <thead>
        <tr>
          <th>Clef</th>
          <th>Valeur</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="it in entries()" :key="it.key">
          <td>{{ it.key }}</td>

          <td v-if="isList(it.val)">
            <ul v-for="(elt, index) in it.val">
              <div v-if="isList(elt)">
                <!-- only sublists of 2 elts for now. -->
                <li>{{ elt[0] }}: {{ elt[1] }}</li>
              </div>
              <li v-else>
                {{ elt }}
              </li>
            </ul>

            <EditorModal
              :title="it.key"
              :data="it.val"
              :type="it.type"
              :dotted-key="it.key"
              @save="save"
            />
          </td>
          <td v-else>
            <div v-if="it.type === 'HTML'">
              <div v-html="it.val" />
            </div>
            <div v-else>
              {{ showVal(it.val, it.type) }}
            </div>

            <EditorModal
              :title="it.key"
              :data="it.val"
              :type="it.type"
              :dotted-key="it.key"
              @save="save"
            />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import _ from "lodash";
import axios from "axios";
import { Notification } from "element-ui";

import EditorModal from "./editorModal.vue";

export default {
  name: "ConstantsEditor",
  components: {
    EditorModal,
  },

  props: {
    url: String,
    urltypes: String,
    val: undefined, // for sub-components. Can be anything. If list or obj, sub-component.
  },

  data() {
    return {
      constants: undefined,
      types: {}, // obj constant name -> type (str).
      filterKey: "",
      dialogVisible: false,
      modalData: "",
    };
  },

  computed: {
    constantsList() {
      // Constants is a dict because order matters, we want to iterate on a list.
      // (below order not guaranted)

      if (this.constants) {
        return _.toPairs(this.constants);
      }
      if (this.val) {
        if (this.isObj(this.val)) {
          return _.toPairs(this.val);
        }
        return this.val;
      }
    },

    dottedConstants() {
      let val = this.val;
      let res;
      if (this.constants) {
        val = this.constants;
      }
      if (typeof val !== "undefined") {
        // Waiting for startup and first api call.
        res = this._dottedConstants("", val);
      }
      return _.flattenDeep(res); // removes order ?
    },
  },

  mounted() {
    if (this.url) {
      console.log("Getting constants on ", this.url);
      axios.get(this.url).then(result => {
        const data = result.data;
        this.constants = data;
        // console.log("Got types: ", res.types);
        this.types = data.types;
        delete this.constants.types;
      });
    }

    // Get types.
    if (this.urltypes) {
      axios.get(this.urltypes).then(result => {
        const data = result;
        this.types = data;
      });
    }
  },

  methods: {
    showVal(val, type) {
      // In case of rich text, show a truncated text version.
      const LENGTH_MAX = 800;
      if (type === "HTML") {
        return val.replace(/(<([^>]+)>)/g, "").slice(0, LENGTH_MAX) + "...";
      }
      return val;
    },

    isObj(arg) {
      return _.isPlainObject(arg);
    },

    isList(arg) {
      return _.isArray(arg);
    },

    _dottedConstants(key, val) {
      let types = this.types;
      if (this.isObj(val)) {
        let data = _.toPairs(val);

        let resArray = [];
        for (let i = 0; i < data.length; i++) {
          let prefix = key;
          if (key !== "") {
            prefix = prefix + ".";
          }
          prefix = prefix + data[i][0];
          let res = this._dottedConstants(prefix, data[i][1]);
          resArray.push(res);
        }
        return resArray;
      }

      let res = {
        key: key,
        val: val,
      };

      // If we have a type specified.
      if (typeof types[key] !== "undefined") {
        res.type = types[key];
      }

      return res;
    },

    entries() {
      // Quickfilter.
      const entries = this.dottedConstants;
      const filterKey = this.filterKey; // needed for the arrow function context.

      if (filterKey === "") {
        return entries;
      }

      function keep(it) {
        const content = it.key.toLowerCase();
        return content.indexOf(filterKey) !== -1;
      }

      return _.filter(entries, keep);
    },

    updateObject(obj, dottedKey, val) {
      // Update this object in place from path "dottedKey".
      // Return the updated object.
      // update object in place, from a path.
      const place = _.get(obj, dottedKey);
      if (place.hasOwnProperty("type")) {
        dottedKey += ".val";
      }
      return _.set(obj, dottedKey, val);
    },

    notify(key, msg, status) {
      const h = this.$createElement;
      let options;
      if (status === "success") {
        options = { style: "color: green" };
      } else if (status === "error") {
        options = { style: "color: red" };
      }
      Notification({
        title: msg,
        message: h("i", options, key),
      });
    },

    save(obj) {
      // Change the constants of this key and api call.
      let constants = this.constants;

      if (obj.val === "") {
        return;
      }

      // Access our property.
      const dottedKey = obj.key;
      let res = this.updateObject(constants, dottedKey, obj.val);
      if (typeof res !== "undefined") {
        // api call.
        $.ajax({
          url: "/admin2/constants/save",
          context: this,
          type: "POST",
          data: JSON.stringify(res),
          contentType: "application/json",
          success: function(result) {
            this.notify(obj.key, "Mise à jour effectuée", "success");
          },
          error: function(result) {
            console.log("---- api failed: ", result);
            this.notify(
              obj.key,
              "Attention, la mise à jour a échouée",
              "error"
            );
          },
        });
      }
    },
  },
};
</script>
