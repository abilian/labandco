<template>
  <b-card no-body>
    <div class="card-header box-primary">
      <h3 class="card-title">Informations-clefs</h3>
    </div>

    <div v-if="demande" class="card-body">
      <div class="row">
        <div class="col-md-6">
          <p>
            Type de demande: <b>{{ demande.type }}</b>

            <span v-if="demande.type === 'Demande autre'">
              ({{ demande.data.type }})</span
            >
          </p>

          <template v-if="demande.type === 'Recrutement'">
            <p>
              Intitulé: <b>{{ demande.nom }}</b>
            </p>
            <p>
              Fonction du poste: <b>{{ demande.data.fonction_du_poste }}</b>
            </p>

            <!-- TODO: make this server-side instead -->
            <p v-if="!demande.acces_restreint">
              Salaire brut mensuel:
              <b v-if="demande.salaire_brut_mensuel"
                >{{ demande.salaire_brut_mensuel }} euros</b
              >
            </p>

            <p>
              Date d'embauche:
              <b v-if="demande.date_debut">{{ demande.date_debut }}</b>
            </p>

            <p>
              Durée du contrat de travail:
              <b v-if="demande.duree_mois">{{ demande.duree_mois }} mois</b>
            </p>

            <!-- TODO: make this server-side instead -->
            <p v-if="!demande.acces_restreint">
              Coût total chargé:
              <b v-if="demande.cout_total_charge">{{
                demande.cout_total_charge
              }}</b>
            </p>
          </template>

          <template v-if="demande.type === 'Convention de recherche'">
            <p>
              Intitulé: <b>{{ demande.nom }}</b>
            </p>
            <p>
              Type de financeur: <b>{{ demande.data.type_financeur }}</b>
            </p>
            <p>
              Appel à projet: <b>{{ demande.data.appel_a_projets }}</b>
            </p>
            <p>
              Type de contrat: <b>{{ demande.data.type_contrat }}</b>
            </p>

            <p>
              Montant du financement envisagé:
              <b v-if="demande.data.montant_financement"
                >{{ demande.data.montant_financement }} euros</b
              >
            </p>

            <p v-if="!demande.data.appel_a_projets">
              Durée prévisionnelle:
              <b v-if="demande.data.duree_previsionnelle"
                >{{ demande.data.duree_previsionnelle }} mois</b
              >
            </p>
          </template>

          <template
            v-if="demande.type === 'Avenant à une convention de recherche'"
          >
            <p>
              Intitulé du projet: <b>{{ demande.nom_projet }}</b>
            </p>
            <p>
              EOTP ou № DR&amp;I: <b>{{ demande.eotp_ou_no_dgrtt }}</b>
            </p>
            <p>
              L'avenant concerne la modification de:
              <b>{{ demande.modifications }}</b>
            </p>
          </template>

          <template
            v-if="demande.type === 'Déclaration de logiciel / base de données'"
          >
            <p>
              Intitulé de l'œuvre: <b>{{ demande.data.intitule }}</b>
            </p>
            <p>
              Acronyme: <b>{{ demande.data.acronyme }}</b>
            </p>
          </template>

          <template v-if="demande.type === 'Déclaration d´invention'">
            <p>
              Titre de l'invention: <b>{{ demande.data.titre }}</b>
            </p>
          </template>

          <template v-if="demande.type === 'Demande autre'">
            <p>
              Intitulé: <b>{{ demande.nom }}</b>
            </p>
          </template>
        </div>

        <div class="col-md-6">
          <p>
            Etat de la demande: <b>{{ demande.workflow.state.label }}</b>

            ({{ demande.active ? "Active" : "Archivée" }})
          </p>

          <p v-if="demande.active">
            Prochaine action à réaliser:
            <b>{{ demande.workflow.state.next_action }}</b
            >, par:

            <b v-for="(user, index) in demande.workflow.owners">
              <router-link :to="{ name: 'user', params: { id: user.id } }">{{
                user.full_name
              }}</router-link
              ><span v-if="index !== demande.workflow.owners.length - 1"
                >,
              </span>
            </b>
          </p>

          <p v-if="demande.porteur">
            Porteur:
            <b>
              <router-link
                :to="{ name: 'user', params: { id: demande.porteur.id } }"
                >{{ demande.porteur.full_name }}
              </router-link>
            </b>
          </p>

          <p v-if="demande.gestionnaire">
            Gestionnaire de la demande:
            <b>
              <router-link
                :to="{ name: 'user', params: { id: demande.gestionnaire.id } }"
                >{{ demande.gestionnaire.full_name }}
              </router-link>
            </b>
          </p>

          <p v-if="demande.contact_labco">
            Contact Lab&amp;Co:
            <b>
              <router-link
                :to="{ name: 'user', params: { id: demande.contact_labco.id } }"
                >{{ demande.contact_labco.full_name }}
              </router-link>
            </b>
          </p>

          <p v-if="demande.contributeurs.length > 0">
            Contributeurs:
            <b v-for="(contributeur, index) in demande.contributeurs">
              <router-link
                :to="{ name: 'user', params: { id: contributeur.id } }"
                >{{ contributeur.full_name }}</router-link
              ><span v-if="index !== demande.contributeurs.length - 1">, </span>
            </b>
          </p>
          <p v-else>Contributeurs: aucun</p>
        </div>
      </div>
    </div>
    <div v-else class="card-body">Chargement en cours...</div>
  </b-card>
</template>

<script>
export default {
  props: { demande: Object },
};
</script>
