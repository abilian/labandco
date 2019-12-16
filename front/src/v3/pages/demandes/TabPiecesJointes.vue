<template>
  <div class="mt-4">
    <div v-if="demande.type === 'Recrutement'">
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

    <h3>Pièces-jointes actuelles</h3>

    <ul v-if="piecesJointes">
      <li v-for="pj in piecesJointes" class="row">
        <div class="col-md-6">
          <!--            <a-->
          <!--                href="{{ url_for(".demande_get_attachment", id=demande.id, pj_id=pj.id) }}">{{ pj.name }}</a>-->
          {{ pj.name }}
          <p v-if="pj.creator">
            (déposée par: {{ pj.creator.full_name }}).
            <span v-if="pj.date">
              Le {{ pj.date | moment("DD MMMM YYYY à h:mm:ss") }}.
            </span>
          </p>
        </div>

        <!--          <div class="col-md-1">-->
        <!--            <form method="post" enctype="multipart/form-data" role="form"-->
        <!--                name="delete-attachment"-->
        <!--                class="form-inline"-->
        <!--                action="{{ url_for('.demande_delete_attachment', id=demande.id, pj_id=pj.id) }}">-->
        <!--              <button type="submit" class="form-group form-actions text-danger">-->
        <!--                <span class="far fa-trash"></span>-->
        <!--              </button>-->
        <!--            </form>-->
        <!--          </div>-->
      </li>
      <!--    {% endfor %}-->
    </ul>

    <p v-else>Aucune pièce-jointe pour l'instant.</p>

    <!--{% if user.has_role('dgrtt') or user in demande.owners %}-->
    <!--  <h3>Ajouter une ou des pièce-jointes</h3>-->

    <!--  <form method="POST" enctype="multipart/form-data"-->
    <!--      action="{{ url_for(".demande_upload_attachment", id=demande.id) }}">-->

    <!--    <input type="file" name="file" multiple>-->

    <!--    <br>-->

    <!--    <input type="submit" class="btn btn-primary" name="Envoyer">-->
    <!--  </form>-->
    <!--{% endif %}-->
  </div>
</template>

<script>
export default {
  props: { demande: Object },

  data() {
    return {
      piecesJointes: this.demande.pieces_jointes,
    };
  },
};
</script>
