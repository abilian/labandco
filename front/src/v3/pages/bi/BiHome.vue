<template>
  <div>
    <breadcrumbs title="Statistiques" />

    <b-card>
      <b-card-header>
        <b-card-title>Statistiques</b-card-title>
      </b-card-header>

      <b-card-text v-if="stats">
        <div class="row">
          <div class="col-sm-6 pt-3 pr-5">
            <b-form-group label="Période du" label-for="periode_fin">
              <b-form-input
                id="periode_debut"
                v-model="selected.periode_debut"
                placeholder="AAAA-MM-JJ"
              />
            </b-form-group>

            <b-form-group label="Au" label-for="periode_fin">
              <b-form-input
                id="periode_fin"
                v-model="selected.periode_fin"
                placeholder="AAAA-MM-JJ"
              />
            </b-form-group>

            <template v-for="selector in selectors">
              <b-form-group
                :label="selector.label"
                :label-for="selector.name"
                :key="selector.name"
              >
                <multiselect
                  v-model="selected[selector.name]"
                  :id="selector.name"
                  :options="selector.options"
                  :multiple="selector.multiple"
                  track-by="value"
                  label="text"
                />
              </b-form-group>
            </template>

            <b-button @click="onSubmit" class="btn btn-default"
              >Actualiser</b-button
            >
          </div>

          <div v-if="totals" class="col-sm-6">
            <h3>Chiffres clefs pour la sélection</h3>

            <p>Total des demandes: {{ totals.nb_total }}</p>

            <p>&nbsp;&nbsp;Dont en cours: {{ totals.nb_en_cours }}</p>

            <p>
              &nbsp;&nbsp;&nbsp;&nbsp;Dont en édition (après une demande de
              modification): {{ totals.nb_en_edition }}
            </p>

            <p>
              &nbsp;&nbsp;&nbsp;&nbsp;Dont en validation:
              {{ totals.nb_en_validation }}
            </p>
            <p>
              &nbsp;&nbsp;&nbsp;&nbsp;Dont en vérification DR&amp;I:
              {{ totals.nb_en_verification }}
            </p>
            <p>
              &nbsp;&nbsp;&nbsp;&nbsp;Dont en instruction DR&amp;I:
              {{ totals.nb_en_instruction }}
            </p>

            <p>&nbsp;&nbsp;Dont archivées: {{ totals.nb_archivee }}</p>

            <p>
              &nbsp;&nbsp;&nbsp;&nbsp;Dont traitement finalisé par la DR&amp;I:
              {{ totals.nb_traitee }}
            </p>
            <p>
              &nbsp;&nbsp;&nbsp;&nbsp;Dont rejetées par la DR&amp;I:
              {{ totals.nb_rejetee }}
            </p>
            <p>
              &nbsp;&nbsp;&nbsp;&nbsp;Dont abandonnés:
              {{ totals.nb_abandonnee }}
            </p>
          </div>
        </div>

        <table class="table table-striped table-bordered bi-table mt-4">
          <thead>
            <tr>
              <td width="22%"></td>
              <td width="13%">Moyenne</td>
              <td width="13%">Médiane</td>
              <td width="13%">Ecart-type</td>
              <td width="13%">Min</td>
              <td width="13%">Max</td>
              <td width="13%">Cumul</td>
            </tr>
          </thead>

          <tbody v-if="stats">
            <template v-if="stats.conventions.count">
              <tr class="bi-subhead">
                <td colspan="7">
                  Demandes de conventions de recherche ({{
                    stats.conventions.count
                  }})
                </td>
              </tr>

              <tr>
                <td>Montant (€)</td>
                <td
                  v-for="x in stats.conventions.montant"
                  style="text-align: right"
                >
                  {{ x }}
                </td>
              </tr>

              <tr>
                <td>Recrutements prévus</td>
                <td
                  v-for="x in stats.conventions.recrutements_prev"
                  style="text-align: right"
                >
                  {{ x }}
                </td>
              </tr>

              <tr>
                <td>Durée prev. (mois)</td>
                <td
                  v-for="x in stats.conventions.duree"
                  style="text-align: right"
                >
                  {{ x }}
                </td>
              </tr>
            </template>

            <template v-if="stats.rh.count">
              <tr class="bi-subhead">
                <td colspan="7">Demandes RH ({{ stats.rh.count }})</td>
              </tr>

              <tr>
                <td>Durée (mois)</td>
                <td v-for="x in stats.rh.duree" style="text-align: right">
                  {{ x }}
                </td>
              </tr>

              <tr>
                <td>Salaire brut mensuel (€)</td>
                <td
                  v-for="x in stats.rh.salaire_brut_mensuel"
                  style="text-align: right"
                >
                  {{ x }}
                </td>
              </tr>

              <tr>
                <td>Coût total mensuel (€)</td>
                <td
                  v-for="x in stats.rh.cout_total_mensuel"
                  style="text-align: right"
                >
                  {{ x }}
                </td>
              </tr>
            </template>

            <tr v-if="stats.avenants.count" class="bi-subhead">
              <td colspan="7">
                Avenants convention ({{ stats.avenants.count }})
              </td>
            </tr>

            <tr v-if="stats.pi_logiciel.count" class="bi-subhead">
              <td colspan="7">PI logiciel ({{ stats.pi_logiciel.count }})</td>
            </tr>

            <tr v-if="stats.pi_invention.count" class="bi-subhead">
              <td colspan="7">PI invention ({{ stats.pi_invention.count }})</td>
            </tr>

            <tr>
              <td colspan="7" />
            </tr>

            <tr>
              <td class="bi-subhead">Durée de traitement (jours)</td>
              <td v-for="x in stats.duree_traitement" style="text-align: right">
                {{ x }}
              </td>
            </tr>
          </tbody>
        </table>
      </b-card-text>

      <b-card-text v-else> En cours de chargement... </b-card-text>
    </b-card>
  </div>
</template>

<script>
import { ContextFetcher } from "../../mixins";

export default {
  props: { id: String },

  mixins: [ContextFetcher],

  data() {
    return {
      ou: null,
      title: "Statistiques",
      stats: null,
      totals: {},
      selectors: [],
      selected: {},
    };
  },

  methods: {
    whenReady() {},

    onSubmit() {
      this.$root.rpc("get_stats", this.selected).then((result) => {
        this.stats = result.stats;
        this.totals = result.totals;

        const msg = "Tableau mis à jour";
        this.$root.$bvToast.toast(msg, {
          title: "OK",
          variant: "info",
          solid: true,
        });
      });
    },
  },
};
</script>
