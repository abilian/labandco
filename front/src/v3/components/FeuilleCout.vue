<!-- suppress OverlyComplexArithmeticExpressionJS -->
<template>
  <div class="m-3 feuille-cout">
    <h1>
      Estimation des coûts complets de la recherche
      <span v-if="!model.id">(calculette)</span>
    </h1>

    <p v-if="!model.editable">
      Attention, seul le porteur du projet ou le gestionnaire de la demande peut
      sauvergarder les modifications effectuées sur cette feuille de calcul.
    </p>

    <h2>
      Dépenses liées aux personnels de la structure impliqués dans le projet de
      recherche
    </h2>

    <h3>
      T1 : Personnel permanent titulaire et/ou contractuel rémunéré par Sorbonne
      Université ou d'autres partenaires (INSERM, CNRS…)
    </h3>

    <table
      class="table table-condensed table-bordered"
      @keyup="modelUpdated"
      @change="modelUpdated"
    >
      <thead>
        <tr class="personnel">
          <th />
          <th>Nom</th>
          <th>Prénom</th>
          <th>Établissement employeur</th>
          <th>Statut</th>
          <th>Brut mensuel</th>
          <th>Période d'activité (mois)</th>
          <th>% d'activité sur le projet</th>
          <th>Personne mois</th>
          <th>Salaire brut chargé sur le projet</th>
          <th>Coût complet environné</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(line, index) in model.t1.lines">
          <td>
            <button
              class="btn btn-danger no-print"
              @click="removeLine('t1', line)"
            >
              -
            </button>
          </td>
          <td>
            <input
              v-model="line.nom"
              :readonly="readonly"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.nom }}</span>
          </td>

          <td>
            <input
              v-model="line.prenom"
              :readonly="readonly"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.prenom }}</span>
          </td>

          <td>
            <input
              v-model="line.employeur"
              :readonly="readonly"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.employeur }}</span>
          </td>

          <td>
            <select
              v-model="line.statut"
              :readonly="readonly"
              class="form-control"
            >
              <option
                v-for="statut in statuts"
                :value="statut"
                :selected="line.statut === statut"
              >
                {{ statut }}
              </option>
            </select>
            <span class="only-print">{{ line.statut }}</span>
          </td>

          <td>{{ line.brut_mensuel | currency("€") }}</td>

          <td>
            <input
              v-model="line.duree_mois"
              :readonly="readonly"
              class="form-control"
              type="number"
            />
            <span class="only-print">{{ line.duree_mois }}</span>
          </td>

          <td>
            <input
              v-model="line.pc_activite"
              :readonly="readonly"
              class="form-control"
              type="number"
            />
            <span class="only-print">{{ line.pc_activite }}</span>
          </td>

          <td class="number">
            {{ line.personne_mois }}
          </td>

          <td class="currency">
            {{ line.brut_charge_projet | currency("€") }}
          </td>

          <td class="currency">
            {{ line.cout_complet | currency("€") }}
          </td>
        </tr>

        <tr>
          <td colspan="8">Total</td>
          <td class="number">
            {{ model.t1.total_duree }}
          </td>
          <td class="currency">
            {{ model.t1.total_brut_charge | currency("€") }}
          </td>
          <td class="currency">
            {{ model.t1.total_cout_complet | currency("€") }}
          </td>
        </tr>
      </tbody>
    </table>

    <button
      v-if="!readonly"
      class="btn btn-default no-print"
      @click="addLine('t1')"
    >
      +
    </button>

    <!-- ------------------------------------------------------------------ -->

    <h3>
      T2 : Personnel non-permanent, hébergé non rémunéré par Sorbonne Université
      ou d'autres partenaires (INSERM, CNRS…)
    </h3>

    <table
      class="table table-condensed table-bordered"
      @keyup="modelUpdated"
      @change="modelUpdated"
    >
      <thead>
        <tr class="personnel">
          <th />
          <th>Nom</th>
          <th>Prénom</th>
          <th>Établissement employeur</th>
          <th>Statut</th>
          <th>Période d'activité (mois)</th>
          <th>% d'activité sur le projet</th>
          <th>Personne mois</th>
          <th>Coût complet environné</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="line in model.t2.lines">
          <td>
            <button
              class="btn btn-danger no-print"
              @click="removeLine('t2', line)"
            >
              -
            </button>
          </td>

          <td>
            <input
              v-model="line.nom"
              :readonly="readonly"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.nom }}</span>
          </td>

          <td>
            <input
              v-model="line.prenom"
              :readonly="readonly"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.prenom }}</span>
          </td>

          <td>
            <input
              v-model="line.employeur"
              :readonly="readonly"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.employeur }}</span>
          </td>

          <td>
            <select
              v-model="line.statut"
              :readonly="readonly"
              class="form-control"
            >
              <option
                v-for="statut in statuts2"
                :value="statut"
                :selected="line.statut === statut"
              >
                {{ statut }}
              </option>
            </select>
            <span class="only-print">{{ line.statut }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.duree_mois"
              class="form-control"
              type="number"
            />
            <span class="only-print">{{ line.duree_mois }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.pc_activite"
              class="form-control"
              type="number"
            />
            <span class="only-print">{{ line.pc_activite }}</span>
          </td>

          <td>{{ line.personne_mois }}</td>

          <td class="currency">
            {{ line.cout_complet | currency("€") }}
          </td>
        </tr>

        <tr>
          <td colspan="7">Total</td>
          <td class="number">
            {{ model.t2.total_duree }}
          </td>
          <td class="currency">
            {{ model.t2.total_cout_complet | currency("€") }}
          </td>
        </tr>
      </tbody>
    </table>

    <button
      v-if="!readonly"
      class="btn btn-default no-print"
      @click="addLine('t2')"
    >
      +
    </button>

    <h2>Dépenses liées aux personnels à recruter sur la convention</h2>

    <!-- ------------------------------------------------------------------ -->

    <h3>T3 : Personnel non-permanent, rémunéré sur la convention</h3>

    <table
      class="table table-condensed table-bordered"
      @keyup="modelUpdated"
      @change="modelUpdated"
    >
      <thead>
        <tr class="personnel">
          <th />
          <th>Nom</th>
          <th>Prénom</th>
          <th>Établissement employeur</th>
          <th>Statut</th>
          <th>Brut mensuel (€)</th>
          <th>Période d'activité (mois)</th>
          <th>% d'activité sur le projet</th>
          <th>Personne mois</th>
          <th>Salaire brut chargé sur le projet</th>
          <th>Coût complet environné</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="line in model.t3.lines">
          <td>
            <button
              class="btn btn-danger no-print"
              @click="removeLine('t3', line)"
            >
              -
            </button>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.nom"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.nom }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.prenom"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.prenom }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.employeur"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.employeur }}</span>
          </td>

          <td>CDD</td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.brut_mensuel"
              class="form-control"
              type="number"
              step="0.01"
            />
            <span class="only-print">{{ line.brut_mensuel }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.duree_mois"
              class="form-control"
              type="number"
            />
            <span class="only-print">{{ line.duree_mois }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.pc_activite"
              class="form-control"
              type="number"
            />
            <span class="only-print">{{ line.pc_activite }}</span>
          </td>

          <td>{{ line.personne_mois }}</td>

          <td class="currency">
            {{ line.brut_charge_projet | currency("€") }}
          </td>

          <td class="currency">
            {{ line.cout_complet | currency("€") }}
          </td>
        </tr>

        <tr>
          <td colspan="8">Total</td>
          <td class="number">
            {{ model.t3.total_duree }}
          </td>
          <td class="currency">
            {{ model.t3.total_brut_charge | currency("€") }}
          </td>
          <td class="currency">
            {{ model.t3.total_cout_complet | currency("€") }}
          </td>
        </tr>

        <tr>
          <td colspan="6" />
          <td colspan="3">
            Total + provision risque et charge du personnel contractuel
          </td>
          <td class="currency">
            {{ model.t3.total_plus_provision | currency("€") }}
          </td>
          <td />
        </tr>
      </tbody>
    </table>

    <button
      v-if="!readonly"
      class="btn btn-default no-print"
      @click="addLine('t3')"
    >
      +
    </button>

    <!-- ------------------------------------------------------------------ -->

    <h3>
      T4 : Personnel stagiaire gratifié sur la convention (impact sur le budget
      de fonctionnement)
    </h3>

    <table
      class="table table-condensed table-bordered"
      @keyup="modelUpdated"
      @change="modelUpdated"
    >
      <thead>
        <tr class="personnel">
          <th />
          <th>Nom</th>
          <th>Prénom</th>
          <th>Coût horaire</th>
          <th>Période d'activité (mois)</th>
          <th>% d'activité sur le projet</th>
          <th>Personne mois</th>
          <th>Gratification estimée</th>
          <th>Coût complet environné</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="line in model.t4.lines">
          <td>
            <button
              class="btn btn-danger no-print"
              @click="removeLine('t4', line)"
            >
              -
            </button>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.nom"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.nom }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.prenom"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.prenom }}</span>
          </td>

          <td>{{ model.constants.COUT_HORAIRE_STAGE | currency("€") }}</td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.duree_mois"
              class="form-control"
              type="number"
            />
            <span class="only-print">{{ line.duree_mois }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.pc_activite"
              class="form-control"
              type="number"
            />
            <span class="only-print">{{ line.pc_activité }}</span>
          </td>

          <td>{{ line.personne_mois }}</td>

          <td class="currency">
            {{ line.gratification_estimee | currency("€") }}
          </td>

          <td class="currency">
            {{ line.cout_complet | currency("€") }}
          </td>
        </tr>

        <tr>
          <td colspan="6">Total</td>
          <td class="number">
            {{ model.t4.total_duree }}
          </td>
          <td class="currency">
            {{ model.t4.total_gratification | currency("€") }}
          </td>
          <td class="currency">
            {{ model.t4.total_cout_complet | currency("€") }}
          </td>
          <td />
        </tr>
      </tbody>
    </table>

    <button
      v-if="!readonly"
      class="btn btn-default no-print"
      @click="addLine('t4')"
    >
      +
    </button>

    <h2>Autres dépenses</h2>

    <!-- ------------------------------------------------------------------ -->

    <h3>T5 : Equipement (bien immobilisé)</h3>

    <table
      class="table table-condensed table-bordered"
      @keyup="modelUpdated"
      @change="modelUpdated"
    >
      <thead>
        <tr class="personnel">
          <th />
          <th>Désignation</th>
          <th>Coût HT (€)</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="line in model.t5.lines">
          <td>
            <button
              class="btn btn-danger no-print"
              @click="removeLine('t5', line)"
            >
              -
            </button>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.designation"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.designation }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.cout_ht"
              class="form-control"
              type="number"
              step="0.01"
            />
            <span class="only-print">{{ line.cout_ht }}</span>
          </td>
        </tr>

        <tr>
          <td colspan="2">Total</td>
          <td class="currency">
            {{ model.t5.cout_total | currency("€") }}
          </td>
        </tr>
      </tbody>
    </table>

    <button
      v-if="!readonly"
      class="btn btn-default no-print"
      @click="addLine('t5')"
    >
      +
    </button>

    <!-- ------------------------------------------------------------------ -->

    <h3>
      T6 : Autres dépenses de fonctionnement : consommables, petit équipement
      non armortissable (hors eau, gaz et électricité), publications, stagiaires
    </h3>

    <table
      class="table table-condensed table-bordered"
      @keyup="modelUpdated"
      @change="modelUpdated"
    >
      <thead>
        <tr class="personnel">
          <th />
          <th>Désignation</th>
          <th>Coût HT (€)</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="line in model.t6.lines">
          <td>
            <button
              class="btn btn-danger no-print"
              @click="removeLine('t6', line)"
            >
              -
            </button>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.designation"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.designation }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.cout_ht"
              class="form-control"
              type="number"
              step="0.01"
            />
          </td>
          <span class="only-print">{{ line.cout_ht }}</span>
        </tr>

        <tr>
          <td colspan="2">Total</td>
          <td class="currency">
            {{ model.t6.cout_total | currency("€") }}
          </td>
        </tr>
      </tbody>
    </table>

    <button
      v-if="!readonly"
      class="btn btn-default no-print"
      @click="addLine('t6')"
    >
      +
    </button>

    <!-- ------------------------------------------------------------------ -->

    <h3>T7 : Frais de missions</h3>

    <table
      class="table table-condensed table-bordered"
      @keyup="modelUpdated"
      @change="modelUpdated"
    >
      <thead>
        <tr class="personnel">
          <th />
          <th>Désignation</th>
          <th>Coût HT (€)</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="line in model.t7.lines">
          <td>
            <button
              class="btn btn-danger no-print"
              @click="removeLine('t7', line)"
            >
              -
            </button>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.designation"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.designation }}</span>
          </td>

          <td>
            <input
              v-model="line.cout_ht"
              class="form-control"
              type="number"
              step="0.01"
            />
            <span class="only-print">{{ line.cout_ht }}</span>
          </td>
        </tr>

        <tr>
          <td colspan="2">Total</td>
          <td class="currency">
            {{ model.t7.cout_total | currency("€") }}
          </td>
        </tr>
      </tbody>
    </table>

    <button
      v-if="!readonly"
      class="btn btn-default no-print"
      @click="addLine('t7')"
    >
      +
    </button>

    <!-- ------------------------------------------------------------------ -->

    <h3>T8 : Prestation</h3>

    <table
      class="table table-condensed table-bordered"
      @keyup="modelUpdated"
      @change="modelUpdated"
    >
      <thead>
        <tr class="personnel">
          <th />
          <th>Désignation</th>
          <th>Coût HT (€)</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="line in model.t8.lines">
          <td>
            <button
              class="btn btn-danger no-print"
              @click="removeLine('t8', line)"
            >
              -
            </button>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.designation"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.designation }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.cout_ht"
              class="form-control"
              type="number"
              step="0.01"
            />
            <span class="only-print">{{ line.cout_ht }}</span>
          </td>
        </tr>

        <tr>
          <td colspan="2">Total</td>
          <td class="currency">
            {{ model.t8.cout_total | currency("€") }}
          </td>
        </tr>
      </tbody>
    </table>

    <button
      v-if="!readonly"
      class="btn btn-default no-print"
      @click="addLine('t8')"
    >
      +
    </button>

    <!-- ------------------------------------------------------------------ -->

    <h3>
      T9 : Dépenses liées à l'utilisation de moyens spécifiques (équipements…)
    </h3>

    <table
      class="table table-condensed table-bordered"
      @keyup="modelUpdated"
      @change="modelUpdated"
    >
      <thead>
        <tr>
          <th />
          <th>Équipement utilisé et acheté depuis moins de 5 ans</th>
          <th>Catégorie d'équipement</th>
          <th>Mois année d'achat</th>
          <th>Utilisation en % temps mensuel</th>
          <th>Durée d'amortissement (années)</th>
          <th>Prix d'achat HT</th>
          <th>Charge d'amortissement</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="line in model.t9.lines">
          <td>
            <button
              class="btn btn-danger no-print"
              @click="removeLine('t9', line)"
            >
              -
            </button>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.designation"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.designation }}</span>
          </td>

          <td>
            <select
              :readonly="readonly"
              v-model="line.categorie"
              class="form-control"
            >
              <option
                v-for="categorie in categories"
                :value="categorie"
                :selected="line.categorie === categorie"
              >
                {{ categorie }}
              </option>
            </select>
            <span class="only-print">{{ line.categorie }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.mois_annee_achat"
              class="form-control"
              type="text"
            />
            <span class="only-print">{{ line.mois_annee_achat }}</span>
          </td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.pc_utilisation"
              class="form-control"
              type="number"
            />
            <span class="only-print">{{ line.pc_utilisation }}</span>
          </td>

          <td>{{ line.duree_amortissement }}</td>

          <td>
            <input
              :readonly="readonly"
              v-model="line.prix_achat"
              class="form-control"
              type="number"
              step="0.01"
            />
            <span class="only-print">{{ line.prix_achat }}</span>
          </td>

          <td>{{ line.charge_amortissement | currency("€") }}</td>
        </tr>

        <tr>
          <td colspan="7">Total</td>
          <td class="currency">
            {{ model.t9.cout_total | currency("€") }}
          </td>
        </tr>
      </tbody>
    </table>

    <button
      v-if="!readonly"
      class="btn btn-default no-print"
      @click="addLine('t9')"
    >
      +
    </button>

    <h2>Totaux</h2>

    <table
      class="table table-condensed table-bordered"
      @keyup="modelUpdated"
      @change="modelUpdated"
    >
      <thead>
        <tr>
          <th />
          <th />
          <th style="min-width: 240px" />
          <th style="min-width: 120px">Coûts additionnels</th>
          <th style="min-width: 120px">Coût total</th>
        </tr>
      </thead>

      <tr>
        <td rowspan="5">Coûts directs</td>
        <td>
          Total des dépenses de personnels permanents titulaires ou contractuels
          rémunérés par Sorbonne Université ou d'autres partenaires (INSERM,
          CNRS…)
        </td>
        <td>(= T1)</td>
        <td class="currency">
          {{ model.ca1 | currency("€") }}
        </td>
        <td class="currency">
          {{ model.ct1 | currency("€") }}
        </td>
      </tr>

      <tr>
        <td>
          Total des dépenses de personnels non permanents rémunérés (hors risque
          et charge du personnel contractuel)
        </td>
        <td>(= T3)</td>
        <td class="currency">
          {{ model.ca2 | currency("€") }}
        </td>
        <td class="currency">
          {{ model.ct2 | currency("€") }}
        </td>
      </tr>

      <tr>
        <td>Total des dépenses d'équipement</td>
        <td>(= T5)</td>
        <td class="currency">
          {{ model.ca3 | currency("€") }}
        </td>
        <td class="currency">
          {{ model.ct3 | currency("€") }}
        </td>
      </tr>

      <tr>
        <td>Total des dépenses de fonctionnement</td>
        <td>(= T4 + T6 + T7 + T8 +T9)</td>
        <td class="currency">
          {{ model.ca4 | currency("€") }}
        </td>
        <td class="currency">
          {{ model.ct4 | currency("€") }}
        </td>
      </tr>

      <tr>
        <td><b>Total des dépenses</b></td>
        <td />
        <td class="currency">
          <b>{{ model.ca5 | currency("€") }}</b>
        </td>
        <td class="currency">
          <b>{{ model.ct5 | currency("€") }}</b>
        </td>
      </tr>

      <tr>
        <td rowspan="6">Coûts indirects</td>
        <td>Coût d'environnement associé à la charge de personnel permanent</td>
        <td>
          (= T1 * {{ model.constants.TAUX_ENVIRONNEMENT_PERSONNEL_PERMANENT }}%)
        </td>
        <td class="currency">
          {{ model.ca6 | currency("€") }}
        </td>
        <td class="currency">
          {{ model.ct6 | currency("€") }}
        </td>
      </tr>

      <tr>
        <td>Coût d'environnement associé à la charge de personnel hébergé</td>
        <td>
          (= T2 *
          {{ model.constants.COUT_ENVIRONNEMENT_PERSONNEL_HEBERGE }} forfait
          mois complet)
        </td>
        <td class="currency">
          {{ model.ca7 | currency("€") }}
        </td>
        <td class="currency">
          {{ model.ct7 | currency("€") }}
        </td>
      </tr>

      <tr>
        <td>
          Coût d'environnement associé à la charge de personnel non permanent et
          aux stagiaires gratifiés sur la convention
        </td>
        <td>
          (= (T3 +T4) x
          {{ model.constants.TAUX_ENVIRONNEMENT_PERSONNEL_NON_PERMANENT }}%)
        </td>
        <td class="currency">
          {{ model.ca8 | currency("€") }}
        </td>
        <td class="currency">
          {{ model.ct8 | currency("€") }}
        </td>
      </tr>

      <tr>
        <td>
          Participation aux coûts induits par le contrat pour Sorbonne
          Université
        </td>
        <td>
          (=
          <input
            :readonly="readonly"
            v-model="model.couts_induits"
            type="number"
            style="width: 40px"
          /><span class="only-print">{{ model.couts_induits }}</span
          >% du coût total)
        </td>
        <td class="currency">
          {{ model.ca10 | currency("€") }}
        </td>
        <td class="currency">
          {{ model.ct10 | currency("€") }}
        </td>
      </tr>

      <tr>
        <td>Préciput structure</td>
        <td>
          (=
          <input
            :readonly="readonly"
            v-model="model.preciput_labo"
            type="number"
            style="width: 40px"
          /><span class="only-print">{{ model.preciput_labo }}</span
          >% du coût total - part SU)
        </td>
        <td class="currency">
          {{ model.ca11 | currency("€") }}
        </td>
        <td class="currency">
          {{ model.ct11 | currency("€") }}
        </td>
      </tr>

      <tr>
        <td><b>Total des coûts indirects</b></td>
        <td />
        <td class="currency">
          <b>{{ model.ca12 | currency("€") }}</b>
        </td>
        <td class="currency">
          <b>{{ model.ct12 | currency("€") }}</b>
        </td>
      </tr>

      <tr>
        <td colspan="3">
          <b>Coût total HT de la recherche pour SU</b>
        </td>
        <td class="currency">
          <b>{{ model.ca13 | currency("€") }}</b>
        </td>
        <td class="currency">
          <b>{{ model.ct13 | currency("€") }}</b>
        </td>
      </tr>
    </table>

    <h3>Note</h3>

    <p>
      Le coût total calculé par ce devis est une base de travail avant un
      ajustement possible discuté avec le porteur de projet/chargé d'affaire
      scientifique.
    </p>

    <p>Ce devis est aussi une base de négociation avec ses partenaires.</p>

    <p>
      Le coût additionnel correspond au minimum nécessaire pour les projets de
      type ANR ou collaborations.
    </p>

    <p>Le coût complet correspond au montant minimum d'une prestation.</p>

    <div v-if="model.id" class="no-print" style="text-align: center">
      <button
        v-if="model.editable && !saving"
        class="btn btn-primary m-1"
        @click="onSubmit"
      >
        Sauver
      </button>
      <button v-if="model.editable && saving" class="btn btn-primary m-1">
        Saving...
      </button>
      <button class="btn btn-danger m-1" @click="onCancel">
        Retour à la demande
      </button>
    </div>
  </div>
</template>

<script>
import Vue from "vue";

export default {
  props: {
    model: { type: Object, required: true },
  },

  data() {
    const constants = this.model.constants;
    const categories = constants.DUREE_AMORTISSEMENT.map((x) => x[0]);
    const statuts = constants.REMUNERATION.map((x) => x[0]);

    return {
      statuts: [""].concat(statuts),
      statuts2: ["", "Stagiaire", "Bourse Cifre", "Invité", "Autre"],
      categories: [""].concat(categories),
      saving: false,
      readonly: !this.model.editable,
    };
  },

  created() {
    for (let i = 1; i <= 9; i++) {
      if (!this.model["t" + i]) {
        Vue.set(this.model, "t" + i, { lines: [] });
      }
    }
    this.modelUpdated();
  },

  methods: {
    onCancel(e) {
      e.preventDefault();
      window.location = `/#/demandes/${this.model.id}`;
    },

    onSubmit(e) {
      e.preventDefault();
      if (this.saving) {
        return;
      }
      this.saving = true;
      const html = document.children[0].innerHTML;
      const args = [this.model, html];
      const msg = "Feuille de coût sauvegardée";
      this.$root.rpc("update_feuille_de_cout", args, msg).then((result) => {
        window.location = `/#/demandes/${this.model.id}`;
      });
    },

    modelUpdated() {
      update_t1(this.model, this.model.t1);
      update_t2(this.model, this.model.t2);
      update_t3(this.model, this.model.t3);
      update_t4(this.model, this.model.t4);
      update_t5_8(this.model, this.model.t5);
      update_t5_8(this.model, this.model.t6);
      update_t5_8(this.model, this.model.t7);
      update_t5_8(this.model, this.model.t8);
      update_t9(this.model, this.model.t9);

      update_couts_totaux(this.model);
    },

    addLine(t) {
      this.model[t].lines.push({});
    },

    removeLine(t, line) {
      // this.model[t].lines.[index];
      let index = this.model[t].lines.indexOf(line);
      this.model[t].lines.splice(index, 1);
      this.modelUpdated();
    },
  },
};

function get_brut_charge(model, line) {
  // field: '<indice> : <CT annuel>' depuis constante json.
  // brut chargé = CT annuel / 12."
  if (typeof model.couts_charges[line.statut] === "undefined") {
    // alert("Pas de coût chargé donné pour " + line.statut);
    return 0;
  }
  let field = model.couts_charges[line.statut];
  let brut = field.split(":");
  brut = parseInt(brut[1]) / 12.0;
  return brut;
}

function update_t1(m, t) {
  let total_duree = 0;
  let total_brut_charge = 0;
  let total_cout_complet = 0;

  for (let line of t.lines) {
    if (line.pc_activite > 100) {
      line.pc_activite = 100;
    }
    if (line.pc_activite < 0) {
      line.pc_activite = 0;
    }
    Vue.set(line, "statut", (line.statut || "").trim());
    Vue.set(line, "brut_mensuel", salaire_charge(m, line.statut));
    Vue.set(
      line,
      "personne_mois",
      ((line.duree_mois || 0) * (line.pc_activite || 0)) / 100
    );
    const brut_charge_mensuel = get_brut_charge(m, line);
    Vue.set(
      line,
      "brut_charge_projet",
      line.personne_mois * brut_charge_mensuel
    );
    Vue.set(
      line,
      "cout_complet",
      (1 + m.constants.TAUX_ENVIRONNEMENT_PERSONNEL_PERMANENT) *
        line.brut_charge_projet
    );

    total_duree += line.personne_mois;
    total_brut_charge += line.brut_charge_projet;
    total_cout_complet += line.cout_complet;
  }
  Vue.set(t, "total_duree", total_duree);
  Vue.set(t, "total_brut_charge", total_brut_charge);
  Vue.set(t, "total_cout_complet", total_cout_complet);
}

function update_t2(m, t) {
  let total_duree = 0;
  let total_cout_complet = 0;

  for (let line of t.lines) {
    if (line.pc_activite > 100) {
      line.pc_activite = 100;
    }
    if (line.pc_activite < 0) {
      line.pc_activite = 0;
    }

    Vue.set(
      line,
      "personne_mois",
      ((line.duree_mois || 0) * (line.pc_activite || 0)) / 100
    );
    Vue.set(
      line,
      "cout_complet",
      line.personne_mois * m.constants.COUT_ENVIRONNEMENT_PERSONNEL_HEBERGE
    );

    total_duree += line.personne_mois;
    total_cout_complet += line.cout_complet;
  }
  Vue.set(t, "total_duree", total_duree);
  Vue.set(t, "total_cout_complet", total_cout_complet);
}

function update_t3(m, t) {
  let total_duree = 0;
  let total_brut_charge = 0;
  let total_cout_complet = 0;

  for (let line of t.lines) {
    if (line.pc_activite > 100) {
      line.pc_activite = 100;
    }
    if (line.pc_activite < 0) {
      line.pc_activite = 0;
    }

    const brut_charge_mensuel =
      line.brut_mensuel * (1 + m.constants.TAUX_CHARGE_PATRONALE);
    const nb_mois = ((line.duree_mois || 0) * (line.pc_activite || 0)) / 100;
    Vue.set(line, "personne_mois", nb_mois);
    Vue.set(
      line,
      "brut_charge_projet",
      line.personne_mois * brut_charge_mensuel
    );
    Vue.set(
      line,
      "cout_complet",
      (1 + m.constants.TAUX_ENVIRONNEMENT_PERSONNEL_PERMANENT) *
        line.brut_charge_projet
    );

    total_duree += line.personne_mois;
    total_brut_charge += line.brut_charge_projet;
    total_cout_complet += line.cout_complet;
  }
  Vue.set(t, "total_duree", total_duree);
  Vue.set(t, "total_brut_charge", total_brut_charge);
  Vue.set(t, "total_cout_complet", total_cout_complet);
  Vue.set(
    t,
    "total_plus_provision",
    total_brut_charge * (1 + m.constants.TAUX_PROVISION_RISQUE)
  );
}

function update_t4(m, t) {
  let total_duree = 0;
  let total_gratification = 0;
  let total_cout_complet = 0;
  for (let line of t.lines) {
    if (line.pc_activite > 100) {
      line.pc_activite = 100;
    }
    if (line.pc_activite < 0) {
      line.pc_activite = 0;
    }

    let personne_mois =
      ((line.duree_mois || 0) * (line.pc_activite || 0)) / 100;
    total_duree += personne_mois;

    let gratification_estimee =
      line.personne_mois * m.constants.COUT_HORAIRE_STAGE * 7 * 22;
    total_gratification += gratification_estimee;

    let cout_complet =
      (1 + m.constants.TAUX_ENVIRONNEMENT_PERSONNEL_NON_PERMANENT) *
      gratification_estimee;
    total_cout_complet += cout_complet;

    Vue.set(line, "gratification_estimee", gratification_estimee);
    Vue.set(line, "personne_mois", personne_mois);
    Vue.set(line, "cout_complet", cout_complet);
  }
  Vue.set(t, "total_duree", total_duree);
  Vue.set(t, "total_gratification", total_gratification);
  Vue.set(t, "total_cout_complet", total_cout_complet);
}

function update_t5_8(m, t) {
  let cout_total = 0;
  for (let line of t.lines) {
    cout_total += line.cout_ht * 1.0;
  }
  Vue.set(t, "cout_total", cout_total);
}

function update_t9(m, t) {
  let cout_total = 0;
  for (let line of t.lines) {
    Vue.set(
      line,
      "duree_amortissement",
      duree_amortissement(m, line.categorie)
    );

    let charge_amortissement = 0;
    if (line.duree_amortissement) {
      charge_amortissement =
        ((((24 / 12.0) * line.pc_utilisation) / 100) * line.prix_achat) /
        line.duree_amortissement;
    }
    cout_total += charge_amortissement;
    Vue.set(line, "charge_amortissement", charge_amortissement);
  }
  Vue.set(t, "cout_total", cout_total);
}

function update_couts_totaux(m) {
  if (m.preciput_labo < 0) {
    m.preciput_labo = 0;
  }
  if (m.preciput_labo > 100) {
    m.preciput_labo = 100;
  }
  if (m.couts_induits === undefined) {
    m.couts_induits = 15;
  }
  if (m.couts_induits < 0) {
    m.couts_induits = 0;
  }
  if (m.couts_induits > 100) {
    m.couts_induits = 100;
  }

  const preciput = (m.preciput_labo || 0) / 100.0;
  const couts_induits = (m.couts_induits || 0) / 100.0;

  Vue.set(m, "ct1", m.t1.total_brut_charge || 0);
  Vue.set(m, "ct2", m.t3.total_plus_provision || 0);
  Vue.set(m, "ct3", m.t5.cout_total || 0);
  Vue.set(
    m,
    "ct4",
    m.t4.total_gratification +
      m.t6.cout_total +
      m.t7.cout_total +
      m.t8.cout_total +
      m.t9.cout_total || 0
  );
  Vue.set(m, "ct5", m.ct1 + m.ct2 + m.ct3 + m.ct4);

  Vue.set(
    m,
    "ct6",
    m.ct1 * m.constants.TAUX_ENVIRONNEMENT_PERSONNEL_PERMANENT || 0
  );
  Vue.set(
    m,
    "ct7",
    m.t2.total_duree * m.constants.COUT_ENVIRONNEMENT_PERSONNEL_HEBERGE || 0
  );
  Vue.set(
    m,
    "ct8",
    (m.t3.total_plus_provision + m.t4.total_gratification) *
      m.constants.TAUX_ENVIRONNEMENT_PERSONNEL_NON_PERMANENT
  );

  // const tx_part = m.constants.TAUX_PARTICIPATION_COUTS_INDUITS;
  const tx_part = couts_induits;
  Vue.set(
    m,
    "ct11",
    ((m.ct5 + m.ct6 + m.ct7 + m.ct8) /
      (1 - preciput - tx_part + preciput * tx_part)) *
      preciput
  );
  Vue.set(
    m,
    "ct10",
    ((m.ct5 + m.ct6 + m.ct7 + m.ct8 + m.ct11) /
      (1 - preciput - tx_part + preciput * tx_part)) *
      tx_part
  );
  Vue.set(m, "ct12", m.ct6 + m.ct7 + m.ct8 + m.ct10 + m.ct11);
  Vue.set(m, "ct13", m.ct5 + m.ct12);

  Vue.set(m, "ca1", 0);
  Vue.set(m, "ca2", m.ct2);
  Vue.set(m, "ca3", m.ct3);
  Vue.set(m, "ca4", m.ct4);
  Vue.set(m, "ca5", m.ca2 + m.ca3 + m.ca4);
  Vue.set(m, "ca6", 0);
  Vue.set(
    m,
    "ca7",
    m.t2.total_duree * m.constants.COUT_ENVIRONNEMENT_PERSONNEL_HEBERGE || 0
  );
  Vue.set(
    m,
    "ca8",
    (m.t3.total_plus_provision + m.t4.total_gratification) *
      m.constants.TAUX_ENVIRONNEMENT_PERSONNEL_NON_PERMANENT
  );

  Vue.set(
    m,
    "ca11",
    ((m.ca5 + m.ca6 + m.ca7 + m.ca8) /
      (1 - preciput - tx_part + preciput * tx_part)) *
      preciput
  );
  Vue.set(
    m,
    "ca10",
    ((m.ca5 + m.ca6 + m.ca7 + m.ca8 + m.ca11) /
      (1 - preciput - tx_part + preciput * tx_part)) *
      tx_part
  );
  Vue.set(m, "ca12", m.ca6 + m.ca7 + m.ca8 + m.ca10 + m.ca11);
  Vue.set(m, "ca13", m.ca5 + m.ca12);
}

function salaire_charge(m, statut) {
  const table = {};
  for (let t of m.constants.REMUNERATION) {
    table[t[0]] = t[1] * m.constants.POINT_INDICE;
  }
  return table[statut] || 0;
}

function duree_amortissement(m, categorie) {
  const table = {};
  for (let t of m.constants.DUREE_AMORTISSEMENT) {
    table[t[0]] = t[1];
  }
  return table[categorie] || 0;
}
</script>

<style>
h2,
h3 {
  margin-top: 1em;
  margin-bottom: 0.5em;
}

/*@page {*/
/*  size: A4 landscape;*/
/*}*/

/*@media print {*/
/*  .feuille-cout {*/
/*    font-family: "Arial", sans-serif;*/
/*    font-size: 9pt;*/
/*    !* Doesn't work with WeasyPrint *!*/
/*    hyphens: auto;*/
/*  }*/
/*}*/
</style>
