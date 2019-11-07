<template>
  <div class="box">
    <div class="box-header with-border">
      <h3 class="box-title">
        {{ title }} ({{ first }} - {{ last }} sur {{ total }})
      </h3>

      <div class="box-tools">
        <ul
          class="pagination pagination-sm float-right"
          style="margin: 0 0 0 4em;"
        >
          <li>
            <a href="#" @click.prevent="previous_page()">
              «
            </a>
          </li>
          <li>
            <a href="#"> {{ page }} / {{ pageCount }} </a>
          </li>
          <li>
            <a href="#" @click.prevent="next_page()">
              »
            </a>
          </li>
        </ul>

        <div class="input-group input-group-sm" style="width: 250px;">
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
            <th width="20%">
              Nom
            </th>
            <th width="20%">
              Prénom
            </th>
            <th width="60%">
              Roles
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="entry in data">
            <td>
              <a :href="entry.url">
                {{ entry.nom }}
              </a>
            </td>
            <td>
              <a :href="entry.url">
                {{ entry.prenom }}
              </a>
            </td>
            <td>
              <div v-for="structure in entry.structures">
                <a :href="structure.url">
                  {{ structure.name }}
                </a>
                ({{ structure.roles }})
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="box-footer clearfix">
      <ul class="pagination float-right">
        <li>
          <a href="#" @click.prevent="previous_page()">
            «
          </a>
        </li>
        <li>
          <a href="#"> {{ page }} / {{ pageCount }} </a>
        </li>
        <li>
          <a href="#" @click.prevent="next_page()">
            »
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import _ from "lodash";
import axios from "axios";
// const axios = require("axios");

const PAGE_SIZE = 100;

export default {
  name: "TableUsers",

  props: {
    title: String,
    url: String,
    role: String,
    admin: Boolean,
  },

  data: function() {
    return {
      data: [],
      page: 1,
      count: 0,
      pageCount: 0,
      total: 0,
      filterKey: "",
    };
  },

  watch: {
    filterKey: function() {
      this.page = 1;
      this.update();
    },
  },

  mounted: function() {
    this.$nextTick(function() {
      this.update();
    });
  },

  methods: {
    sleep: function(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },

    update: async function() {
      // Why wait ? see table_orgs.vue
      await this.sleep(400);
      let url = this.url + "?page=" + (this.page - 1);
      if (this.filterKey) {
        url = url + "&q=" + this.filterKey;
      }
      axios.get(url).then(result => {
        const data = result.data;
        this.data = data["users"];
        this.total = data["total"];
        if (this.data) {
          this.count = this.data.length;
        } else {
          this.count = 0;
        }
        this.pageCount = Math.ceil(this.total / PAGE_SIZE);
        this.first = (this.page - 1) * PAGE_SIZE + 1;
        this.last = _.min([this.page * PAGE_SIZE, this.total]);
      });
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
  },
};
</script>
