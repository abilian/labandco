// Testing Constants Editor component.
// https://vue-test-utils.vuejs.org/en/guides/getting-started.html

import { mount } from "vue-test-utils";

import ConstantsEditor from "@/admin2/constantsEditor.vue";

const constants = {
  // Types should be specified on leaves.
  // They are not mandatory.
  faq_categories: [
    "Conventions de recherche \u2013 g\u00e9n\u00e9ralit\u00e9s",
    "Gestion financi\u00e8re d\u2019un contrat",
    "Ressources humaines",
  ],
  nom_bureaux_dgrtt: {
    // we can safely guess the String type.
    MSAR: "Moyens et suivi des activit\u00e9s de recherche",
    PIJ: "Propri\u00e9t\u00e9 intellectuelle (juriste)",
    ETT: "Entreprises et transfert de technologie",
    AIPI: "Propri\u00e9t\u00e9 intellectuelle",
    CC: "Coordination et communication",
    CFE: "Contrats et financements europ\u00e9ens",
    GF: "Gestion financi\u00e8re des contrats",
    EU: "Contrats et financements europ\u00e9ens",
    PI2: "Propri\u00e9t\u00e9 intellectuelle 2",
    CP: "Contrats publics",
    REF: "R\u00e9f\u00e9rents",
    DIR: "Direction DGRTT",
    CT: "Contrats de travail",
  },
  recrutement: {
    provision_risque_charge_employeur: {
      type: "Integer",
      val: 8,
    },
    salaire_min_doctorant: 2000,
    grades: ["IR", "IE", "ASI", "Tech", "Chercheur", "ARC", "Autre"],
    ecoles_doctorales: [
      "ED 127 : Astronomie et astrophysique d'\u00cele-de-France",
      "ED 129 : Sciences de l'environnement d'\u00cele-de-France",
      "ED 130 : Informatique, t\u00e9l\u00e9communications et \u00e9lectronique de Paris",
      "ED 158 : Cerveau, cognition, comportement (3C)",
      "ED 227 : Sciences de la Nature et de l'Homme : \u00e9cologie & \u00e9volution",
      "ED 386 : Sciences math\u00e9matiques de Paris Centre",
      "ED 388 : Chimie physique et chimie analytique de Paris Centre",
      "ED 391 : Sciences m\u00e9caniques, acoustique, \u00e9lectronique et robotique de Paris (SMAER)",
      "ED 393 : Sant\u00e9 publique : \u00e9pid\u00e9miologie et sciences de l'information biom\u00e9dicale",
      "ED 394 : Physiologie, physiopathologie et th\u00e9rapeutique",
      "ED 397 : Physique et chimie des mat\u00e9riaux",
      "ED 398 : G\u00e9osciences, ressources naturelles et environnement",
      "ED 406 : Chimie mol\u00e9culaire de Paris-Centre",
      "ED 515 : Complexit\u00e9 du vivant",
      "ED 560 : Sciences de la Terre et Physique de l'univers",
      "ED 564 : Physique en \u00cele-de-France",
    ],
    principes:
      "<h4>Les trois principes r\u00e9gissant les contrats de travail de Sorbonne Universités</h4>\n\n<ul>\n<li>\nLa mobilit\u00e9 apr\u00e8s la th\u00e8se\n<br/>\nUne personne ayant effectu\u00e9 sa th\u00e8se dans un laboratoire ne peut pas\n\u00eatre accueillie en contrat post-doctoral dans le m\u00eame laboratoire. Le\nconseil scientifique de Sorbonne Universités a adopt\u00e9 un code de conduite sur\nl\u2019accueil de chercheurs post-doctoraux en 2011.\n</li>\n<li>\nLe contrat doctoral de trois ans\n<br/>\nLe contrat doctoral, d\u00e9fini par le d\u00e9cret n\u00b02009-464 du 23 avril 2009\nrelatif aux doctorants contractuels, est un CDD de droit public de\ntrois ans. Il a \u00e9t\u00e9 mis en place \u00e0 Sorbonne Universités en septembre 2009.\n</li>\n<li>\nPas plus de trois ans de CDD\n<br/>\nSorbonne Universités n\u2019accepte pas de prolonger un CDD au-del\u00e0 de 3 ans. Ce principe\nvisant \u00e0 lutter contre la pr\u00e9carit\u00e9 de l\u2019emploi est inscrit dans le\nd\u00e9cret du Saic n\u00b02002-1347 du 7 novembre 2002. Il s\u2019appr\u00e9cie en\nincluant les autres employeurs publics partenaires du laboratoire.\n<br/>\nExceptionnellement, dans l\u2019int\u00e9r\u00eat de la personne recrut\u00e9e, une\nprolongation au-del\u00e0 des trois ans est possible (par exemple, pour\nattendre une mobilit\u00e9 programm\u00e9e). Une telle prolongation n\u00e9cessite un\narbitrage de la DGRTT et ne peut \u00eatre obtenue qu\u2019une seule fois.\n</li>\n</ul>\n\n<h4>Ce que l\u2019on ne peut pas ignorer quand on souhaite recruter sur\nconvention de recherche</h4>\n<ul>\n<li>\nIl est ill\u00e9gal de faire travailler une personne sans qu\u2019elle ait sign\u00e9\nun contrat de travail. Les risques encourus par le directeur d\u2019unit\u00e9\net le pr\u00e9sident de l\u2019universit\u00e9 sont civils et p\u00e9naux.\n</li>\n<li>Depuis d\u00e9cembre 2013, la recette g\u00e9n\u00e9rale des finances qui traite\nles paies pour le compte des universit\u00e9s impose 6 \u00e0 8 semaines entre la\nsignature d\u2019un contrat de travail et la premi\u00e8re paie ou le premier\nacompte. Par ailleurs, deux dates de recrutement sont possibles : le 1er\nou le 15 de chaque mois.\n</li>\n<li>\nLa DGRTT ne r\u00e9dige des contrats de travail que si le dossier est\ncomplet (cf. PROCEDURE). Ceci implique notamment l\u2019existence d\u2019un\ndevis valid\u00e9 par la DGRTT et la structure recruteuse. Pour rappel, la\nvalidation du devis d\u00e9pend de l\u2019existence d\u2019une convention de\nrecherche sign\u00e9e permettant de couvrir le salaire de la personne\nrecrut\u00e9e pendant la dur\u00e9e de son contrat. Des exceptions sont\npossibles, elles concernent essentiellement la dur\u00e9e de la couverture\nsalariale des contrats doctoraux et n\u00e9cessite un engagement financier\nde la structure recruteuse.\n</li>\n</ul>\n",
    charges_plus_12_mois: 36.18,
    charges_moins_12_mois: 37.88,
    transport: 35,
  },
  message_dgrtt:
    "Roses are red, Violets are blue, Sugar is sweet, And so are you.",
  point_indice: 4.630291,
  convention: {
    TAUX_ENVIRONNEMENT_PERSONNEL_NON_PERMANENT: 0.8,
    TAUX_PROVISION_RISQUE: 0.08,
    COUT_HORAIRE_STAGE: 3.6,
    REMUNERATION: [
      ["PU/DR C EX Confirm\u00e9", 1320],
      ["PU/DR C EX", 1270],
      ["PU/DR C1 Confirm\u00e9", 1164],
      ["PU/DR C1", 1058],
      ["PU/DR C2 Confirm\u00e9", 963],
      ["PU/DR C2", 776],
      ["MC/CR HC Confirm\u00e9", 963],
      ["MC/CR HC", 776],
      ["MC/CR CN Confirm\u00e9", 821],
      ["MC/CR CN", 673],
      ["IR HC Confirm\u00e9", 963],
      ["IR HC", 821],
      ["IR C1 Confirm\u00e9", 821],
      ["IR C1", 734],
      ["IR C2 Confirm\u00e9", 713],
      ["IR C2", 550],
      ["IE HC confirm\u00e9", 783],
      ["IE HC", 729],
      ["IE C1 Confirm\u00e9", 673],
      ["IE C1", 612],
      ["IE C2 Confirm\u00e9", 619],
      ["IE C2", 492],
      ["ASI Confirm\u00e9", 551],
      ["ASI", 440],
      ["TR CE Confirm\u00e9", 514],
      ["TR CE", 445],
      ["TR CS Confirm\u00e9", 489],
      ["TR CS", 405],
      ["TR CN Confirm\u00e9", 463],
      ["TR CN", 362],
    ],
    TAUX_ENVIRONNEMENT_PERSONNEL_PERMANENT: 0.8,
    COUT_ENVIRONNEMENT_PERSONNEL_HEBERGE: 3000,
    DUREE_AMORTISSEMENT: [
      ["Acquisition de logiciels", 1],
      ["Mat\u00e9riel informatique", 3],
      ["Mat\u00e9riel scientifique", 5],
      ["Mat\u00e9riel de bureau", 5],
      ["Mobilier", 10],
      ["Installations techniques", 10],
      ["Mat\u00e9riel divers", 10],
    ],
    TAUX_PARTICIPATION_COUTS_INDUITS: 0.15,
    TAUX_CHARGE_PATRONALE: 0.375,
  },
};

describe("Creating the list of dotted keys", () => {
  const wrapper = mount(ConstantsEditor, {
    propsData: {
      val: constants,
      // no url prop, no ajax call in tests.
    },
    attachToDocument: true,
  });
  // Accessing the Vue instance:
  const vm = wrapper.vm;

  // beforeEach(() => {
  // afterEach

  it("should create the list of dotted key", () => {
    expect(vm.val).toEqual(constants);
    expect(vm.isObj(constants)).toBeTruthy();
    const res = vm.dottedConstants;
    expect(res[0].key).toEqual("faq_categories");
    expect(res[0].val.length).toEqual(3);
  });

  it("should preserve order (entries())", () => {
    const res = vm.entries();
    expect(res[0].key).toEqual("faq_categories");
    expect(res[1].key).toEqual("nom_bureaux_dgrtt.MSAR");
  });

  it("quickfilter", () => {
    expect(vm.entries().length).toBeGreaterThan(1);
    vm.filterKey = "faq";
    expect(vm.entries().length).toEqual(1);
  });

  it("Save accesses the constants from a dotted key", () => {
    vm.constants = constants;
    let res = vm.updateObject(constants, "faq_categories", "rst");
    expect(res.faq_categories).toEqual("rst");
  });
});
