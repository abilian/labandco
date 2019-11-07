import Vue from "vue";
import Router from "vue-router";
import axios from "axios";

import Home from "../pages/home/Home";
import Tasks from "../pages/home/Tasks";
import Demandes from "../pages/home/Demandes";
import DemandesEnRetard from "../pages/home/DemandesEnRetard";
import Archives from "../pages/home/Archives";

import Structures from "../pages/annuaire/Structures";
import Structure from "../pages/annuaire/Structure";

import Users from "../pages/annuaire/Users";
import User from "../pages/annuaire/User";

import Faq from "../pages/faq/Faq";
import Message from "../pages/faq/Message";

import Search from "../pages/search/Search";
import Timeline from "../pages/tools/Timeline";
import Contacts from "../pages/tools/Contacts";
import Preferences from "../pages/tools/Preferences";

import DemandeEdit from "../pages/demandes/DemandeEdit";
import DemandeView from "../pages/demandes/DemandeView";

import NouvelleDemande from "../pages/forms/NouvelleDemande";

Vue.use(Router);

const router = new Router({
  base: __dirname,
  mode: "hash",
  // mode: "history",

  scrollBehavior: () => ({ y: 0 }),

  routes: [
    // Home & t￿âches
    {
      path: "/",
      component: Home,
    },
    {
      path: "/tasks",
      component: Tasks,
    },
    {
      path: "/demandes",
      component: Demandes,
    },
    {
      path: "/demandes_en_retard",
      component: DemandesEnRetard,
    },
    {
      path: "/archives",
      component: Archives,
    },

    // Annuaires
    {
      name: "structures",
      path: "/annuaire/structures",
      component: Structures,
    },
    {
      name: "structure",
      path: "/annuaire/structures/:id",
      component: Structure,
      props: true,
    },
    {
      path: "/annuaire/users",
      component: Users,
    },
    {
      name: "user",
      path: "/annuaire/users/:id",
      component: User,
      props: true,
    },

    // Demandes
    {
      name: "nouvelle_demande",
      path: "/demandes/new/:type",
      component: NouvelleDemande,
      props: true,
    },

    {
      name: "demande",
      path: "/demandes/:id",
      component: DemandeView,
      props: true,
    },
    {
      path: "/demandes/:id/edit",
      component: DemandeEdit,
    },

    // Faq
    {
      path: "/faq",
      component: Faq,
    },
    {
      path: "/faq/message",
      component: Message,
    },

    // Tools
    {
      path: "/timeline",
      component: Timeline,
    },
    {
      path: "/contacts",
      component: Contacts,
    },
    {
      path: "/preferences",
      component: Preferences,
    },
    {
      path: "/search",
      component: Search,
      props: route => ({ q: route.query.q }),
    },
  ],

  meta: {
    progress: {
      func: [
        { call: "color", modifier: "temp", argument: "#ffb000" },
        { call: "fail", modifier: "temp", argument: "#6e0000" },
        { call: "location", modifier: "temp", argument: "top" },
        {
          call: "transition",
          modifier: "temp",
          argument: { speed: "1.5s", opacity: "0.6s", termination: 400 },
        },
      ],
    },
  },
});

router.beforeEach((to, from, next) => {
  const url = "/v3/api/ui-context";
  let user = Vue.$storage.get("user");

  if (!user) {
    axios.get(url).then(response => {
      const data = response.data;

      Vue.$storage.set("user", data.user);
      Vue.$storage.set("menu", data.menu);
      next();
    });
  } else {
    next();
  }
});

export default router;
