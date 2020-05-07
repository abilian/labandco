<template>
  <div>
    <breadcrumbs title="Contacts Lab &amp; Co" />

    <div class="card">
      <div class="card-header with-border">
        <h3 class="card-title">Contacts Lab&amp;Co</h3>
      </div>

      <div v-if="ready && mes_contacts.length > 0" class="card-body">
        <h3>Structures dont je suis le contact Lab&amp;Co</h3>

        <table class="table mt-3 mb-3 table-striped table-bordered">
          <thead>
            <tr>
              <td>
                Structure
              </td>
              <td>Type de contact</td>
            </tr>
          </thead>
          <template v-for="d in mes_contacts">
            <tr>
              <td class="w-75">
                <router-link
                  :to="{ name: 'structure', params: { id: d.structure.id } }"
                >
                  {{ d.structure.type }}:
                  {{ d.structure.name }}
                  <span v-if="d.structure.sigle"
                    >({{ d.structure.sigle }})</span
                  >
                </router-link>
              </td>
              <td class="w-25">{{ d.bureau }}</td>
            </tr>
          </template>
        </table>
      </div>

      <div v-if="ready && structures.length > 0" class="card-body">
        <h3>Mes contacts Lab&amp;Co</h3>

        <div v-for="d in structures">
          <table class="table mt-3 mb-3 table-striped table-bordered">
            <thead>
              <tr>
                <td colspan="4" class="text-center">
                  {{ d.structure.type }}: {{ d.structure.name }}
                </td>
              </tr>
              <tr>
                <td>
                  Bureau
                </td>
                <td>Contact</td>
                <td>Email</td>
                <td>Telephone</td>
              </tr>
            </thead>
            <template v-for="contact in d.contacts">
              <tr v-if="contact.id">
                <td class="w-25">{{ contact.type_value }}</td>
                <td class="w-25">
                  <router-link
                    :to="{ name: 'user', params: { id: contact.id } }"
                    >{{ contact.name }}
                  </router-link>
                </td>
                <td class="w-40">
                  <a :href="`mailto:${contact.email}`">{{ contact.email }}</a>
                </td>
                <td class="w-10">{{ contact.tel }}</td>
              </tr>
            </template>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      ready: false,
      structures: [],
      mes_contacts: [],
    };
  },

  created() {
    this.$root.rpc("get_contacts_for_user").then(result => {
      this.structures = result.structures;
      this.mes_contacts = result.mes_contacts;
      this.ready = true;
    });
  },
};
</script>
