<template>
  <div>
    <a :name="'field-' + field.name" />

    <template v-if="field.type[0] === 'HTML'">
      <div v-html="field.label" />
    </template>

    <template v-if="field.type[0] !== 'HTML' && !field.scalar">
      <Component :is="subcomponent" :field="field" :model="model" />
    </template>

    <div
      v-if="field.type[0] !== 'HTML' && field.scalar"
      v-show="field.visible"
      :id="'field-' + field.name"
      class="form-group"
    >
      <label :for="field.id" class="control-label col-sm-4">
        <span v-html="field.label" />&nbsp;<template v-if="field.required">
          (<span class="text-red">*</span>)
        </template>
      </label>

      <div class="col-sm-6">
        <Component :is="subcomponent" :field="field" :model="model" />

        <div v-if="field.note">
          <em v-html="field.note" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from "lodash";

// Scalars
import StringWidget from "./widgets/string-widget.vue";
import IntegerWidget from "./widgets/integer-widget.vue";
import EmailWidget from "./widgets/email-widget.vue";
import DateWidget from "./widgets/date-widget.vue";
import SelectWidget from "./widgets/select-widget.vue";
import TextAreaWidget from "./widgets/textarea-widget.vue";
import BooleanWidget from "./widgets/boolean-widget.vue";
import YesNoWidget from "./widgets/yesno-widget.vue";
import TriStateWidget from "./widgets/tri-state-widget.vue";
// listes
import ListePartenairesWidget from "./widgets/liste-partenaires-widget.vue";
import ListeDivulgationsPasseesWidget from "./widgets/liste-divulgations-passees.vue";
import ListeDivulgationsFuturesWidget from "./widgets/liste-divulgations-futures.vue";
import ListeContratsWidget from "./widgets/liste-contrats.vue";
import ListeMaterielsWidget from "./widgets/liste-materiels.vue";
import ListeAutresDeclarationsWidget from "./widgets/liste-autres-declarations.vue";
import ListeLicencesExistantesWidget from "./widgets/liste-licences-existantes.vue";
import ListePartenairesContactesWidget from "./widgets/liste-partenaires-contactes-widget.vue";

const components = {
  // Scalars
  StringWidget,
  IntegerWidget,
  EmailWidget,
  DateWidget,
  TextAreaWidget,
  SelectWidget,
  BooleanWidget,
  YesNoWidget,
  TriStateWidget,
  // Listes
  ListePartenairesWidget,
  ListeDivulgationsPasseesWidget,
  ListeDivulgationsFuturesWidget,
  ListeContratsWidget,
  ListeMaterielsWidget,
  ListeAutresDeclarationsWidget,
  ListeLicencesExistantesWidget,
  ListePartenairesContactesWidget,
};

function fieldTypeToWidgetName(fieldType) {
  const type = fieldType;
  if (type === "BooleanField") {
    return "yes-no-widget";
  }
  if (type === "Boolean2Field") {
    return "boolean-widget";
  }
  if (type === "Select2Field") {
    return "select-widget";
  }
  let name = _.kebabCase(type);
  if (name.endsWith("-field")) {
    name = name.slice(0, -"-field".length);
  }
  return name + "-widget";
}

export default {
  name: "FormGroup",

  components: components,

  props: {
    fieldName: { type: String, required: true },
    model: { type: Object, required: true },
    form: { type: Object, required: true },
  },

  data: function() {
    const field = this.form.fields[this.fieldName];
    return {
      field: field,
      subcomponent: fieldTypeToWidgetName(field.type[0]),
    };
  },
};
</script>
