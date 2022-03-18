// import { login } from "./tests_utils.js";

import { ClientFunction, Selector } from "testcafe";

const getWindowPathname = ClientFunction(() => window.location.pathname);

// login (as a user with demande creation right) and redirect to the form.
fixture`Nouvelle demande`
  .page`http://localhost:5000/backdoor?uid=courtoisi&next=http://localhost:5000/demandes/new?type=convention`;

async function click_and_augment_form(t) {
  await t.click("#lien_contrat[value=oui]");
}

test("Le formulaire de nouvelle_demande est réactif", async (t) => {
  await click_and_augment_form(t);
  await t.expect(Selector("input[name=eotp_ou_no_dgrtt]").exists).ok();
});

async function fill_form(t) {
  await t
    .click("#lien_contrat[value=non]")
    .typeText("input[name=nom_ou_acronyme]", "test")
    .typeText("input[name=nom_financeur]", "test")
    .typeText("textarea[name=description_courte]", "test")
    .click("#integre_entreprise[value=non]")
    .click("#appel_a_projets[value=non]")
    .typeText("input[name=date_depot]", "2017-01-01")
    .typeText("input[name=duree_previsionnelle]", "20")
    .click("#materiel_donnees[value=non]")
    .click("#savoir_faire[value=non]")
    .click("#logiciel[value=non]")
    .click("#brevet[value=non]")
    .click("#creer-demande")

    // assertions
    // a "method not allowed" error would stick us to /demandes/new instead of /demandes/<id>.
    .expect(getWindowPathname())
    .notEql("/demandes/new");
}

test("Nouvelle_demande redirige correctement", async (t) => {
  await fill_form(t);
});
