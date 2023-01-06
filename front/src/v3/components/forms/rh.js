import _ from "lodash";
import fp from "lodash/fp";

export default function update_rh(form, model) {
  function get_fieldset_by_name(name) {
    return _.findIndex(form.fieldsets, function (it) {
      return it.name === name;
    });
  }

  const nature_du_recrutement = model.nature_du_recrutement;
  const salaires_indicatifs =
    form.constants.recrutement.salaire_brut_mensuel_indicatif;

  if (nature_du_recrutement === "CDD") {
    const choices = [
      "Contrat initial",
      "Renouvellement",
      "Modification du contrat en cours",
    ];
    form.fields.type_de_demande.choices = choices;
    if (!_.includes(choices, model.type_de_demande)) {
      model.type_de_demande = choices[0];
    }
  } else if (nature_du_recrutement === "Doctorant") {
    const choices = [
      "Contrat doctoral initial",
      "Prolongation par avenant d'un contrat doctoral en cours",
      "Prolongation par CDD d'un doctorat en cours (cas particulier)",
      "Thèse medico-scientifique",
      "Modification du contrat en cours",
    ];
    form.fields.type_de_demande.choices = choices;
    if (!_.includes(choices, model.type_de_demande)) {
      model.type_de_demande = choices[0];
    }
  } else {
    const choices = ["Contrat initial"];
    form.fields.type_de_demande.choices = choices;
    if (!_.includes(choices, model.type_de_demande)) {
      model.type_de_demande = choices[0];
    }
  }
  const type_de_demande = model.type_de_demande;

  const doctorant = nature_du_recrutement === "Doctorant";
  const modification_contrat_en_cours =
    type_de_demande === "Modification du contrat en cours";

  // Doctorant
  form.fields.co_finance.visible = doctorant;

  const show_financement2 = doctorant && model.co_finance === "oui";
  form.fields.financement2.visible = show_financement2;
  form.fields.numero_de_financement2.visible = show_financement2;

  if (model.financement2 === "Notification de financement") {
    form.fields.financement2.note =
      'Pensez à inclure la notification de financement dans l\'onglet "pièces à joindre".';
    form.fields.numero_de_financement2.visible = false;
  } else {
    form.fields.financement2.note = "";
    form.fields.numero_de_financement2.visible = show_financement2;
  }

  form.fields.structure_financeuse.visible =
    model.structures_concernees.length > 0;
  if (model.structures_concernees.length > 0) {
    const l = model.structures_concernees;
    const choices = fp.map((x) => x, l);
    choices.unshift(model.laboratoire);
    form.fields.structure_financeuse.choices = choices;
  }

  const show_similar_experience =
    nature_du_recrutement !== "Doctorant" &&
    nature_du_recrutement !== "Bourse Marie Curie" &&
    !modification_contrat_en_cours;
  form.fields.similar_experience.visible = show_similar_experience;
  const similar_experience = model.similar_experience;
  form.fields.similar_experience_years.visible =
    show_similar_experience &&
    (similar_experience === "Pour un ingénieur, technicien ou administratif" ||
      similar_experience === "Pour un chercheur");

  form.fields.ecole_doctorale.visible = doctorant;
  form.fields.fonction_du_poste.editable = !doctorant;

  // Dates
  const id_dates = get_fieldset_by_name("dates");
  const dates_visible = !(
    type_de_demande === "Modification du contrat en cours"
  );
  form.fieldsets[id_dates].visible = dates_visible;
  form.fields.date_debut.visible = dates_visible;
  form.fields.date_fin.visible = dates_visible;

  // // Durée
  // const contrat_doctoral_initial = type_de_demande === "Contrat doctoral initial";
  // //form.fields.date_fin.editable = !contrat_doctoral_initial;
  // form.fields.duree.editable = !contrat_doctoral_initial;
  // if (contrat_doctoral_initial) {
  //  if (model.duree > 36) {
  //    model.duree = 36;
  //  }
  // }
  // if (doctorant && type_de_demande.startsWith("Prolongation")) {
  //  if (model.duree > 12) {
  //    model.duree = 12;
  //  }
  // } else if (doctorant && type_de_demande.search(/médico/) >= 0) {
  //  if (model.duree > 24) {
  //    model.duree = 24;
  //  }
  // }

  const id_responsable = get_fieldset_by_name("responsable_scientifique");
  if (doctorant) {
    model.fonction_du_poste = "Doctorant";
    model.quotite_de_travail = "100%";

    form.fields.porteur.label = "Directeur de thèse";
    form.fieldsets[id_responsable].label = "Directeur de thèse";

    form.fields.quotite_de_travail.choices = ["100%"];
    form.fields.quotite_de_travail.editable = false;
  } else {
    form.fieldsets[id_responsable].label =
      "Responsable scientifique de la personne recrutée";
    form.fields.porteur.label =
      "Responsable scientifique de la personne recrutée";
    form.fields.quotite_de_travail.choices = [
      "100%",
      "90%",
      "80%",
      "70%",
      "60%",
      "50%",
    ];
    form.fields.quotite_de_travail.editable = true;
  }

  // Financement
  if (model.financement === "Notification de financement") {
    form.fields.financement.note =
      'Pensez à inclure la notification de financement dans l\'onglet "pièces à joindre".';
    form.fields.numero_de_financement.visible = false;
  } else {
    form.fields.financement.note = "";
    form.fields.numero_de_financement.visible = true;
  }

  // Pavé "Poste à pourvoir"
  form.fields.modification_mission.visible = modification_contrat_en_cours;
  let show_poste_a_pourvoir =
    !modification_contrat_en_cours || model.modification_mission === "oui";

  if (nature_du_recrutement === "Doctorant") {
    show_poste_a_pourvoir = false;
  }

  const show_grade_correspondant =
    show_poste_a_pourvoir &&
    nature_du_recrutement !== "Doctorant" &&
    nature_du_recrutement !== "Bourse Marie Curie";

  form.fields.fonction_du_poste.visible = show_poste_a_pourvoir;
  form.fields.grade_correspondant.visible = show_grade_correspondant;
  form.fields.objet_de_la_mission.visible = show_poste_a_pourvoir;
  form.fields.localisation.visible = show_poste_a_pourvoir;
  form.fields.quotite_de_travail.visible = show_poste_a_pourvoir;

  // Pavé "Rémunération"
  form.fields.modification_remuneration.visible = modification_contrat_en_cours;

  // Calculer le montant indicatif du salaire brut mensuel.
  let montant_indicatif = 0;

  const grade = model.grade_correspondant;
  let key = grade;
  if (grade === "Chercheur") {
    montant_indicatif = salaires_indicatifs.Chercheur;
  } else {
    if (grade === "Post-doctorant") {
      const salaires_postdocs = _.fromPairs(
        salaires_indicatifs["Post-doctorant"]
      );

      if (model.similar_experience === "Pour un post-doctorant: doctorat") {
        let sal = salaires_postdocs.doctorat;
        montant_indicatif = sal;
      }
      if (
        model.similar_experience ===
        "Pour un post-doctorant: doctorat plus 2 ans"
      ) {
        montant_indicatif = salaires_postdocs["doctorat-plus"];
      }
      if (
        model.similar_experience ===
        "Pour un post-doctorant: doctorat plus 3 ans"
      ) {
        montant_indicatif = salaires_postdocs["doctorat-plus-3"];
      }
    } else {
      let similar_experience_years = model.similar_experience_years;
      similar_experience_years = similar_experience_years.replace(",", ".");

      if (grade === "Technicien classe supérieure") {
        key = "technicien-sup";
      }

      if (grade === "Technicien classe normale") {
        key = "technicien-normale";
      }

      if (grade === "Adjoint technique") {
        key = "adjoint";
      }

      // The chain of if: not optimum, but readable.
      if (similar_experience_years >= 0) {
        if (similar_experience_years >= 37) {
          montant_indicatif = _.fromPairs(salaires_indicatifs[key])["37"];
        }
        if (similar_experience_years <= 36) {
          montant_indicatif = _.fromPairs(salaires_indicatifs[key])["31-36"];
        }
        if (similar_experience_years <= 30) {
          montant_indicatif = _.fromPairs(salaires_indicatifs[key])["25-30"];
        }
        if (similar_experience_years <= 24) {
          montant_indicatif = _.fromPairs(salaires_indicatifs[key])["19-24"];
        }
        if (similar_experience_years <= 18) {
          montant_indicatif = _.fromPairs(salaires_indicatifs[key])["13-18"];
        }
        if (similar_experience_years <= 12) {
          montant_indicatif = _.fromPairs(salaires_indicatifs[key])["7-12"];
        }
        if (similar_experience_years <= 6) {
          montant_indicatif = _.fromPairs(salaires_indicatifs[key])["0-6"];
        }
      }
    }
  }

  if (!model.quotite_de_travail) {
    model.quotite_de_travail = "100%";
  }
  const quotite = parseInt(model.quotite_de_travail.slice(0, -1));
  const quotite_pas_100pc = quotite !== 100;

  /*
  Lancelot: Voici ce que je comprends :
  - Soit A, un agent dont le brut mensuel ETP est X = 2349.10 euros bruts
  - Soit alpha = 80% la quotité de travail de A
  - Soit beta_alpha = 85.7% le coefficient multiplicateur de rémunération
    associé à la quotité alpha (fourni par une table ou une formule)

  Le brut mensuel de A, pour une quotité de travail de alpha = 80% est :
  Y = beta_alpha * X = 2013,18 euros bruts
  */
  let beta_alpha = quotite;
  if (quotite === 80) {
    beta_alpha = 85.7;
  }

  if (montant_indicatif !== "au cas par cas") {
    model.salaire_brut_mensuel_indicatif = (
      (montant_indicatif * beta_alpha) /
      100
    ).toFixed(2);
  } else {
    model.salaire_brut_mensuel_indicatif = "au cas par cas";
  }

  form.fields.salaire_brut_mensuel_indicatif.visible =
    nature_du_recrutement !== "Doctorant" &&
    nature_du_recrutement !== "Bourse Marie Curie" &&
    !modification_contrat_en_cours;

  // Accept both comas and points as decimal separator.
  let salaire_input = model.salaire_brut_mensuel.toString();
  if (salaire_input.indexOf(",") !== -1) {
    salaire_input = salaire_input.replace(",", ".");
    model.salaire_brut_mensuel = parseFloat(salaire_input);
  }

  const needs_justification =
    model.salaire_brut_mensuel &&
    montant_indicatif &&
    montant_indicatif !== "au cas par cas" &&
    parseFloat(model.salaire_brut_mensuel_indicatif) !==
      parseFloat(model.salaire_brut_mensuel);
  form.fields.salaire_justification.visible = needs_justification;
  form.fields.salaire_justification.required = needs_justification;

  const show_remuneration =
    !modification_contrat_en_cours || model.modification_remuneration === "oui";
  form.fields.salaire_brut_mensuel.visible = show_remuneration;
  form.fields.indemnite_transport_en_commun.visible = show_remuneration;
  form.fields.nombre_enfants_a_charge.visible = show_remuneration;

  // const brut_min = 1684.93;
  const brut_min = form.constants.recrutement.salaire_min_doctorant;

  const salaire_brut_mensuel_etp = (
    (model.salaire_brut_mensuel * 100.0) /
    beta_alpha
  ).toFixed(2);
  form.fields.salaire_brut_mensuel_etp.visible =
    show_remuneration && quotite_pas_100pc;
  if (show_remuneration && quotite && quotite_pas_100pc) {
    model.salaire_brut_mensuel_etp = salaire_brut_mensuel_etp;
  }

  // Demande de recrutement pour : Doctorant, contrat initial
  // Montant du salaire brut mensuel :
  // si le montant rentré est inférieur à 1684.93 €, la mention
  // "Le salaire minimum d'un doctorant est 1684.93 €." doit apparaître
  // quand il est supérieur ou égal à 1938 €, un champ de justification apparaît,
  // c'est bien mais il doit être accompagné de la mention
  // "Ce salaire est supérieur de 15% au salaire brut minimum d'un doctorant,
  // pouvez-vous expliquer pourquoi ?".

  const types_demandes_doctorant = [
    "Contrat doctoral initial",
    "Prolongation par avenant d'un contrat doctoral en cours",
    "Prolongation par CDD d'un doctorat en cours (cas particulier)",
  ];

  if (
    show_remuneration &&
    doctorant &&
    types_demandes_doctorant.indexOf(type_de_demande) >= 0
  ) {
    if (model.salaire_brut_mensuel * 1.0 < brut_min) {
      model.salaire_brut_mensuel = brut_min;
      form.fields.salaire_brut_mensuel.note =
        "Le salaire minimum d'un doctorant est " + brut_min + " €";
      form.fields.justification_du_salaire.note = "";
    } else if (model.salaire_brut_mensuel * 1.0 > 1.15 * brut_min) {
      form.fields.justification_du_salaire.note =
        "Ce salaire est supérieur de 15% au salaire brut minimum d'un doctorant, pouvez-vous expliquer pourquoi ?";
    } else {
      form.fields.justification_du_salaire.note = "";
    }
  } else {
    form.fields.justification_du_salaire.note = "";
  }

  form.fields.justification_du_salaire.visible =
    show_remuneration &&
    doctorant &&
    model.salaire_brut_mensuel * 1.0 > 1.15 * brut_min;
  form.fields.justification_du_salaire.note =
    "Ce salaire est supérieur de 15% au salaire brut minimum d'un doctorant, pouvez-vous expliquer pourquoi ?";

  // Pavé "Autre modification"
  const id_autre_modification = get_fieldset_by_name("autre_modification");
  form.fieldsets[id_autre_modification].visible = modification_contrat_en_cours;
  form.fields.modification_autre.visible = modification_contrat_en_cours;

  const show_modification_autre_detail =
    modification_contrat_en_cours && model.modification_autre === "oui";
  if (typeof form.fields.modification_autre_detail !== "undefined") {
    form.fields.modification_autre_detail.visible = show_modification_autre_detail;
  }

  // Pavé "Publicité"
  const show_publicite =
    type_de_demande === "Contrat initial" ||
    type_de_demande === "Contrat doctoral initial" ||
    nature_du_recrutement === "Bourse Marie Curie";

  const id_pub = get_fieldset_by_name("publicite");
  form.fieldsets[id_pub].visible = show_publicite;
  form.fields.publicite.visible = show_publicite;
  form.fields.nb_candidats_recus.visible = show_publicite;

  // Dates
  if (
    model.date_debut &&
    model.date_fin &&
    model.date_fin <= model.date_debut
  ) {
    form.fields.date_fin.note =
      "La date de fin doit être postérieure à la date de début.";
  } else {
    form.fields.date_fin.note = "";
  }
}
