<template>
  <b-card no-body>
    <div class="card-header">
      <h3 class="card-title">Actions possibles</h3>
    </div>

    <div v-if="demande" class="card-body">
      <button
        v-if="demande.is_editable"
        @click="onClick"
        name="action-modifier"
        class="btn btn-primary m-2"
      >
        Modifier la demande
      </button>

      <button
        v-if="demande.is_duplicable"
        @click="onClick"
        name="dupliquer"
        class="btn btn-default m-2"
      >
        Dupliquer la demande
      </button>

      <button
        v-for="transition in demande.workflow.transitions"
        type="submit"
        :class="`btn btn-${transition.category} m-2`"
        :value="transition.id"
        @click="onClick"
        name="action"
      >
        {{ transition.label }}
      </button>
    </div>

    <template v-for="transition in demande.workflow.transitions">
      <b-modal
        :id="'confirm-modal-' + transition.id"
        :key="transition.id"
        hide-footer
        size="lg"
      >
        <template v-slot:modal-title>
          Confirmer l'action "{{ transition.label }}"
        </template>

        <p>
          Êtes-vous sûr de vouloir effectuer l'action "{{ transition.label }}"
          sur la demande "{{ demande.nom }}" ?
        </p>

        <p>
          A cet effet, merci de bien vouloir compléter les informations
          suivantes (les champs suivis d'un astérisque sont obligatoires):
        </p>

        <div class="form-horizontal">
          <div v-for="field in transition.form" :key="field.name">
            <template v-if="field.type === 'textarea'">
              <div class="text-bold mt-3">
                {{ field.label }}
                <span v-if="field.required" class="text-red">(*)</span>
              </div>
              <b-form-textarea
                v-model="model.note"
                :required="field.required"
                rows="6"
                max-rows="10"
              />
            </template>

            <template v-else-if="field.type === 'text'">
              <div class="text-bold mt-3">
                {{ field.label }}
                <span v-if="field.required" class="text-red">(*)</span>
              </div>
              <b-form-input
                type="text"
                v-model="model[field.name]"
                :required="field.required"
              />
            </template>

            <template v-else-if="field.type === 'bool'">
              <b-form-checkbox v-model="model[field.name]" class="my-3">
                {{ field.label }}
              </b-form-checkbox>
            </template>

            <div v-else>TODO: {{ field }}</div>
          </div>

          <!-- -->

          <div class="text-center mt-4">
            <button class="btn btn-primary" @click="confirm(transition)">
              Confirmer l'action
            </button>
            <span class="ml-4" />
            <button class="btn btn-danger" @click="cancel(transition)">
              Annuler
            </button>
          </div>
        </div>
      </b-modal>
    </template>
  </b-card>
</template>

<script>
export default {
  props: { demande: Object },

  data: function () {
    const model = {
      note: "",
    };
    return {
      model: model,
    };
  },

  methods: {
    onClick(e) {
      const button = e.target;
      const buttonName = button.name;

      if (buttonName === "action-modifier") {
        this.$parent.goToTab("Formulaire");
      } else if (buttonName === "action") {
        this.$bvModal.show("confirm-modal-" + button.value);
      } else if (buttonName === "dupliquer") {
        this.duplicate();
      }
    },

    cancel(transition) {
      this.$bvModal.hide("confirm-modal-" + transition.id);
    },

    confirm(transition) {
      for (let i = 0; i < transition.form.length; i++) {
        const field = transition.form[i];
        if (field.required && !this.model[field.name]) {
          this.$root.$bvToast.toast(
            "Vous devez remplir les champs obligatoires",
            {
              title: "",
              variant: "danger",
              solid: true,
            }
          );
          return;
        }
      }

      const args = {
        demande_id: this.demande.id,
        action: transition.id,
        data: this.model,
      };
      this.$root.rpc("wf_transition", args).then((result) => {
        const msg = result;
        this.$router.go();
        this.$root.$bvToast.toast(msg[0], {
          title: "",
          variant: msg[1],
          solid: true,
        });
      });
    },

    duplicate() {
      this.$root.rpc("dupliquer_demande", [this.demande.id]).then((result) => {
        if (!result) {
          const msg = "La duplication de la demande a échoué";
          this.$root.$bvToast.toast(msg, {
            title: "",
            variant: "danger",
            solid: true,
          });
          return;
        }

        const msg = "Demande dupliquée avec succès";
        this.$router.push({ path: `/demandes/${result}` });
        this.$router.go();
        this.$root.$bvToast.toast(msg, {
          title: "",
          variant: "success",
          solid: true,
        });
      });
    },
  },
};
</script>
