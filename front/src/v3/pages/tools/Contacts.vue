<template>
  <div>
    <breadcrumbs title="Contacts Lab &amp; Co"></breadcrumbs>

    <div class="card">
      <div class="card-header with-border">
        <h3 class="card-title">Contacts Lab&amp;Co</h3>
      </div>

      <div class="card-body">
        <b-container class="mt-4 mb-0">
          <b-row>
            <b-col lg="6" class="my-1">
              <b-form-group
                label="Filtrer"
                label-cols-sm="3"
                label-align-sm="right"
                label-size="sm"
                label-for="filterInput"
                class="mb-0"
              >
                <b-input-group size="sm">
                  <b-form-input
                    v-model="filter"
                    type="search"
                    id="filterInput"
                  ></b-form-input>
                  <b-input-group-append>
                    <b-button :disabled="!filter" @click="filter = ''"
                      >Effacer</b-button
                    >
                  </b-input-group-append>
                </b-input-group>
              </b-form-group>
            </b-col>

            <b-col md="2"></b-col>

            <b-col md="4" class="my-1 text-right">
              <b-pagination
                v-model="currentPage"
                :total-rows="totalRows"
                :per-page="perPage"
                size="sm"
              ></b-pagination>
            </b-col>
          </b-row>
        </b-container>

        <b-table
          outlined
          id="table-contacts"
          show-empty
          responsive="md"
          hover
          :items="provider"
          :fields="fields"
          :filter="filter"
          :no-provider-paging="true"
          :no-provider-filtering="true"
          :current-page="currentPage"
          :per-page="perPage"
          @filtered="onFiltered"
        >
          <template v-slot:table-colgroup="scope">
            <col class="w-50" />
            <col class="w-50" />
          </template>

          <template v-slot:cell(structure)="row">
            <router-link
              :to="{ name: 'structure', params: { id: row.item.structure.id } }"
            >
              {{ row.item.structure.type }}:
              {{ row.item.structure.name }}
              <span v-if="row.item.structure.sigle"
                >({{ row.item.structure.sigle }})</span
              >
            </router-link>
          </template>

          <template v-slot:cell(contacts)="row">
            <table class="table mb-0">
              <template v-for="contact in row.item.contacts">
                <tr v-if="contact.id">
                  <td class="w-50">{{ contact.type_value }}</td>
                  <td class="w-50">
                    <router-link
                      :to="{ name: 'user', params: { id: contact.id } }"
                      >{{ contact.name }}
                    </router-link>
                  </td>
                </tr>
              </template>
            </table>
          </template>

          <template v-slot:table-busy>
            <div class="text-center my-2">
              <b-spinner class="align-middle"></b-spinner>
              <strong>Chargement en cours...</strong>
            </div>
          </template>
        </b-table>

        <b-container>
          <b-row class="text-right">
            <b-col md="8" class="my-1"> </b-col>
            <b-col md="4" class="my-1">
              <b-pagination
                v-model="currentPage"
                :total-rows="totalRows"
                :per-page="perPage"
              ></b-pagination>
            </b-col>
          </b-row>
        </b-container>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      fields: ["Structure", "Contacts"],
      filter: "",
      totalRows: 1,
      currentPage: 1,
      perPage: 10,
    };
  },

  methods: {
    provider(ctx, callback) {
      this.$root.rpc("get_all_contacts", []).then(result => {
        this.totalRows = result.length;
        callback(result);
      });
    },

    onFiltered(filteredItems) {
      // Trigger pagination to update the number of buttons/pages due to filtering
      this.totalRows = filteredItems.length;
      this.currentPage = 1;
    },
  },
};
</script>
