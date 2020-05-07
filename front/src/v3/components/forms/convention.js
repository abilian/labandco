export default function update_convention(form, model) {
  const lien_contrat = model.lien_contrat === "oui";

  form.fields.eotp_ou_no_dgrtt.visible = lien_contrat;

  const show_nom_financeur =
    model.type_financeur !== "Commission Européenne" &&
    model.type_financeur !== "ANR";

  form.fields.nom_financeur.visible = show_nom_financeur;

  form.fields.type_contrat.visible = model.appel_a_projets === "non";

  // On cache la section "partenaires" dans le cas d'un appel à projets
  form.fieldsets[6].visible = model.appel_a_projets === "non";

  if (model.appel_a_projets === "oui") {
    form.fields.appel_a_projets.note =
      "Dans le cas d’un appel à projet, la liste des partenaires est à renseigner dans les pièces jointes et n’a pas à être décrite ici.";
  } else {
    form.fields.appel_a_projets.note = "";
  }

  form.fields.integre_entreprise.visible =
    model.type_financeur !== "Entreprise";

  const v1 = model.materiel_donnees === "oui";
  form.fields.materiel_donnees_propre_upmc.visible = v1;
  form.fields.materiel_donnees_obtenu_precedents_contrats.visible = v1;
  form.fields.materiel_donnees_humains.visible = v1;
  form.fields.materiel_donnees_infectieux.visible = v1;
  form.fields.materiel_donnees_description.visible = v1;

  const v2 = model.savoir_faire === "oui";
  form.fields.savoir_faire_propre_upmc.visible = v2;
  form.fields.savoir_faire_obtenu_precedents_contrats.visible = v2;
  form.fields.savoir_faire_description.visible = v2;

  const v3 = model.logiciel === "oui";
  form.fields.logiciel_propre_upmc.visible = v3;
  form.fields.logiciel_obtenu_precedents_contrats.visible = v3;
  form.fields.logiciel_libre.visible = v3;
  form.fields.logiciel_description.visible = v3;

  const v4 = model.brevet === "oui";
  form.fields.brevet_propre_upmc.visible = v4;
  form.fields.brevet_obtenu_precedents_contrats.visible = v4;
  form.fields.brevet_description.visible = v4;
}
