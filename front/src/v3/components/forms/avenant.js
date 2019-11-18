export default function update_avenant(form, model) {
  form.fields.nouvelle_date_fin.visible = model.duree === "oui";

  form.fields.message_montant.visible = model.montant === "oui";
  form.fields.nouveau_montant.visible = model.montant === "oui";

  form.fields.message_programme_scientifique.visible =
    model.programme_scientifique === "oui";

  form.fields.autre_precisez.visible = model.autre === "oui";

  const consortium = model.consortium === "oui";

  form.fields.ajouter_partenaires.visible = consortium;
  form.fields.partenaires_a_ajouter.visible =
    consortium && model.ajouter_partenaires === "oui";

  form.fields.modifier_partenaires.visible = consortium;
  form.fields.partenaires_a_modifier.visible =
    consortium && model.modifier_partenaires === "oui";

  form.fields.retirer_partenaires.visible = consortium;
  form.fields.partenaires_a_retirer.visible =
    consortium && model.retirer_partenaires === "oui";
}
