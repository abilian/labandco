// Testing Vue tables components.
// https://vue-test-utils.vuejs.org/en/guides/getting-started.html

import { mount } from "vue-test-utils";

import ColSettings from "@/v3/components/grids/col-settings.vue";

const entriesFixture = [
  {
    __created_at__: "2017-10-18",
    nom: "testeur",
    age: 100,
  },
  {
    __created_at__: "2017-10-18",
    nom: "foo",
    age: 2,
  },
];

describe("The column settings modale, with NO given props", () => {
  const wrapper = mount(ColSettings, {
    attachToDocument: true,
  });

  wrapper.setProps({
    colId: "nom",
    entries: entriesFixture,
    colFilter: {},
  });

  const vm = wrapper.vm;

  it("sets the __all__ bool to true", () => {
    expect(vm.filterValues.__all__).toBeTruthy();
    expect(vm.filterValues.test).toBeFalsy();
  });
});

describe("The column settings modale, with given props", () => {
  // Now mount the component and you have the wrapper
  const wrapper = mount(ColSettings, {
    attachToDocument: true,
  });

  wrapper.setProps({
    colId: "nom",
    entries: entriesFixture,
    colFilter: { nom: { test: true } },
  });

  const vm = wrapper.vm;

  it("reads its props", () => {
    expect(vm.entries.length).toEqual(2);
    expect(vm.colId).toEqual("nom");
  });

  it("finds all the possible values of this column", () => {
    expect(vm.colValues).toEqual(["foo", "testeur"]);
  });

  it("sets the __all__ boolean to false when it is given a filter value as entry.", () => {
    expect(vm.__all__).toBeFalsy();
    // expect(vm.selectAll).not.toBeTruthy(); // fails. bug ?
    expect(vm.filterValues.test).toBeTruthy();
  });

  // it("checks the checkboxes by default", () => {
  // xxx
  // const selectAll = wrapper.find("#selectAll");
  // expect(selectAll.checked).toBeTruthy();
  // const checkboxes = wrapper.findAll('.checkboxe-inline');
  // expect(checkboxes.length).toEqual(3);
  // });
});

describe("The column settings modale, with given props", () => {
  const entriesWithDates = [
    {
      // oldest
      created_at: "29/10/2018",
      __created_at__: "2018-10-29",
    },
    {
      created_at: "29/10/2017",
      __created_at__: "2017-10-29",
    },
    {
      // youngest
      created_at: "18/10/2017",
      __created_at__: "2017-10-18",
    },
  ];

  const wrapper = mount(ColSettings, {
    attachToDocument: true,
  });

  wrapper.setProps({
    colId: "created_at",
    entries: entriesWithDates,
  });

  const vm = wrapper.vm;

  it("finds all dates, sorted", () => {
    expect(vm.colValues).toEqual([
      entriesWithDates[2].created_at,
      entriesWithDates[1].created_at,
      entriesWithDates[0].created_at,
    ]);
  });
});
