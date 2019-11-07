<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title">{{ title }} ({{ count }} de {{ total }})</h3>

      <div class="card-tools">
        <ul
          class="pagination pagination-sm float-right"
          style="margin: 0 0 0 4em;"
        >
          <li class="page-item">
            <a href="#" @click.prevent="previous_page()" class="page-link">
              «
            </a>
          </li>
          <li class="page-item">
            <a href="#" class="page-link">
              {{ page }}
            </a>
          </li>
          <li class="page-item">
            <a href="#" @click.prevent="next_page()" class="page-link">
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

    <div class="card-body table-responsive">
      <table class="table table-hover">
        <thead>
          <tr>
            <th width="65%">
              Nom
            </th>
            <th width="15%">
              Sigle
            </th>
            <th width="15%">
              Type
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
                {{ entry.sigle }}
              </a>
            </td>
            <td>{{ entry.type }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="card-footer clearfix">
      <ul class="pagination float-right">
        <li>
          <a href="#" @click.prevent="previous_page()">
            «
          </a>
        </li>
        <li>
          <a href="#">
            {{ page }}
          </a>
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
import axios from "axios";

export default {
  name: "BoxOrgs",

  props: {
    title: String,
    url: String,
    admin: Boolean,
  },

  data: function() {
    return {
      data: [],
      page: 0,
      count: 0,
      total: 0,
      filterKey: "",
    };
  },

  watch: {
    filterKey: function() {
      this.update();
    },
  },

  mounted: function() {
    this.$nextTick(function() {
      this.page = 0;
      this.update();
    });
  },

  methods: {
    sleep: function(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },

    update: async function() {
      // We currently fire this ajax call at each keypress.
      // On prod, it lags, the filter doesn't work. The calls are made in order, but
      // eventually the full api search is displayed, not the filtered one.
      // Waiting a bit gives more chance to the api calls to be populated
      // with the full filterKey
      // (as a result, typing "lov" quickly, we get three calls with "lov").
      await this.sleep(400);
      const that = this;
      let url = this.url + "?page=" + this.page;
      if (this.filterKey) {
        url = url + "&q=" + this.filterKey;
      }
      if (this.admin) {
        url = url + "&admin=true";
      }

      axios.get(url).then(result => {
        const data = result.data;
        that.data = data["orgs"];
        that.total = data["total"];
        if (that.data) {
          that.count = that.data.length;
        } else {
          that.count = 0;
        }
      });
    },

    next_page: function() {
      this.page++;
      this.update();
    },

    previous_page: function() {
      if (this.page > 0) {
        this.page--;
      }
      this.update();
    },
  },
};
</script>
