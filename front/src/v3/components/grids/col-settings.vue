<template>
  <span>
    <span
      class="far fa-chevron-down"
      style="cursor: pointer;"
      aria-hidden="true"
      @click="showModal = true"
    />

    <modal v-if="showModal" @close="showModal = false">
      <!--
        you can use custom content here to overwrite
        default content. (use slot="header/body/footer")
      -->
      <div slot="header">
        <h3>Trier et Filtrer</h3>
        <h4>{{ colLabel }}</h4>
      </div>

      <div slot="body">
        <div>
          <em>
            Choisissez un ordre de tri pour cette colonne. Il sera préservé pour
            votre prochaine connexion.
          </em>

          <div>
            <br />
            <div>
              <span>
                <button
                  type="button"
                  :class="{
                    'btn btn-default glyphicon glyphicon-sort-by-alphabet': true,
                    active: sort_order === 0,
                  }"
                  @click="sortRows(0)"
                >
                  Croissant
                </button>
              </span>
              <span>
                <button
                  type="button"
                  :class="{
                    'btn btn-default glyphicon glyphicon-sort-by-alphabet-alt': true,
                    active: sort_order === 1,
                  }"
                  @click="sortRows(1)"
                >
                  Décroissant
                </button>
              </span>
            </div>
            <button
              type="submit"
              class="btn btn-default btn-sm"
              style="margin-top: 20px; margin-bottom: 20px"
              title="Trier par date de création."
              @click="sortDeactivate"
            >
              Annuler
            </button>
          </div>

          <br />
          <div class="scrollbar">
            <em style="">
              Filtrez sur cette colonne.
            </em>

            <div>
              <label class="checkbox-inline">
                <input
                  id="selectAll"
                  v-model="selectAll"
                  type="checkbox"
                  @change="selectAllToggle"
                />
                Tout sélectionner
              </label>
            </div>
            <div v-if="hasNulls">
              <label class="checkbox-inline">
                <input
                  id="includeNulls"
                  v-model="includeNulls"
                  type="checkbox"
                  @change="toggleIncludeNulls"
                />
                Inclure valeurs vides
              </label>
            </div>
            <div
              v-for="val in colValues"
              style="background-color: whitesmoke; max-height: 20px"
            >
              <label class="checkbox-inline">
                <input
                  v-model="filterValues[val]"
                  type="checkbox"
                  :value="val"
                  @change="toggleInput"
                />
                {{ val | truncate }}
              </label>
            </div>
          </div>

          <button
            type="submit"
            class="btn btn-default btn-sm"
            style="margin-top: 20px; margin-bottom: 20px"
            title="Désactiver le filtre."
            @click="filterDeactivate"
          >
            Annuler
          </button>

          <button
            type="submit"
            class="btn btn-default btn-sm"
            style="margin-top: 20px; margin-bottom: 20px"
            title="Remettre à zéro tous les filtres de toutes les colonnes."
            @click="filterDeactivateAll"
          >
            Annuler tous
          </button>
        </div>
      </div>
    </modal>
  </span>
</template>

<script>
import _ from "lodash";
import Modal from "./modal.vue";

export default {
  name: "ColSettings",

  components: {
    Modal,
  },

  filters: {
    truncate: function(value) {
      const max_length = 40;
      if (!value) {
        return "";
      }
      if (value.length >= max_length) {
        return value.substring(0, max_length) + "...";
      }
      return value;
    },
  },

  props: [
    "colId",
    "colLabel",
    "entries",
    "colFilter", // For each column, the list of selected entries.
  ],

  data: function() {
    return {
      showModal: false,
      sort_order: undefined, // needed only to bind css classes.
      selectAll: true,
      includeNulls: true, // model for the template. Stored as __nulls__ in filterValues list.
      filterCounter: 0, // counting number of checked boxes, to help knowing if the column is filtered.
    };
  },

  computed: {
    colValues: function() {
      // Get all the possible values of this column.
      let values;
      // FIXME: make more generic
      // console.log(this.colId);
      if (this.colId === "created_at") {
        // Sort dates accurately with the timestamp (__created_at__),
        // but still return the human date (created_at).
        let sortedEntries = _.sortBy(this.entries, "__created_at__");
        values = _.map(sortedEntries, this.colId);
      } else if (this.colId === "date_debut") {
        let sortedEntries = _.sortBy(this.entries, "__date_debut__");
        values = _.map(sortedEntries, this.colId);
      } else {
        values = _.map(this.entries, this.colId);
        values = values.sort();
      }
      values = _.filter(values, it => it !== "");
      values = _.uniq(values);
      return values;
    },

    hasNulls: function() {
      // Hide the "include nulls" button if there is none of them.
      let values = _.map(this.entries, this.colId);
      return values.indexOf("") !== -1;
    },

    filterValues: function() {
      // Chosen values for the filter.
      // For each possible entrie, a boolean if the user selected it.
      let values = {};

      // get the selected values for this column.
      if (this.colFilter && this.colFilter[this.colId]) {
        values = this.colFilter[this.colId];
      } else {
        // init. Select all.
        for (let i = 0; i < this.colValues.length; i++) {
          values[this.colValues[i]] = true;
        }
      }

      // set selectAll button on re-opening the modale,
      // where it is possible this property is not set.
      if (!this.includeNulls) {
        return values;
      }
      for (let i = 0; i < this.colValues.length; i++) {
        if (values.hasOwnProperty(this.colValues[i])) {
          if (!values[this.colValues[i]]) {
            this.selectAll = false;
            values.__all__ = false;
            return values;
          }
        } else {
          this.selectAll = false;
          values.__all__ = false;
          return values;
        }
      }
      this.selectAll = true;
      values.__all__ = true;

      return values;
    },
  },

  methods: {
    sortRows: function(order) {
      this.sort_order = order;
      this.$emit("sortRows", this.colId, order);
    },

    sortDeactivate: function() {
      this.$emit("sortDeactivate");
    },

    setSelectAll: function() {
      // If all checkboxes are checked, including the nulls, we check the selectAll button.
      // Used when re-opening the modale and reading data in colFilter where selectAll can not be present.
      // caution: see same functionnality in filterValues computed property.
      if (!this.includeNulls) {
        return;
      }
      this.selectAll = true;
      this.filterValues.__all__ = true;
      for (let i = 0; i < this.colValues.length; i++) {
        if (this.filterValues.hasOwnProperty(this.colValues[i])) {
          if (!this.filterValues[this.colValues[i]]) {
            this.selectAll = false;
            this.filterValues.__all__ = false;
            return;
          }
        } else {
          this.selectAll = false;
          this.filterValues.__all__ = false;
          return;
        }
      }
    },

    toggleInput: function(e) {
      let val = e.target.value;
      const checked = e.target.checked;
      this.filterValues[val] = checked;

      // toggle selectAll button.
      if (checked) {
        // are all checkboxes checked ?
        this.setSelectAll();
      } else {
        // unchecking, so selectAll is false.
        this.selectAll = false;
        this.filterValues.__all__ = false;
      }

      this.$emit("filterChanged", this.colId, this.filterValues);
    },

    filterDeactivate: function() {
      // Deactivate the filter. Re-put null rows.
      this.doSelectAll();
      this.$emit("filterDeactivate", this.colId, this.filterValues);
    },

    filterDeactivateAll: function() {
      // Deacitate filters of all columns.
      this.doSelectAll();
      this.$emit("filterDeactivateAll");
      this.$emit("close");
    },

    doSelectAll: function() {
      for (let i = 0; i < this.colValues.length; i++) {
        let val = this.colValues[i];
        this.filterValues[val] = true;
      }
      this.filterValues.__nulls__ = true;
      this.includeNulls = true;
      this.filterValues.__all__ = true;
      this.selectAll = true;
    },

    selectAllToggle: function(e) {
      // Toggle the selection.
      let checked = e.target.checked;
      this.selectAll = checked;
      this.includeNulls = checked;
      this.filterValues.__all__ = checked;
      this.filterValues.__nulls__ = checked;
      // Here it can happen a mismatch between this.selectAll and this.filterValues.__all__
      // the first can be true and the other false.
      // doing
      // this.filterValues.__all__ = this.selectAll;
      // doesn't help.
      // console.log("selectAll: ", this.selectAll, " / __all__: ", this.filterValues.__all__); // bug, they're different.

      for (let i = 0; i < this.colValues.length; i++) {
        let val = this.colValues[i];
        if (checked) {
          this.filterValues[val] = true;
        } else {
          if (this.filterValues.hasOwnProperty(val)) {
            this.filterValues[val] = false;
          }
        }
      }

      this.$forceUpdate(); // needed for chrome apparently.
      this.$emit("filterChanged", this.colId, this.filterValues);
    },

    toggleIncludeNulls: function(e) {
      this.filterValues.__nulls__ = e.target.checked;
      if (!this.filterValues.__nulls__) {
        this.selectAll = false;
        this.filterValues.__all__ = false;
        delete this.filterValues.__nulls__;
      }
      // const colValues = this.colValues;
      if (this.filterCounter === 0) {
        if (
          this.filterValues.hasOwnProperty("__nulls__") &&
          this.filterValues.__nulls__ === true
        ) {
          // TODO This is not finished !
          console.log("Empty block in toggleIncludeNulls reached");
        }
      }
      this.$emit("filterChanged", this.colId, this.filterValues);
    },
  },
};
</script>
