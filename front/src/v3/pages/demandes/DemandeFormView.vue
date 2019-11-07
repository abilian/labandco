<template>
  <!--{% macro display_list(field, value, specs) %}-->
  <!--  <td class="col-md-4 text-muted text-right">{{ field.label|safe }}</td>-->
  <!--  <td class="col-md-8">-->
  <!--    <table class="table" style="width: 100%; margin-bottom: 0;">-->
  <!--      <tr>-->
  <!--        {% for attr_name, label in specs %}-->
  <!--          <th class="text-muted" style="font-weight: normal;">{{ label }}</th>-->
  <!--        {% endfor %}-->
  <!--      </tr>-->
  <!--      {% for item in value %}-->
  <!--        {% if item %}-->
  <!--          <tr>-->
  <!--            {% for attr_name, label in specs %}-->
  <!--              <td>{{ item.get(attr_name, '') }}</td>-->
  <!--            {% endfor %}-->
  <!--          </tr>-->
  <!--        {% endif %}-->
  <!--      {% endfor %}-->
  <!--    </table>-->
  <!--  </td>-->
  <!--{% endmacro %}-->

  <!--{% set form_state = demande.form_state %}-->
  <!--{% set demande_errors = demande.errors %}-->

  <div>
    <div v-for="fieldset in form.fieldsets">
      <div v-if="fieldset.visible" :id="'fieldset-' + fieldset.name">
        <h3 class="mt-4">{{ fieldset.label }}</h3>

        <table class="table table-striped table-bordered">
          <form-view-line
            v-for="fieldName in fieldset.fields"
            :key="fieldName"
            :field="form.fields[fieldName]"
            :value="demande.form_data[fieldName]"
            :has_error="false"
          />

          <!--          {{-->
          <!--            field.name-->
          <!--          }}-->

          <!--        {%- for field in fieldset.fields %}-->
          <!--          {% set field_name = field.name %}-->
          <!--          {% if field_name %}-->
          <!--            {% set field_state = form_state.fields.get(field_name) %}-->
          <!--            {% if field_state and field_state.visible is defined and field_state.visible %}-->
          <!--              {% set has_error = field_name in demande_errors %}-->
          <!--              {% set value = field.get_display_value(demande) %}-->

          <!--              {{ m_line(field_state, value, has_error) }}-->
          <!--            {% endif %}-->
          <!--          {% endif %}-->
          <!--        {%- endfor %}-->
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import FormViewLine from "./FormViewLine";

export default {
  name: "DemandeFormView",
  props: { demande: Object, form: Object },

  components: { FormViewLine },

  created() {
    console.log("Demande:", this.demande);
    console.log("Form:", this.form);
  },
};
</script>
