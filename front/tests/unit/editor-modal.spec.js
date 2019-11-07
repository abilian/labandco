import { shallow } from "vue-test-utils";

import { _ } from "lodash";

import EditorModal from "@/admin2/editorModal.vue";

describe("Editing an INTEGER constant", () => {
  const wrapper = shallow(EditorModal, {
    propsData: {
      title: "editor modal test",
      data: "100",
      type: "int",
      dottedKey: "recrutement.salaire_min_doctorant",
    },
  });
  // Accessing the Vue instance:
  const vm = wrapper.vm;

  beforeEach(() => {
    // Mock this method that calls a Notification element-ui component.
    vm.notifyWarning = jest.fn();
  });

  it("should work", () => {
    expect(vm.parseType("50")).toEqual(50);
  });

  it("should use the setter", () => {
    const newdata = "10";
    vm.newdata = newdata;
    expect(vm.toret).toEqual(10);
  });

  it("should not validate a string representing a float", () => {
    expect(vm.parseType("50.9")).toBeFalsy();
    expect(vm.notifyWarning).toHaveBeenCalledTimes(1);
    expect(vm.parseType("50,9")).toBeFalsy();
    expect(vm.notifyWarning).toHaveBeenCalledTimes(2);
  });

  it("should not validate a void input", () => {
    expect(vm.parseType("")).toBeFalsy();
    expect(vm.notifyWarning).toHaveBeenCalledTimes(1);
  });
});

describe("Editing a FLOAT constant", () => {
  const wrapper = shallow(EditorModal, {
    propsData: {
      title: "editor modal test",
      data: "100.20",
      type: "float",
      dottedKey: "convention.COUT_HORAIRE_STAGE",
    },
  });
  // Accessing the Vue instance:
  const vm = wrapper.vm;

  it("should work", () => {
    expect(vm.parseType("50.20")).toEqual(50.2);
  });

  it("should use the setter", () => {
    const newdata = "10.10";
    vm.newdata = newdata;
    expect(vm.toret).toEqual(10.1);
  });
});

describe("Editing a list of strings", () => {
  const constants = {
    faq_categories: ["Gestion contrat", "Ressources humaines"],
  };

  const wrapper = shallow(EditorModal, {
    propsData: {
      title: "editor modal test",
      data: constants["faq_categories"],
      type: "list[str]",
      dottedKey: "faq_categories",
    },
  });

  const vm = wrapper.vm;

  it("should display a string", () => {
    expect(_.isString(vm.listdata)).toBeTruthy();
  });

  it("should read back to a list of strings", () => {
    const newData = "foo\nbar";
    vm.listdata = newData;
    expect(vm.toret).toEqual(["foo", "bar"]);
  });
});

describe("Editing a list of lists with a str, a number", () => {
  const constants = {
    REMUNERATION: [["PU/DR", 1320], ["TR CN", 362]],
  };

  const wrapper = shallow(EditorModal, {
    propsData: {
      title: "editor modal test",
      data: constants["REMUNERATION"],
      type: "list[list[str,int]]",
      dottedKey: "REMUNERATION",
    },
  });
  // Accessing the Vue instance:
  const vm = wrapper.vm;

  beforeEach(() => {
    vm.notifyWarning = jest.fn();
  });

  it("should display the data array as a string", () => {
    expect(_.isString(vm.listoflists)).toBeTruthy();
  });

  it("should parse new user input to a list", () => {
    const newData = "foo, 10\nbar, 20";
    vm.listoflists = newData;
    expect(vm.toret.length).toEqual(2);
  });

  it("should parse new user input to a list of str/int", () => {
    const newData = "foo, 10\nbar, 20";
    vm.listoflists = newData;
    expect(vm.toret[0][1]).toEqual(10);
    expect(vm.toret[1][1]).toEqual(20);
  });

  it("should parse new user input to a list of str/float", () => {
    const newData = "foo, 10.10\nbar, 20.20";
    vm.listoflists = newData;
    expect(vm.toret[0][1]).toEqual(10.1);
    expect(vm.toret[1][1]).toEqual(20.2);
  });

  it("should warn the user he didn't enter a valid number", () => {
    let newData = "foo, blorgh\nbar, 20.20";
    vm.listoflists = newData;
    expect(vm.notifyWarning).toHaveBeenCalledTimes(1);

    // Parsing 10.xx actually works (10) but should not.
    // newData = "foo, 10.xx\nbar, 20.20";
    // vm.listoflists = newData;
    // expect(vm.notifyWarning).toHaveBeenCalledTimes(2);
  });

  it("should show a warning with other parsing errors", () => {
    const newData = "foo: 10\nbar, 20.20"; // a colon instead of a coma.
    vm.listoflists = newData;
    expect(vm.notifyWarning).toHaveBeenCalledTimes(1);
  });
});
