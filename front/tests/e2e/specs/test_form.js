describe("Formulaire", () => {
  beforeEach(() => {
    cy.visit("/backdoor?uid=courtoisi");
    cy.visit("/demandes/new?type=convention");
  });

  it("Should show form", () => {
    cy.contains("Nouvelle demande");
  });

  it("Should be reactive", () => {
    cy.get("#lien_contrat[value=oui]").click();
    cy.get("input[name=eotp_ou_no_dgrtt]").should("exist");
  });

  it("Should be fillable", () => {
    cy.get("#lien_contrat[value=non]").click();
    cy.get("input[name=nom_ou_acronyme]").type("test");
    cy.get("input[name=nom_financeur]").type("test");

    cy.get("textarea[name=description_courte]").type("test");
    cy.get("#integre_entreprise[value=non]").click();
    cy.get("#appel_a_projets[value=non]").click();
    cy.get("input[name=date_depot]").type("2017-01-01");
    cy.get("input[name=duree_previsionnelle]").type("20");
    cy.get("#materiel_donnees[value=non]").click();
    cy.get("#savoir_faire[value=non]").click();
    cy.get("#logiciel[value=non]").click();
    cy.get("#brevet[value=non]").click();
    cy.get("#creer-demande").click();

    cy.url().should("include", "/demandes/");
    cy.url().should("not.include", "/demandes/new");
  });
});
