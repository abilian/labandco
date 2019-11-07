/* eslint-disable import/first */
jest.mock("@/v3/components/tableStorage/tableStorage.js");

import { mount, shallow } from "vue-test-utils";

import { tableStorage } from "@/v3/components/tableStorage/tableStorage";
import BoxDemandes from "@/v3/components/grids/box-demandes.vue";

/* eslint-enable import/first */

const dataFixture = [
  {
    __created_at__: "2017-10-19",
    nom: "testeur",
    age: 100,
  },
  {
    __created_at__: "2017-10-18",
    nom: "foo",
    age: 2,
  },
];

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

const colFilter = {};

describe("Filtering entries", () => {
  // Now mount the component and you have the wrapper
  const wrapper = mount(BoxDemandes, {
    propsData: {
      id: "test",
      // don't give the url prop to prevent the ajax call.
    },
    attachToDocument: true,
  });

  // Accessing the Vue instance:
  const vm = wrapper.vm;

  it("filters out old entries (old=true)", () => {
    wrapper.setData({ data: dataFixture });
    wrapper.setData({
      old: true,
      colFilter: colFilter,
    });
    expect(vm.data).toEqual(dataFixture);
    expect(vm.old).toBeTruthy();
    expect(vm.entries().length).toEqual(1);
    // caution, dependent on columns order in mocks.
    expect(vm.preFilter(dataFixture)).toEqual([dataFixture[0]]);
    expect(vm.total).toEqual(dataFixture.length);
  });

  it("accepts old entries (old=false)", () => {
    wrapper.setData({ data: dataFixture });
    wrapper.setData({
      old: false,
      colFilter: colFilter,
    });
    expect(vm.data).toEqual(dataFixture);
    expect(vm.entries()).toEqual(dataFixture);
  });

  it("filters entries with a column filter", () => {
    wrapper.setData({ data: dataFixture });
    wrapper.setData({
      old: false,
      colFilter: { nom: { testeu: true } },
    });
    expect(vm.data).toEqual(dataFixture);
    expect(vm.entries().length).toEqual(1);
    // caution, dependent on columns order in mocks.
    expect(vm.entries()[0]).toEqual(dataFixture[0]);
  });

  it("uses the quickfilter", () => {
    wrapper.setData({
      filterKey: "foo",
      colFilter: colFilter,
    });
    // caution, dependent on columns order in mocks.
    expect(vm.entries()).toEqual([dataFixture[1]]);
  });
});

describe("Table demandes with filters", () => {
  const wrapper = shallow(BoxDemandes, {
    attachToDocument: true,
  });

  const vm = wrapper.vm;

  // fixtures
  wrapper.setData({ data: dataFixture });

  it("deactivates all filters", () => {
    wrapper.setData({ colFilter: { nom: { test: true } } });
    // caution, dependent on columns order in mocks.
    expect(vm.entries()).toEqual([dataFixture[0]]);
    vm.onFilterDeactivateAll(); // how to properly $emit ?
    // wrapper.trigger("filterDeactivateAll");  // no
    expect(vm.entries()).toEqual(dataFixture);
  });
});

describe("Pagination", () => {
  const wrapper = shallow(BoxDemandes);

  const vm = wrapper.vm;

  const dataFixture = [
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
    {
      __created_at__: "2017-10-18",
      nom: "t2",
      age: 100,
    },
    {
      __created_at__: "2017-10-18",
      nom: "t3",
      age: 2,
    },
  ];

  // fixtures
  wrapper.setData({ data: dataFixture });
  // 2 elements per page.
  wrapper.setData({ pageCount: { number: 2 } });

  it("returns the data for the current page", () => {
    expect(vm.entries_page().length).toEqual(2);
  });

  it("respects page boundaries", () => {
    expect(vm.page).toEqual(1);

    vm.previousPage();
    expect(vm.page).toEqual(1);

    vm.nextPage();
    expect(vm.page).toEqual(2);

    vm.nextPage();
    expect(vm.page).toEqual(2);

    vm.previousPage();
    expect(vm.page).toEqual(1);
    expect(vm.pageMax).toEqual(2);

    vm.firstPage();
    expect(vm.page).toEqual(1);

    vm.lastPage();
    expect(vm.page).toEqual(2);
  });
});

describe("Sorting rows", () => {
  const wrapper = shallow(BoxDemandes);
  const vm = wrapper.vm;

  wrapper.setData({ data: dataFixture });

  it("should sort by creation date", () => {
    vm.sortRows("__created_at__", columns, 0);
    let a = vm.data[0].__created_at__;
    let b = vm.data[1].__created_at__;
    expect(a < b).toBeTruthy();
    // reverse.
    vm.sortRows("__created_at__", columns, 1);
    a = vm.data[0].__created_at__;
    b = vm.data[1].__created_at__;
    expect(a < b).toBeFalsy();
  });

  it("should sort by name", () => {
    vm.sortRows("nom", columns, 0);
    let a = vm.data[0].nom;
    let b = vm.data[1].nom;
    expect(a < b).toBeTruthy();
  });
});

describe("Computing the available columns and their order", () => {
  // Trying to test this.columns.
  // So need to mock the tableStorage api.

  const wrapper = shallow(BoxDemandes);
  const vm = wrapper.vm;

  it("should set mocks accordingly", () => {
    expect(tableStorage.isDefined()).toBeTruthy();
    expect(tableStorage.get("id", "columns")).toEqual(columns);
  });

  it("should set columns", () => {
    expect(vm.columns).toEqual(columns);
  });
});
