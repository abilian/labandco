describe("Table", () => {
  beforeEach(() => {
    cy.visit("/backdoor?uid=courtoisi");
  });

  it("should save state in local storage", () => {
    cy.get(".fa-chevron-down").eq(0).click();
    cy.get("#selectAll").should("be.checked");

    cy.get("#selectAll").click();
    cy.get("#button-ok").click();

    cy.reload();

    cy.get(".fa-chevron-down").eq(0).click();
    cy.get("#selectAll").should("not.be.checked");
  });
});

// const firstMenu = Selector(".glyphicon-menu-down").nth(0);
// // const checkboxes = Selector(".checkbox-inline");
// const selectAll = Selector("#selectAll");
// const buttonOk = selectAll("#button-ok");
//
// // FIXME
// // test("clicking selectAll twice in a row", async t => {
// //   // await t.expect(firstMenu.exists).ok();
// //   await t.click(firstMenu).click("#selectAll");
// //
// //   // click again
// //   await t.click("#selectAll");
// //   await t.expect(selectAll.checked).ok(); // => failing two clicks in a row !
// // });
//
// // FIXME
// // test("Unchecking all adds the filter icon", async t => {
// //   await t
// //     .click(firstMenu)
// //     .click(selectAll)
// //     .click(buttonOk);
// //
// //   const icon = Selector(".glyphicon-filter");
// //   await t.expect(icon.count).eql(1);
// // });
