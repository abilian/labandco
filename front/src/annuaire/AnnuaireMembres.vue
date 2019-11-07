<template>
  <div>
    <h3>Annuaire des membres ({{ first }} - {{ last }} sur {{ total }})</h3>

    <div class="box-tools" style="margin-top: 2em;">
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

      <div class="input-group input-group-sm float-right" style="width: 250px;">
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

      <div>
        Afficher les membres des sous-structures?
        <input v-model="includeSS" type="checkbox" />
      </div>
    </div>

    <!-- <div class="box-body table-responsive"> -->
    <table class="table table-hover">
      <thead>
        <tr>
          <th width="20%">
            Nom
          </th>
          <th width="20%">
            Prénom
          </th>

          <th width="30%">
            Département
          </th>
          <th width="30%">
            Équipe
          </th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="entry in paginatedEntries">
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
            <a v-if="entry.departement" :href="entry.url">
              {{ entry.departement.name }}
            </a>
          </td>
          <td>
            <a v-if="entry.equipe" :href="entry.url">
              {{ entry.equipe.name }}
            </a>
          </td>
        </tr>
      </tbody>
    </table>

    <ul class="pagination float-right">
      <li>
        <a href="#" @click.prevent="previous_page()"> « </a>
      </li>
      <li>
        <a href="#">{{ page }} / {{ pageCount }} </a>
      </li>
      <li>
        <a href="#" @click.prevent="next_page()"> » </a>
      </li>
    </ul>
  </div>
</template>

<script>
import _ from "lodash";

const PAGE_SIZE = 50;

export default {
  name: "AnnuaireMembres",

  props: {
    role: String,
    admin: Boolean,
  },

  data() {
    return {
      // eslint-disable-next-line no-undef
      entries: DATA.entries,
      // eslint-disable-next-line no-undef
      total: DATA.entries.length,
      //
      filterKey: "",
      includeSS: true,
      //
      page: 1,
      pageCount: 1,
      count: 0,
      first: 1,
      last: 1,
      paginatedEntries: [],
    };
  },

  watch: {
    filterKey() {
      this.page = 1;
      this.update();
    },
    includeSS() {
      this.page = 1;
      this.update();
    },
  },

  mounted() {
    this.$nextTick(function() {
      this.update();
    });
  },

  methods: {
    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },

    update() {
      const filterKey = this.filterKey.toLowerCase();
      const includeSS = this.includeSS;

      function keep(it) {
        if (!includeSS && !it.membre_direct) {
          return false;
        }
        const content = it.nom.toLowerCase();
        return content.indexOf(filterKey) !== -1;
      }

      // eslint-disable-next-line no-undef
      this.entries = _.filter(DATA.entries, keep);
      this.count = this.entries.length;

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
  },
};
</script>
