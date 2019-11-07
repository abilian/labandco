/**
 Mocking for Jest unit tests.

 In the test, tell Jest to use them:

   jest.mock("../../tableStorage/tableStorage.js");

 and import them.

 We can use storageFoo.mockImplementation to rewrite the mock function
 for each test.
*/

const columns = [
  {
    id: "__created_at__",
    label: "foo",
    sort_key: "__created_at__",
  },
  {
    id: "nom",
    label: "nom",
    sort_key: "nom",
  },
  {
    id: "age",
    label: "age",
    sort_key: "age",
  },
];

const columnOrder = [
  {
    id: "age",
    order: 0,
  },
  {
    id: "nom",
    order: 1,
  },
];

const isDefined = jest.fn(() => true);
const set = jest.fn(() => "set");
const get = jest.fn((id, what) => {
  if (what === "columns") {
    return columns;
  }
  if (what === "colOrders") {
    return columnOrder;
  }
});
const remove = jest.fn(() => "remove");
const hasStorage = jest.fn(() => "remove");
const hasKey = jest.fn(() => "remove");

export let tableStorage = { get, set, remove, hasKey, hasStorage, isDefined };
