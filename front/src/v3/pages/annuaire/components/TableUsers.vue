<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title">
        {{ title }} ({{ first }} - {{ last }} sur {{ total }})
      </h3>

      <div class="card-tools">
        <ul
          class="pagination pagination-sm float-right"
          style="margin: 0 0 0 4em;"
        >
          <li>
            <a href="#" @click.prevent="previous_page()" class="page-link">
              «
            </a>
          </li>
          <li>
            <a href="#" class="page-link"> {{ page }} / {{ pageCount }} </a>
          </li>
          <li>
            <a href="#" @click.prevent="next_page()" class="page-link">
              »
            </a>
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

        <!--        <div class="input-group input-group-sm" style="width: 250px;">-->
        <!--          <input-->
        <!--            v-model="filterKey"-->
        <!--            type="text"-->
        <!--            name="table_search"-->
        <!--            class="form-control pull-right"-->
        <!--            placeholder="Filtrer"-->
        <!--          />-->

        <!--          <div class="input-group-btn">-->
        <!--            <button type="submit" class="btn btn-default">-->
        <!--              <i class="far fa-search" />-->
        <!--            </button>-->
        <!--          </div>-->
        <!--        </div>-->
      </div>
    </div>

    <div v-if="ready" class="card-body table-responsive p-0">
      <table class="table table-hover">
        <thead>
          <tr>
            <th class="w-25">
              Nom
            </th>
            <th class="w-25">
              Prénom
            </th>
            <th class="w-50">
              Structure d'appartenance & rôle(s)
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="entry in data">
            <td>
              <router-link :to="{ name: 'user', params: { id: entry.id } }">{{
                entry.nom
              }}</router-link>
            </td>
            <td>
              <router-link :to="{ name: 'user', params: { id: entry.id } }">{{
                entry.prenom
              }}</router-link>
            </td>
            <td>
              <div v-for="structure in entry.structures">
                <router-link
                  :to="{ name: 'structure', params: { id: structure.id } }"
                  >{{ structure.name }}</router-link
                >
                ({{ structure.roles }})
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="card-body table-responsive p-2">
      Chargement en cours...
    </div>

    <div class="card-footer clearfix">
      <ul class="pagination float-right">
        <li>
          <a href="#" @click.prevent="previous_page()" class="page-link">
            «
          </a>
        </li>
        <li>
          <a href="#" class="page-link"> {{ page }} / {{ pageCount }} </a>
        </li>
        <li>
          <a href="#" @click.prevent="next_page()" class="page-link">
            »
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import _ from "lodash";

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
      ready: false,
      data: [],
      page: 1,
      count: 0,
      first: 0,
      last: 0,
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
      this.ready = false;

      const args = { page: this.page - 1 };
      if (this.filterKey) {
        args.q = this.filterKey;
      }

      this.$root.rpc("get_users", args).then(result => {
        this.data = result["users"];
        this.total = result["total"];
        if (this.data) {
          this.count = this.data.length;
        } else {
          this.count = 0;
        }
        this.pageCount = Math.ceil(this.total / PAGE_SIZE);
        this.first = (this.page - 1) * PAGE_SIZE + 1;
        this.last = _.min([this.page * PAGE_SIZE, this.total]);

        this.ready = true;
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
