<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title mt-1">
        {{ title }} ({{ entries_length }} / {{ total }})
      </h3>

      <div class="card-tools">
        <form class="form-inline ml-3 mt-1">
          <div class="input-group input-group-sm">
            <input
              v-model="filterKey"
              type="text"
              name="table_search"
              class="form-control"
              placeholder="Filtrer"
              aria-label="Filtrer"
            />

            <div class="input-group-append">
              <button class="btn btn-default" type="submit">
                <i class="far fa-search" />
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <div class="card-body scrollable-container p-0">
      <table v-if="ready" class="table table-hover">
        <thead>
          <tr>
            <th
              v-for="col in columns"
              :id="col.id"
              style="overflow: hidden; white-space: nowrap;"
            >
              <span v-if="col.__show__">
                {{ col.label }}

                <span
                  :class="{ 'far fa-filter': hasFilter(col.id) }"
                  style="font-size: 9px; color: orange"
                />

                <span v-if="showSorting(col.id) === 1">
                  <span class="far fa-sort-down" />
                </span>
                <span v-else-if="showSorting(col.id) === 0">
                  <span class="far fa-sort-up" />
                </span>

                <ColSettings
                  :col-id="col.id"
                  :col-label="col.label"
                  :entries="data"
                  :col-filter="colFilter"
                  @sortRows="onSortRows"
                  @filterChanged="onFilterChanged"
                  @filterDeactivate="onFilterDeactivate"
                  @filterDeactivateAll="onFilterDeactivateAll"
                  @sortDeactivate="onSortDeactivate"
                />
              </span>
            </th>

            <th>
              <SelectColumns
                class="float-right"
                :columns="columns"
                style="font-weight: normal;"
                @columnsChanged="onColumnsChanged"
              />
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="entry in entries_page()">
            <td v-for="col in columns" :key="col.id" :href="entry[col.href]">
              <span v-if="col.__show__">
                <i
                  v-if="entry[col.class]"
                  :class="entry[col.class]"
                  :title="entry.type"
                />
                <a v-else-if="entry[col.href]" :href="entry[col.href]">
                  {{ entry[col.id] }}
                </a>
                <span v-else>
                  {{ entry[col.id] }}
                </span>
              </span>
            </td>
          </tr>
          <tr />
        </tbody>
      </table>

      <div v-else>Chargement en cours...</div>
    </div>

    <div class="card-footer">
      <slot name="footer-left" />

      <span v-if="dgrtt" class="col-md-4">
        <form class="form-inline">
          <div class="form-group">
            <div class="checkbox">
              <label>
                <input v-model="old" type="checkbox" @change="saveOld" />
                Demandes de plus de 3 mois
              </label>
            </div>
          </div>
        </form>
      </span>

      <slot name="footer-pagination">
        <span class="float-right">
          Éléments par page:
          <select
            v-model="pageCount"
            style="margin-right: 7px"
            @change="pageCountChanged"
          >
            <option :value="{ number: 5 }">
              5
            </option>
            <option :value="{ number: 10 }">
              10
            </option>
            <option :value="{ number: 15 }">
              15
            </option>
            <option :value="{ number: 20 }">
              20
            </option>
          </select>

          <ul
            class="pagination pagination-sm float-right"
            style="text-align: center;"
          >
            <li class="page-item">
              <a @click="firstPage()" class="page-link">
                <span class="far fa-fast-backward" />
              </a>
            </li>
            <li class="page-item">
              <a @click="previousPage()" class="page-link">
                <span class="far fa-step-backward" />
              </a>
            </li>
            <li class="page-item">
              <a href="#" class="page-link"> {{ page }} / {{ pageMax }} </a>
            </li>
            <li class="page-item">
              <a @click="nextPage()" class="page-link">
                <span class="far fa-step-forward" />
              </a>
            </li>
            <li class="page-item">
              <a @click="lastPage()" class="page-link">
                <span class="far fa-fast-forward" />
              </a>
            </li>
          </ul>
        </span>
      </slot>
    </div>
  </div>
</template>

<script>
import _ from "lodash";

import { tableStorage } from "../tableStorage/tableStorage";

import SelectColumns from "./select-columns.vue";
import ColSettings from "./col-settings.vue";

export default {
  name: "BoxDemandes",

  components: {
    SelectColumns,
    ColSettings,
  },

  props: {
    // unique id to save the component data in local storage.
    id: {
      type: String,
      required: true,
    },
    title: String,
    scope: String,
    archives: Boolean,
    dgrtt: {
      type: Boolean,
      default: false,
    },
  },

  data: function() {
    return {
      ready: false,

      old: false, // warn: for table_dgrtt
      data: [],
      entries_length: 0,
      filterKey: "",
      colFilter: {}, // for each column id, store its selected filter values.
      // Shall we include the null values ? for each column, use a boolean stored as
      // '__nulls__' into the colFilter[colId] list.
      colOrders: [], // remember the order of application of columns ordering.
      lastColSorted: undefined, // id of the last column we sorted, to show the sort icon.
      columnSelection: [], // for each column, boolean if selected or not. Another property in order to put on watcher on columns.
      columnsChanged: false, // were they changed by the modale ?
      showFilters: false, // hide/show all filters
      pageCount: { number: 5 },
      page: 1,
      // stupid version number to know if we need to clear the local
      // storage (and we need to after code changes).
      version: 9,

      defaultColumns: [
        { id: "created_at", label: "Date création" },
        {
          id: "type",
          label: "Type",
          class: "icon_class",
          sort_key: "type",
        },
        { id: "nom", label: "Intitulé", href: "url", sort_key: "nom" },
        { id: "date_debut", label: "Date début", sort_key: "date_debut" },
        {
          id: "date_soumission",
          label: "Date soumission",
          sort_key: "date_soumission",
        },
        {
          id: "porteur_nom",
          label: "Porteur",
          href: "porteur_url",
          sort_key: "porteur_nom",
        },
        {
          id: "gestionnaire_nom",
          label: "Gestionnaire",
          href: "gestionnaire_url",
          sort_key: "gestionnaire_nom",
        },
        {
          id: "no_infolab",
          label: "N° infolab",
          sort_key: "no_infolab",
        },
        {
          id: "laboratoire",
          label: "Structure",
          href: "laboratoire_url",
          sort_key: "laboratoire",
        },
        {
          id: "contact_dgrtt_nom",
          label: "Contact",
          href: "contact_dgrtt_url",
          sort_key: "contact_dgrtt_nom",
        },
        {
          id: "prochaine_action",
          label: "Prochaine action",
          sort_key: "prochaine_action",
        },
        {
          id: "owner",
          label: "Par",
          href: "contact_dgrtt_url",
          sort_key: "contact_dgrtt_nom",
        },
      ],
    };
  },

  computed: {
    columns() {
      let columns = [];
      // Get a previous order of columns.
      if (tableStorage.isDefined()) {
        let storedColumns = tableStorage.get(this.id, "columns");
        if (storedColumns && storedColumns !== null) {
          // This binding doesn't replicate to the child component
          // SelectColumns, so we'll also read the local storage
          // there.
          columns = storedColumns;
        } else {
          // Init new property. Using "hidden" and the existence
          // of this property would not be natural.
          columns = this.defaultColumns;
          if (this.dgrtt) {
            columns = columns.concat({
              id: "etat",
              label: "État",
              sort_key: "etat",
            });
          }

          columns.forEach(col => {
            col.__show__ = true;
          });
        }

        // Show only selected columns.
        if (this.columnsChanged) {
          columns = this.columnSelection;
          this.columnsChanged = false;
        }

        // Sort columns in order.
        if (tableStorage.get(this.id, "colOrders")) {
          this.colOrders = tableStorage.get(this.id, "colOrders");
          this.colOrders.forEach(it => {
            this.sortRows(it.id, this.defaultColumns, it.order);
          });
        }

        // Make colFilter[key] reactive for each column.
        if (columns.length > 0) {
          if (typeof this.colFilter === "undefined" || this.colFilter === {}) {
            columns.forEach(col => {
              this.$set(this.colFilter, col.id, "");
            });
          }
        }
      }

      return columns;
    },

    total() {
      if (typeof this.data !== "undefined") {
        return this.data.length;
      }
      return 0;
    },

    pageMax() {
      // Get the nb of pages. 16 elements / 3 elts per page = 5.xx, 16%3 = 1 --> 6 pages.
      function add_one_page(entries_length, page_count) {
        if (entries_length % page_count === 0) {
          return 0;
        }
        return 1;
      }

      return (
        Math.floor(this.entries_length / this.pageCount.number) +
        add_one_page(this.entries_length, this.pageCount.number)
      );
    },
  },

  mounted: function() {
    // Don't run the Ajax call when scope is not defined, this
    // makes it easier to test.
    if (!this.scope) {
      return;
    }

    const args = {
      scope: this.scope,
      archives: this.archives,
    };
    this.$root
      .rpc("get_demandes", args)
      .then(result => (this.data = result))
      .then(this.update)
      .then(() => (this.ready = true));
  },

  methods: {
    update() {
      if (tableStorage.isDefined()) {
        // Check this script version. If mismatch, clear the local storage.
        const version = JSON.parse(localStorage.getItem("version"));
        if (version && typeof version !== "undefined") {
          if (version && this.version !== version) {
            localStorage.clear();
            localStorage.setItem("version", JSON.stringify(this.version));
            alert(
              "Vos préférences de filtres ont dû être désactivées pour permettre une mise à jour logicielle."
            );
          }
        } else {
          localStorage.clear();
          localStorage.setItem("version", JSON.stringify(this.version));
        }
      }

      // Get pageCount, nb of elements per page.
      if (tableStorage.hasKey(this.id, "pageCount")) {
        this.pageCount = tableStorage.get(this.id, "pageCount");
      }

      // Show old entries > 3 months
      /* if (this.id && this.dgrtt && storage.old !== "undefined") { */
      if (this.id && this.dgrtt && tableStorage.hasKey(this.id, "old")) {
        this.old = tableStorage.get(this.id, "old");
      }

      // Get the filters for each column.
      this.colFilter = {}; // the declaration in data comes after.
      if (tableStorage.hasKey(this.id, "colFilter")) {
        this.colFilter = tableStorage.get(this.id, "colFilter");
      }

      if (tableStorage.hasKey(this.id, "colOrders")) {
        if (tableStorage.hasKey(this.id, "lastColSorted")) {
          this.lastColSorted = tableStorage.get(this.id, "lastColSorted");
        }
      }
    },

    // Called before the quickfilter, before the filter of all columns.
    preFilter: function(entries) {
      // this.old: show only older than 3 months.
      // otherwise: show all.
      if (this.old) {
        return _.filter(entries, e => (e.age >= 90 ? 1 : 0));
      } else {
        return entries;
      }
    },

    entries() {
      let filterKey = (this.filterKey || "").toLowerCase();

      function keep(e) {
        // for the quickfilter.
        let content = (
          e.porteur +
          " " +
          e.gestionnaire +
          " " +
          e.laboratoire +
          " " +
          e.contact_dgrtt +
          " " +
          e.no_infolab +
          " " +
          e.nom
        ).toLowerCase();
        return content.indexOf(filterKey) !== -1;
      }

      let entries = this.data;

      // For specific filter of a child element.
      if (typeof this.preFilter !== "undefined") {
        entries = this.preFilter(entries);
      }

      // Quickfilter.
      if (filterKey !== "") {
        entries = _.filter(entries, keep);
      }

      // Columns filters.
      let filterPairs = [];
      if (typeof this.colFilter !== "undefined") {
        filterPairs = _.toPairs(this.colFilter);
      }

      for (let i = 0; i < filterPairs.length; i++) {
        let filterColId = filterPairs[i][0];
        // filterValues: list of the user selection (str).
        let filterValues = filterPairs[i][1];
        if (filterValues !== "") {
          entries = _.filter(entries, row => {
            const content = row[filterColId];
            const keys = _.keys(filterValues);
            for (let i = 0; i < keys.length; i++) {
              if (content.indexOf(keys[i]) !== -1) {
                return true;
              }
              // Include also null values ?
              if (content === "" && keys.includes("__nulls__")) {
                return true;
              }
            }
            return false;
          });
        }
      }
      this.entries_length = entries.length;
      return entries;
    },

    entries_page() {
      return this.entries().slice(
        this.pageCount.number * (this.page - 1),
        this.pageCount.number * this.page
      );
    },

    previousPage: function() {
      if (this.page > 1) {
        this.page--;
      }
    },

    nextPage: function() {
      if (!this.entries()) {
        return 1;
      }
      if (this.page < this.pageMax) {
        this.page++;
        return this.entries().slice(
          this.pageCount.number * (this.page - 1),
          this.pageCount.number * 2 * this.page
        );
      }
    },

    firstPage: function() {
      this.page = 1;
    },

    lastPage: function() {
      this.page = this.pageMax;
    },

    onColumnsChanged: function(data) {
      this.columnSelection = data;
      this.columnsChanged = true;
      tableStorage.set(this.id, "columns", data);
      this.$forceUpdate();
    },

    sortIt: function(a, b, id, columns, order) {
      if (id === "created_at" || id === "__created_at__") {
        a = a.__created_at__;
        b = b.__created_at__;
      } else if (id === "date_debut" || id === "__date_debut__") {
        a = a.__date_debut__;
        b = b.__date_debut__;
      } else {
        // Sort with the id or an optional sort_key.
        const col = _.find(columns, it => it.id === id);
        if (typeof col === "undefined") {
          return 0;
        }
        const a_sort_key = a[col.sort_key];
        if (typeof a_sort_key !== "undefined") {
          a = a_sort_key.toUpperCase();
        } else {
          a = a[id].toUpperCase();
        }

        const b_sort_key = b[col.sort_key];
        if (typeof b_sort_key !== "undefined") {
          b = b_sort_key.toUpperCase();
        } else {
          b = b[id].toUpperCase();
        }
      }

      if (order === 0) {
        return a > b ? 1 : a < b ? -1 : 0;
      }
      if (order === 1) {
        return a < b ? 1 : a > b ? -1 : 0;
      }
    },

    sortRows: function(id, columns, order) {
      this.data.sort((a, b) => this.sortIt(a, b, id, columns, order));
    },

    onSortRows: function(id, order) {
      _.remove(this.colOrders, it => {
        return it.id === id;
      });
      this.sortRows(id, this.columns, order);
      this.colOrders.push({ id: id, order: order });
      tableStorage.set(this.id, "colOrders", this.colOrders);
      this.lastColSorted = id;
      tableStorage.set(this.id, "lastColSorted", id);
    },

    showSorting: function(id) {
      if (this.lastColSorted === id) {
        let col = _.find(this.colOrders, { id: id });
        if (col) {
          return col.order;
        }
      }
      return false;
    },

    onSortDeactivate: function(id, order) {
      const default_order_id = "__created_at__";
      const default_order_order = 0;
      this.colOrders = [];
      this.sortRows(default_order_id, this.defaultColumns, default_order_order);
      tableStorage.set(this.id, "colOrders", []);
    },

    onFilterDeactivate: function(id, filterValues) {
      delete this.colFilter[id]; // include everything, including rows that have null for this column.
      tableStorage.set(this.id, "colFilter", this.colFilter);
      this.$forceUpdate();
    },

    onFilterDeactivateAll: function() {
      // remove all column filters.
      this.colFilter = {};
      tableStorage.remove(this.id, "colFilter");
    },

    onFilterChanged: function(id, filterValues) {
      let selectedValues = _.pickBy(filterValues, (val, key) => {
        // yep, val first
        return val === true;
      });
      if (this.colFilter !== null) {
        this.colFilter[id] = selectedValues;
      }

      // Save for future sessions.
      tableStorage.set(this.id, "colFilter", this.colFilter);

      // vue won't update everything. Only way found:
      this.$forceUpdate();
    },

    pageCountChanged: function(id, filter) {
      tableStorage.set(this.id, "pageCount", this.pageCount);
    },

    saveOld: function() {
      tableStorage.set(this.id, "old", this.old);
      if (!navigator.userAgent.indexOf("Chrome")) {
        // FF needs it to toggle the checkbox, Chrome doesn't.
        tableStorage.set(this.id, "old", this.old);
        this.old = !this.old;
      }
    },

    hasFilter: function(colId) {
      // We have a filter if:
      // - colFilter for this column has no __all__ flag
      // - or no __nulls__ flag
      // (the object doesn't have the property or it is false).
      if (!this.colFilter.hasOwnProperty(colId)) {
        return false;
      }
      if (!this.colFilter[colId].hasOwnProperty("__all__")) {
        return true;
      }
      if (!this.colFilter[colId].hasOwnProperty("__nulls__")) {
        return true;
      }
      if (!this.colFilter[colId].__all__) {
        return true;
      }
      if (!this.colFilter[colId].__nulls__) {
        return true;
      }
      return false;
    },
  },
};
</script>

<style>
.scrollable-container {
  overflow: auto;
}
</style>
