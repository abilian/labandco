<template>
  <div v-if="ou">
    <div class="row mt-4">
      <div class="col-lg-3 text-bold">Structures parentes</div>

      <div v-if="ou" class="col-lg-9">
        <b-table-simple outlined striped condensed hover>
          <tr v-for="parent in ou.parents">
            <td>
              <router-link
                :to="{ name: 'structure', params: { id: parent.id } }"
                >{{ parent.nom }}
                <span v-if="parent.sigle">({{ parent.sigle }})</span>
              </router-link>
              [{{ parent.type }}]
            </td>

            <td style="text-align: right;">
              <button
                v-if="ou.permissions.P2"
                class="btn btn-danger btn-sm"
                @click="deleteEdge(parent.id, ou.id)"
              >
                <i class="far fa-times" />
              </button>
            </td>
          </tr>
        </b-table-simple>

        <div
          v-if="ou && ou.permissions.P2 && parentsOptions.length > 0"
          class="mb-4"
        >
          <b-button
            class="btn-default btn-sm"
            @click="$bvModal.show('add-parent')"
            ><i class="far fa-plus"
          /></b-button>

          <b-modal id="add-parent" hide-footer>
            <template v-slot:modal-title>
              Ajouter une structure parente
            </template>

            <div class="d-block">
              <h2>Choisir une structure</h2>

              <b-form-select
                v-model="parentSelected"
                :options="parentsOptions"
              />
            </div>

            <b-button class="mt-3" block @click="submitModal('add-parent')"
              >Valider
            </b-button>
          </b-modal>
        </div>
      </div>
    </div>

    <div class="row mt-4">
      <div class="col-lg-3 text-bold">Sous-structures</div>

      <div v-if="ou" class="col-lg-9">
        <b-table-simple outlined condensed striped hover>
          <tr v-for="child in ou.children">
            <td>
              <router-link :to="{ name: 'structure', params: { id: child.id } }"
                >{{ child.nom }}
                <span v-if="child.sigle">({{ child.sigle }})</span>
              </router-link>
              [{{ child.type }}]
            </td>

            <td style="text-align: right;">
              <button
                v-if="ou.permissions.P3"
                class="btn btn-danger btn-sm"
                @click="deleteEdge(ou.id, child.id)"
              >
                <i class="far fa-times" />
              </button>
            </td>
          </tr>
        </b-table-simple>

        <div
          v-if="ou && ou.permissions.P3 && typeOptions.length > 0"
          class="mb-4"
        >
          <b-button
            class="btn-default btn-sm"
            @click="$bvModal.show('add-child')"
            ><i class="far fa-plus"
          /></b-button>

          <b-modal id="add-child" hide-footer>
            <template v-slot:modal-title>
              Ajouter une sous-structure
            </template>

            <div v-if="childrenOptions.length" class="mb-4">
              <h3>Ajouter une structure fille existante</h3>

              <div class="d-block">
                <b-form-select
                  v-model="childSelected"
                  :options="childrenOptions"
                >
                </b-form-select>
              </div>
              <b-button class="mt-3" block @click="submitModal('add-child')"
                >Valider
              </b-button>
            </div>

            <div v-if="typeOptions.length" class="mt-4">
              <h3>Créer un nouvelle structure fille</h3>

              <b-form>
                <b-form-group label="Type:" label-for="input-1">
                  <b-form-select
                    id="input-1"
                    v-model="createModel.type_id"
                    :options="typeOptions"
                    required
                  />
                </b-form-group>

                <b-form-group label="Nom:" label-for="input-2">
                  <b-form-input
                    label-for="input-2"
                    v-model="createModel.nom"
                    required
                  />
                </b-form-group>
              </b-form>

              <b-button class="mt-3" block @click="submitModal('create-child')"
                >Valider
              </b-button>
            </div>
          </b-modal>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EventBus from "../../../event-bus";

export default {
  props: {
    ou: Object,
  },

  data() {
    return {
      parentsOptions: [],
      childrenOptions: [],
      parentSelected: null,
      childSelected: null,

      // Create form
      createModel: {
        nom: "",
        type_id: null,
      },

      typeOptions: [],
    };
  },

  watch: {
    $route: "fetchData",
    ou: "fetchData",
  },

  methods: {
    fetchData() {
      if (!this.ou) {
        return;
      }

      this.$root.rpc("sg_get_parents_options", [this.ou.id]).then(result => {
        this.parentsOptions = result;
      });

      this.$root.rpc("sg_get_children_options", [this.ou.id]).then(result => {
        this.childrenOptions = result;
      });

      this.$root
        .rpc("sg_get_possible_child_types", [this.ou.id])
        .then(result => {
          this.typeOptions = result;
        });
    },

    submitModal(type) {
      let args;

      if (type === "create-child") {
        args = [this.ou.id, this.createModel];
        const msg = "Sous-structure créée.";
        if (confirm(`Voulez-vous vraiment ajouter cette sous-structure?`)) {
          this.$root.rpc("sg_create_child_structure", args, msg).then(() => {
            EventBus.$emit("refresh-structure");
          });
        }
        this.$bvModal.hide(type);
        return;
      }

      if (type === "add-parent") {
        args = [this.parentSelected, this.ou.id];
      } else if (type === "add-child") {
        args = [this.ou.id, this.childSelected];
      }
      if (confirm(`Voulez-vous vraiment ajouter ce lien hiérarchique?`)) {
        const msg = "Lien ajouté.";
        this.$root.rpc("sg_add_edge", args, msg).then(() => {
          EventBus.$emit("refresh-structure");
        });
      }

      this.$bvModal.hide(type);
    },

    deleteEdge(parentId, childId) {
      if (confirm(`Voulez-vous vraiment supprimer le lien hiérarchique?`)) {
        const args = [parentId, childId];
        const msg = "Lien supprimé.";
        this.$root.rpc("sg_delete_edge", args, msg).then(() => {
          EventBus.$emit("refresh-structure");
        });
      }
    },
  },
};
</script>
