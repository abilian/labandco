<template>
  <ul class="timeline">
    <template v-for="g in groups">
      <li class="time-label">
        <span class="bg-red">{{ g[0].date }}</span>
      </li>

      <li v-for="notification in g">
        <i v-bind:class="[notification.demande.icon_class, 'bg-blue']" />

        <div class="timeline-item">
          <span class="time">
            <i class="far fa-clock" />
            {{ notification.created_at }}
          </span>

          <h3 class="timeline-header">
            {{ notification.demande.nom }}
          </h3>

          <div class="timeline-body" v-html="notification.body"></div>

          <div class="timeline-footer">
            <router-link
              :to="{ name: 'demande', params: { id: notification.demande.id } }"
              class="btn btn-primary btn-flat btn-sm"
              >Voir la demande</router-link
            >
          </div>
        </div>
      </li>
    </template>

    <li>
      <i class="far fa-clock bg-gray"></i>
    </li>
  </ul>
</template>

<script>
import fp from "lodash/fp";
import { ContextFetcher } from "../../mixins";

export default {
  mixins: [ContextFetcher],

  data() {
    return {
      notifications: [],
      groups: [],
    };
  },

  methods: {
    whenReady() {
      this.groups = fp.flow(
        fp.groupBy("date"),
        fp.sortBy("date")
      )(this.notifications);
    },
  },
};
</script>
