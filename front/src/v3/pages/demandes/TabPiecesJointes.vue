<template>
  <div class="mt-4">
    <div v-if="demande.type === 'Recrutement'">
      <div v-html="constants.demande_recrutement.pj"></div>

      <ul>
        <li v-if="demande.type === 'Doctorant'">Carte d'étudiant</li>
        <li v-if="demande.financement === 'Notification de financement'">
          Notification de financement
        </li>
        <li v-if="demande.financement2 === 'Notification de financement'">
          Notification de co-financement
        </li>
      </ul>
      <p>
        Ces documents peuvent être sous forme d'un ou plusieurs fichiers PDF, à
        votre convenance. Pensez bien, néanmoins, à vérifier que tous les
        documents demandés sont bien attachés à votre demande avant de la
        soumettre.
      </p>
    </div>

    <div v-if="demande.type === 'Convention de recherche'">
      <p>
        Vous pouvez (et, probablement, devez) joindre à ce formulaire des
        documents complémentaires : canevas d’appel à projets, annexe
        scientifique, annexe financière…
      </p>
    </div>

    <div v-if="demande.pieces_jointes.length > 0">
      <h3>Pièces-jointes actuelles</h3>

      <ul class="ml-0">
        <li v-for="pj in demande.pieces_jointes" class="row">
          <div class="mb-3">
            <b-button
              @click="deletePJ(pj.id)"
              variant="danger"
              size="sm"
              class="mr-2"
              >Delete</b-button
            >

            <a :href="'/blob/' + demande.id + '/' + pj.id">{{ pj.name }}</a>

            <span v-if="pj.creator" class="text-sm">
              Déposée par:
              <router-link
                :to="{ name: 'user', params: { id: pj.creator.id } }"
                >{{ pj.creator.name }}</router-link
              >.
              <span v-if="pj.date">
                Le {{ pj.date | moment("DD MMMM YYYY à h:mm:ss") }}.
              </span>
            </span>
          </div>
        </li>
      </ul>
    </div>

    <p v-else>Aucune pièce-jointe pour l'instant.</p>

    <div>
      <!-- TODO: ajouter un if -->
      <h3>Ajouter une ou des pièce-jointes</h3>

      <input
        type="file"
        id="files"
        ref="files"
        multiple
        @change="handleFilesUpload()"
      />

      <br />
      <b-btn @click="onSubmit" class="mt-2">Téléverser</b-btn>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  props: { demande: Object },

  data() {
    return {
      // piecesJointes: this.demande.pieces_jointes,
      files: [],
      // allowUpload: user.has_role('dgrtt') && user in demande.owners,
      constants: this.$storage.get("user_context").constants,
    };
  },

  methods: {
    onSubmit(e) {
      const fd = new FormData();

      let i = 0;
      for (let file of this.files) {
        fd.append("files-" + i, file);
        i++;
      }
      fd.append("demande_id", this.demande.id);

      axios
        .post("/upload/", fd, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        })
        .then(response => {
          this.$root.$bvToast.toast("Pièce(s) jointe(s) ajoutées", {
            title: "",
            variant: "success",
            solid: true,
          });
          this.$parent.$parent.$parent.refresh();
          this.$parent.$parent.$parent.goToTab("Pièces à joindre");
        })
        .catch(error => {
          this.$root.$bvToast.toast(`${error}`, {
            title: "",
            variant: "danger",
            solid: true,
          });
        });
    },

    deletePJ(blobId) {
      const args = [this.demande.id, blobId];
      this.$root.rpc("delete_pj", args).then(result => {
        this.$root.$bvToast.toast("Pièce jointe supprimée", {
          title: "",
          variant: "success",
          solid: true,
        });
        this.$parent.$parent.$parent.refresh();
        this.$parent.$parent.$parent.goToTab("Pièces à joindre");
      });
    },

    handleFilesUpload() {
      this.files = this.$refs.files.files;
    },
  },
};
</script>
