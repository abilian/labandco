<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title">
        Annuaire des structures ({{ first }} - {{ last }} sur {{ total }})
      </h3>

      <div class="card-tools">
        <ul
          class="pagination pagination-sm float-right"
          style="margin: 0 0 0 4em"
        >
          <li class="page-item">
            <a href="#" @click.prevent="previous_page()" class="page-link">
              «
            </a>
          </li>
          <li class="page-item">
            <span class="page-link"> {{ page }} / {{ pageCount }} </span>
          </li>
          <li class="page-item">
            <a href="#" @click.prevent="next_page()" class="page-link"> » </a>
          </li>
        </ul>

        <form class="form-inline ml-3 mt-1">
          <span class="input-group input-group-sm">
            <input
              v-model="filterKey"
              type="text"
              name="table_search"
              class="form-control"
              placeholder="Filtrer"
              aria-label="Filtrer"
            />

            <span class="input-group-append">
              <button class="btn btn-default" type="submit">
                <i class="far fa-search" />
              </button>
            </span>
          </span>
        </form>
      </div>
    </div>

    <div v-if="ready" class="card-body table-responsive p-0">
      <table class="table table-condensed table-hover">
        <thead>
          <tr>
            <th width="60%">Nom</th>
            <th width="20%">Sigle</th>
            <th width="20%">Type</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="entry in paginatedEntries" :style="style(entry)">
            <td>
              {{ "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;".repeat(entry.level) }}
              <a
                v-if="entry.hasChildren && entry.isOpen"
                @click.prevent="toggle(entry)"
                href="#"
              >
                <i class="far fa-minus-square"></i>&nbsp;
              </a>
              <a
                v-if="entry.hasChildren && !entry.isOpen"
                @click.prevent="toggle(entry)"
                href="#"
              >
                <i class="far fa-plus-square"></i>&nbsp;
              </a>
              <router-link
                :to="{ name: 'structure', params: { id: entry.id } }"
                >{{ entry.nom }}</router-link
              >
            </td>
            <td>{{ entry.sigle }}</td>
            <td>{{ entry.type }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="card-body table-responsive p-3">
      Chargement en cours...
    </div>

    <div class="card-footer clearfix">
      <ul class="pagination float-right">
        <li>
          <a href="#" @click.prevent="previous_page()" class="page-link"> « </a>
        </li>
        <li>
          <span class="page-link"> {{ page }} / {{ pageCount }} </span>
        </li>
        <li>
          <a href="#" @click.prevent="next_page()" class="page-link"> » </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import _ from "lodash";

const PAGE_SIZE = 50;

export default {
  name: "TableStructures",

  props: {
    url: String,
  },

  data() {
    return {
      ready: false,

      entries: [],
      // Total number of entries
      total: 0,
      // Filtering
      filterKey: "",
      // Number of entries currently filtered
      count: 0,

      // Pagination
      paginatedEntries: [],
      // Page number
      page: 1,
      // Number of pages
      pageCount: 0,
      first: 0,
      last: 0,
    };
  },

  watch: {
    filterKey() {
      this.page = 1;
      this.update();
    },
  },

  created() {
    this.$root.rpc("sg_all_structures", []).then((result) => {
      this.all_entries = result;
      if (localStorage.cache_structures) {
        this.restoreTree();
      } else {
        this.resetTree();
      }
      this.update();
      this.ready = true;
    });
  },

  methods: {
    resetTree() {
      for (let entry of this.all_entries) {
        if (entry.level === 0) {
          entry.isOpen = true;
          entry.isVisible = true;
        } else if (entry.level === 1) {
          entry.isOpen = false;
          entry.isVisible = true;
        } else {
          entry.isOpen = false;
          entry.isVisible = false;
        }
        entry.hasChildren = entry.children_ids.length > 0;
      }
    },

    restoreTree() {
      const cache = JSON.parse(localStorage.cache_structures);
      for (let entry of this.all_entries) {
        const c = cache[entry.id];
        if (c) {
          entry.isOpen = c.isOpen;
          entry.isVisible = c.isVisible;
        } else {
          entry.isOpen = false;
          entry.isVisible = false;
        }
        entry.hasChildren = entry.children_ids.length > 0;
      }
      this.all_entries[0].isVisible = true;
    },

    saveTree() {
      const cache = {};
      for (let entry of this.all_entries) {
        cache[entry.id] = { isOpen: entry.isOpen, isVisible: entry.isVisible };
      }
      localStorage.cache_structures = JSON.stringify(cache);
    },

    update() {
      // filtering
      const filterKey = this.filterKey.toLowerCase();

      function keep(entry) {
        if (!filterKey && !entry.isVisible) {
          return false;
        }
        const content = entry.nom.toLowerCase() + entry.sigle.toLowerCase();
        return content.indexOf(filterKey) !== -1;
      }

      this.entries = _.filter(this.all_entries, keep);
      this.count = this.entries.length;

      // Pagination
      this.pageCount = Math.ceil(this.count / PAGE_SIZE);
      this.first = PAGE_SIZE * (this.page - 1) + 1;
      this.last = _.min([PAGE_SIZE * this.page, this.count]);
      this.paginatedEntries = this.entries.slice(
        PAGE_SIZE * (this.page - 1),
        PAGE_SIZE * this.page
      );

      this.saveTree();
    },

    next_page() {
      if (this.page < this.pageCount) {
        this.page++;
      }
      this.update();
    },

    previous_page() {
      if (this.page > 1) {
        this.page--;
      }
      this.update();
    },

    style(entry) {
      return "background-color: " + STYLES[entry.level] + ";";
    },

    indent(entry) {
      return { width: `${entry.level * 2}rem` };
    },

    toggle(entry) {
      entry.isOpen = !entry.isOpen;
      const all_entries = this.all_entries;

      function closeChildren(entry) {
        for (let child_id of entry.children_ids) {
          for (let entry2 of all_entries) {
            if (entry2.id === child_id) {
              entry2.isVisible = false;
              closeChildren(entry2);
            }
          }
        }
      }

      if (entry.isOpen) {
        for (let child_id of entry.children_ids) {
          for (let entry2 of all_entries) {
            if (entry2.id === child_id) {
              entry2.isVisible = true;
            }
          }
        }
      } else {
        closeChildren(entry);
      }

      this.update();
    },
  },
};

const STYLES = {
  0: "#fff",
  1: "#f8f8f8",
  2: "#efefef",
  3: "#e8e8e8",
  4: "#dfdfdf",
  5: "#d8d8d8",
  6: "#cfcfcf",
};
</script>
