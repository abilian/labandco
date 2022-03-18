<template>
  <div class="box">
    <div class="box-header with-border">
      <h3 class="box-title">
        Annuaire des structures ({{ first }} - {{ last }} sur {{ total }})
      </h3>

      <div class="box-tools">
        <ul
          class="pagination pagination-sm float-right"
          style="margin: 0 0 0 4em"
        >
          <li>
            <a href="#" @click.prevent="previous_page()"> « </a>
          </li>
          <li>
            <a href="#"> {{ page }} / {{ pageCount }} </a>
          </li>
          <li>
            <a href="#" @click.prevent="next_page()"> » </a>
          </li>
        </ul>

        <div class="input-group input-group-sm" style="width: 250px">
          <input
            v-model="filterKey"
            type="text"
            name="table_search"
            class="form-control float-right"
            placeholder="Filtrer"
          />

          <div class="input-group-btn">
            <button type="submit" class="btn btn-default">
              <i class="far fa-search" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="box-body table-responsive">
      <table class="table table-hover">
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
              {{ "+&nbsp;&nbsp;".repeat(entry.level)
              }}<a :href="entry.url">
                {{ entry.nom }}
              </a>
            </td>
            <td>{{ entry.sigle }}</td>
            <td>{{ entry.type }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="box-footer clearfix">
      <ul class="pagination float-right">
        <li>
          <a href="#" @click.prevent="previous_page()"> « </a>
        </li>
        <li>
          <a href="#"> {{ page }} / {{ pageCount }} </a>
        </li>
        <li>
          <a href="#" @click.prevent="next_page()"> » </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import _ from "lodash";

const PAGE_SIZE = 50;

export default {
  name: "Structures",

  props: {
    role: String,
    admin: Boolean,
  },

  data() {
    return {
      // eslint-disable-next-line no-undef
      entries: DATA.entries,
      // Total number of entries
      // eslint-disable-next-line no-undef
      total: DATA.entries.length,
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

  mounted() {
    this.$nextTick(function () {
      this.update();
    });
  },

  methods: {
    sleep(ms) {
      return new Promise((resolve) => setTimeout(resolve, ms));
    },

    update() {
      // filtering
      const filterKey = this.filterKey.toLowerCase();

      function keep(it) {
        const content = it.nom.toLowerCase() + it.sigle.toLowerCase();
        return content.indexOf(filterKey) !== -1;
      }

      // eslint-disable-next-line no-undef
      this.entries = _.filter(DATA.entries, keep);
      this.count = this.entries.length;

      // Pagination
      this.pageCount = Math.ceil(this.count / PAGE_SIZE);
      this.first = PAGE_SIZE * (this.page - 1) + 1;
      this.last = _.min([PAGE_SIZE * this.page, this.count]);
      this.paginatedEntries = this.entries.slice(
        PAGE_SIZE * (this.page - 1),
        PAGE_SIZE * this.page
      );
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
