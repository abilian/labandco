export default function update_pi_logiciel(form, model) {
  const fields = form.fields;

  fields.precision_type_oeuvre.visible = model.type_oeuvre === "Autre";
  fields.logiciel_compose_details.visible = model.originalite.startsWith(
    "logiciel composé"
  );
  fields.logiciel_derive_details.visible = model.originalite.startsWith(
    "logiciel dérivé"
  );

  fields.precision_negociations.visible = model.negociations === "oui";
  fields.precision_code_publie.visible = model.code_publie === "oui";
  fields.precision_communication_prevue.visible =
    model.communication_prevue === "oui";

  fields.liste_autres_declarations.visible =
    model.autres_declarations === "oui";
  fields.liste_licences_existantes.visible =
    model.licences_existantes === "oui";
  fields.liste_contrats.visible = model.contrats === "oui";
}
