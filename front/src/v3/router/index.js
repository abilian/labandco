import Vue from "vue";
import Router from "vue-router";
import rpc from "../rpc";

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

import DemandeView from "../pages/demandes/DemandeView";

import NouvelleDemande from "../pages/forms/NouvelleDemande";

import BiHome from "../pages/bi/BiHome";

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
      name: "demande.new",
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

    // Faq
    {
      name: "faq",
      path: "/faq",
      component: Faq,
    },
    {
      path: "/faq/message",
      component: Message,
    },

    // Tools
    {
      name: "timeline",
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

    // BI
    {
      name: "bi",
      path: "/bi",
      component: BiHome,
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
  if (!Vue.$storage.has("user_context")) {
    rpc("get_user_context", []).then(data => {
      Vue.$storage.set("user_context", data);
      next();
    });
  } else {
    next();
  }
});

export default router;
