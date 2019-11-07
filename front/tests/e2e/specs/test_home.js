// https://docs.cypress.io/api/introduction/api.html

describe("Login Page", () => {
  it("Unauthenticated, we're redirected to the login page", () => {
    cy.visit("/");
    cy.contains("Connexion");
  });
});

describe("Home", () => {
  beforeEach(() => {
    cy.visit("/backdoor?uid=courtoisi");
  });

  it("Should display the home page", () => {
    cy.contains("Les demandes actives de ma structure");
    cy.contains("Isabelle");
  });
});
