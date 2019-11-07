// import { login } from "./tests_utils.js";

import { ClientFunction, Selector } from "testcafe";

// const getWindowPathname = ClientFunction(() => window.location.pathname);

// login (as a user with demande creation right) and redirect to the form.
fixture`Logging to the tables`
  .page`http://localhost:5000/backdoor?uid=courtoisi&next=http://localhost:5000/`;

const firstMenu = Selector(".fa-chevron-down").nth(0);
// const checkboxes = Selector(".checkbox-inline");
const selectAll = Selector("#selectAll");
const buttonOk = selectAll("#button-ok");

// FIXME
// test("clicking selectAll twice in a row", async t => {
//   // await t.expect(firstMenu.exists).ok();
//   await t.click(firstMenu).click("#selectAll");
//
//   // click again
//   await t.click("#selectAll");
//   await t.expect(selectAll.checked).ok(); // => failing two clicks in a row !
// });

// FIXME
// test("Unchecking all adds the filter icon", async t => {
//   await t
//     .click(firstMenu)
//     .click(selectAll)
//     .click(buttonOk);
//
//   const icon = Selector(".glyphicon-filter");
//   await t.expect(icon.count).eql(1);
// });

const reload = ClientFunction(() => window.location.reload());

test("Reloading the browser uses the saved data in local storage", async t => {
  await t
    .click(firstMenu)
    .click(selectAll)
    .click(buttonOk);

  reload();
  await t.click(firstMenu);

  await t.expect(selectAll.checked).notOk();
});
