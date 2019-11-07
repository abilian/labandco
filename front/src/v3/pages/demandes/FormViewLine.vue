<template>
  <tr>
    <!--      {% if has_error %}-->
    <!--        <td v-html="field.label" class="col-md-4 text-danger text-right"></td>-->
    <!--        <td class="col-md-8 text-danger">-->
    <!--          [A compléter]-->
    <!--          {% if demande.is_editable_by(g.current_user) %}-->
    <!--            <a-->
    <!--                href="{{ url_for(".demande_edit", id=demande.id) + "#field-" + field.name }}"><i-->
    <!--                class="far fa-pencil"></i></a>-->
    <!--          {% endif %}-->
    <!--        </td>-->

    <!--      {% elif field_type == 'ListePartenaires' %}-->
    <!--        {{ display_list(field, value, [-->
    <!--          ['nom_partenaire', "Nom du partenaire"],-->
    <!--          ['prenom_nom_contact', "Contact"],-->
    <!--          ['mail_contact', "Email"],-->
    <!--          ['telephone_contact', "Téléphone"],-->
    <!--          ]) }}-->

    <!--      {% elif field.name == 'liste_autres_declarations' %}-->
    <!--        {{ display_list(field, value, [-->
    <!--          ['type_protection', "Type de protection"],-->
    <!--          ['organisme', "Organisme ayant fait le dépôt"],-->
    <!--          ['exploitation', "Exploitation industrielle"],-->
    <!--          ]) }}-->

    <!--      {% elif field.name == 'liste_contrats' %}-->
    <!--        {{ display_list(field, value, [-->
    <!--          ['contrat', "Contrat/Partenariat de recherche"],-->
    <!--          ['date_signature', "Date de signature du contrat"],-->
    <!--          ['reference', "Référence du contrat"],-->
    <!--          ]) }}-->

    <!--      {% elif field.name == 'liste_licences_existantes' %}-->
    <!--        {{ display_list(field, value, [-->
    <!--          ['type_licence', "Type de la licence"],-->
    <!--          ['nom_version_licence', "Nom et version de la licence"],-->
    <!--          ]) }}-->

    <!--      {% elif field.name == 'liste_divulgations_passees' %}-->
    <!--        {{ display_list(field, value, [-->
    <!--          ['type_divulgation', "Type de divulgation"],-->
    <!--          ['titre', "Titre"],-->
    <!--          ['date_lieu', "Date et lieu"],-->
    <!--          ]) }}-->

    <!--      {% elif field.name == 'liste_divulgations_futures' %}-->
    <!--        {{ display_list(field, value, [-->
    <!--          ['type_divulgation', "Type de divulgation"],-->
    <!--          ['date', "Date envisagée"],-->
    <!--          ]) }}-->

    <!--      {% elif field.name == 'liste_materiels' %}-->
    <!--        {{ display_list(field, value, [-->
    <!--          ['materiel', "Matériel"],-->
    <!--          ]) }}-->

    <!--      {% elif field.name == 'liste_partenaires_contactes' %}-->
    <!--        {{ display_list(field, value, [-->
    <!--          ['contact', "Contact"],-->
    <!--          ['nom_partenaire', "Nom du partenaire"],-->
    <!--          ]) }}-->

    <!--      {% else %}-->
    <td v-html="field.label" class="w-30 text-muted text-right"></td>
    <td class="w-70">
      <span v-if="value" v-html="value"></span>
    </td>
  </tr>
</template>

<script>
export default {
  props: { field: Object, value: [Object, String, Number], has_error: Boolean },

  data() {
    return {
      field_type: this.field.type[0],
    };
  },
};
</script>
