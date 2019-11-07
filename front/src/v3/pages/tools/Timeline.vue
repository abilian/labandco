<template>
  <ul class="timeline">
    <template v-for="g in groups">
      <li class="time-label">
        <span class="bg-red">{{ g[0] }}</span>
      </li>

      <li v-for="notification in g[1]">
        <i v-bind:class="[notification.demande.icon_class, 'bg-blue']"></i>

        <div class="timeline-item">
          <span class="time">
            <i class="far fa-clock"></i>
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
import axios from "axios";
import _ from "lodash";

const URL = "/v3/api/user/timeline";

export default {
  name: "Timeline",

  data() {
    return {
      groups: [],
    };
  },
  created() {
    axios.get(URL).then(response => {
      const data = response.data;
      const groups1 = _.groupBy(data.notifications, "date");
      const groups2 = _.map(groups1, (value, key) => [key.slice(0, 16), value]);
      const groups3 = _.sortBy(groups2);
      this.groups = groups3;
    });
  },
};
</script>
