<template>
  <span id="app">
    <button
      id="show-modal"
      type="button"
      class="btn btn-default btn-sm pull"
      aria-label="settings"
      @click="showModal = true"
    >
      <span class="far fa-cog" style="margin-top: 3px" aria-hidden="true" />
    </button>

    <modal
      v-if="showModal"
      :columns="columns"
      @close="showModal = false"
      @columnsChanged="onColumnsChanged"
    >
      <!--
        you can use custom content here to overwrite
        default content. (use slot="header/body/footer")
      -->
      <div slot="header">
        <h3 slot="header">
          Options de visualisation
        </h3>
        <em>
          Glissez-déposez des éléments pour les trier et sélectionnez les
          colonnes à afficher.
        </em>
      </div>
      <div id="modal-body" slot="body">
        <Draggable v-model="columns2">
          <TransitionGroup>
            <div
              v-for="col in columns2"
              :key="col.label"
              class="list-group-item"
            >
              <input
                v-model="col.__show__"
                type="checkbox"
                style="margin-right: 5px"
              />
              {{ col.label }}
              <i class="far fa-bars float-right" style="cursor: move" />
            </div>
          </TransitionGroup>
        </Draggable>
      </div>
    </modal>
  </span>
</template>

<script>
import Modal from "./modal.vue";
import Draggable from "vuedraggable";

export default {
  name: "SelectColumns",

  components: { Modal, Draggable },
  props: ["columns"],

  data: function() {
    return {
      showModal: false,
      columns2: null,
    };
  },

  mounted: function() {
    this.columns2 = this.columns;
  },

  methods: {
    onColumnsChanged: function(data) {
      this.$emit("columnsChanged", this.columns2);
    },
  },
};
</script>
