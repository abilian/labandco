export default function update_pi_invention(form, model) {
  const fields = form.fields;

  fields.precision_partenaires.visible = model.partenaires === "oui";
  fields.liste_partenaires_contactes.visible =
    model.partenaires_contactes === "oui";
  fields.precision_creation_entreprise.visible =
    model.creation_entreprise === "oui";

  fields.recherche_bases_brevets_detail_1.visible =
    model.recherche_bases_brevets === "oui";
  fields.recherche_bases_brevets_detail_2.visible =
    model.recherche_bases_brevets === "oui";
  fields.recherche_bases_brevets_detail_1.visible =
    model.recherche_bases_brevets === "oui";

  fields.publications_proches_details.visible =
    model.publications_proches === "oui";

  fields.liste_divulgations_passees.visible =
    model.divulgations_passees === "oui";
  fields.liste_divulgations_futures.visible =
    model.divulgations_futures === "oui";
  fields.liste_contrats.visible = model.contrats === "oui";
  fields.liste_materiels.visible = model.materiels === "oui";

  const depot_anterieur = model.depot_anterieur === "oui";
  fields.depot_anterieur_detail.visible = depot_anterieur;
  fields.depot_anterieur_gere_par_upmc.visible = depot_anterieur;
  fields.depot_anterieur_gere_par.visible =
    depot_anterieur && model.depot_anterieur_gere_par_upmc === "non";
}
