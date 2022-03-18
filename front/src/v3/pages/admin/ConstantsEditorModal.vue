<template>
  <div>
    <el-button type="text" @click="dialogVisible = true"> Edit </el-button>

    <el-dialog
      :title="title"
      :visible.sync="dialogVisible"
      :before-close="handleClose"
    >
      <form class="ui form" action="" @submit="save">
        <div class="field">
          <div v-if="datatype === 'HTML'">
            <quill-editor ref="myQuillEditor" v-model="newdata" />
          </div>

          <div v-else-if="datatype === 'str'">
            <ul>
              <li class="my-align">
                <input v-model.trim="newdata" type="text" size="48" />
              </li>
              <li class="my-align my-type">
                {{ types[datatype] }}
              </li>
            </ul>
          </div>

          <div v-else-if="datatype === 'int'">
            <ul>
              <li class="my-align">
                <input v-model.trim="newdata" type="number" />
              </li>
              <li class="my-align my-type">
                {{ types[datatype] }}
              </li>
            </ul>
          </div>

          <div v-else-if="datatype === 'float'">
            <ul>
              <li class="my-align">
                <input v-model.trim="newdata" type="number" step="0.001" />
              </li>
              <li class="my-align my-type">
                {{ types[datatype] }}
              </li>
            </ul>
          </div>

          <div v-else-if="datatype === 'list[list[str,int]]'">
            <p>
              Le format souhaité est une chaîne de caractères et un nombre
              entier, séparés par une virgule.
            </p>
            <textarea v-model.trim="listoflists" cols="80" rows="10" />
          </div>

          <div v-else-if="isList(data)">
            <p>Le format souhaité est une chaîne de caractères par ligne.</p>
            <textarea v-model.trim="listdata" cols="80" rows="10" />
          </div>
        </div>
      </form>

      <span slot="footer" class="dialog-footer">
        <el-button class="ui button" @click="cancel"> Cancel </el-button>
        <el-button class="ui button" type="primary" @click="save">
          Confirm
        </el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import _ from "lodash";

export default {
  name: "EditorModal",
  props: {
    data: {
      type: [Array, String, Number],
      required: true,
    },
    dottedKey: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: false,
    },
    type: {
      type: String,
      required: false,
    },
  },

  data() {
    return {
      dialogVisible: false,
      toret: "",
      types: {
        str: "Chaîne de caractères",
        int: "Nombre entier",
        float: "Nombre réel",
        boolean: "Booléen",
      },
    };
  },

  computed: {
    datatype() {
      return this.type;
    },

    newdata: {
      get() {
        if (!this.toret) {
          return this.data;
        }
        return this.toret;
      },

      set(val) {
        let res = this.parseType(val);
        if (res && res !== this.data) {
          this.toret = res;
        }
      },
    },

    listdata: {
      get() {
        return _.join(this.data, "\n");
      },

      set(entry) {
        // Back to a list of strings (to begin with).
        if (this.listdata === entry) {
          this.toret = "";
        } else {
          let split = entry.split("\n");
          let val = [];
          for (let i = 0; i < split.length; i++) {
            val.push(split[i]);
          }
          this.toret = val;
        }
      },
    },

    listoflists: {
      get() {
        // to CSV lines.
        return _.join(this.data, "\n");
      },

      set(entry) {
        // Back to a list of lists with a string and an int or a float.
        let ok = true;
        this.toret = "";
        if (this.listoflists !== entry) {
          let split = entry.split("\n");
          let val = [];
          for (let i = 0; i < split.length; i++) {
            let innerVal = [];
            let strNb = split[i].split(",");
            let theNb;
            // xxx Validation.
            // xxx Read the type.
            if (strNb.length >= 2 && strNb[1].indexOf(".") !== -1) {
              // xxx parsing "10.xx" works and returns 10, and should not.
              theNb = parseFloat(strNb[1]);
            } else {
              theNb = parseInt(strNb[1]);
            }
            if (isNaN(theNb)) {
              this.notifyWarning(
                "Attention, '" + strNb[1] + "' n'est pas un nombre entier."
              );
              ok = false;
            } else {
              innerVal.push(strNb[0]); // the string
              innerVal.push(theNb); // the int
              val.push(innerVal);
            }
          }
          if (ok) {
            this.toret = val;
          }
        }
      },
    },
  },

  methods: {
    isList(arg) {
      return _.isArray(arg);
    },

    parseType(arg) {
      if (this.datatype === "int") {
        if (arg.indexOf(".") !== -1 || arg.indexOf(",") !== -1) {
          this.notifyWarning("Attention, veuillez entrer un nombre entier.");
          return;
        }
        let res = parseInt(arg);
        // Validation.
        if (isNaN(res)) {
          this.notifyWarning("Attention, veuillez entrer un nombre entier.");
          return;
        }
        return res;
      } else if (this.datatype === "float") {
        let res = parseFloat(arg);
        if (isNaN(res)) {
          this.notifyWarning("Attention, veuillez entrer un nombre réel.");
          return;
        }
        return res;
      }
      return arg;
    },

    handleClose(done) {
      done();
    },

    cancel(e) {
      e.preventDefault();
      this.dialogVisible = false;
      this.toret = this.data;
    },

    save(e) {
      e.preventDefault();
      console.log("--- Updating ", this.dottedKey, " to ", this.toret);
      if (this.toret !== "") {
        this.$emit("save", { key: this.dottedKey, val: this.toret });
      }
      this.dialogVisible = false;
    },

    notifyWarning(msg) {
      const h = this.$createElement;
      Notification({
        title: msg,
        message: h("i"),
      });
    },
  },
};
</script>

<style>
.my-align {
  overflow: hidden;
  float: left;
}

.my-type {
  margin-left: 1em;
}
</style>
