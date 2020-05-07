<template>
  <div>
    <p v-if="demande.errors.length" class="text-red mt-4 mb-4">
      Attention, votre demande est encore incomplète sur les champs suivants:
      <span v-for="error in demande.errors"
        ><b v-html="form.fields[error].label" />.
      </span>
    </p>

    <p v-if="demande.extra_errors.length" class="text-red mt-4 mb-4">
      Merci de prendre en compte les points suivants:
      <span v-for="error in demande.extra_errors" class="text-bold"
        >{{ error }}
      </span>
    </p>

    <template v-for="fieldset in form.fieldsets">
      <fieldset v-if="fieldset.visible">
        <legend>{{ fieldset.label }}</legend>

        <div :id="'fieldset-' + fieldset.name">
          <table class="table table-striped table-bordered">
            <form-view-line
              v-for="fieldName in fieldset.fields"
              :visible="form.fields[fieldName].visible"
              :key="'fm-' + fieldName"
              :field="form.fields[fieldName]"
              :value="demande.form_data[fieldName]"
              :has_error="demande.errors.indexOf(fieldName) >= 0"
            />
          </table>
        </div>
      </fieldset>
    </template>
  </div>
</template>

<script>
import FormViewLine from "./FormViewLine";

export default {
  props: { demande: Object, form: Object },

  components: { FormViewLine },
};
</script>
