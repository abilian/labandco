module.exports = {
  root: true,
  extends: [
    "eslint:recommended",
    "plugin:vue/essential",
    // "plugin:vue/strongly-recommended",

    // "@vue/prettier",
    // https://github.com/feross/standard/blob/master/RULES.md#javascript-standard-style
    "standard",
    "plugin:testcafe/recommended",
  ],
  plugins: [
    // required to lint *.vue files
    "vue",
    "cypress",
    // "testcafe",
    "lodash-fp",
  ],
  env: {
    es6: true,
    jest: true,
    // browser: true,
    // amd: true,
  },
  globals: {
    $: true,
  },
  parserOptions: {
    parser: "babel-eslint",
  },
  // add your custom rules here
  rules: {
    quotes: "off",
    semi: ["error", "always"],
    "comma-dangle": ["error", "always-multiline"],
    "space-before-function-paren": "off",
    camelcase: "off",
    "no-console": "off",
    "vue/no-v-html": "off",
    "vue/singleline-html-element-content-newline": "off",

    // TODO
    "vue/no-side-effects-in-computed-properties": "off",
    "vue/return-in-computed-property": "off",
    "vue/require-v-for-key": "off",
    "vue/no-unused-vars": "off",
    "vue/require-prop-types": "off",
    "vue/require-default-prop": "off",

    // Lodash/fp
    "lodash-fp/consistent-compose": "off",
    // "lodash-fp/consistent-name": ["error", "fp"],
    "lodash-fp/no-argumentless-calls": "error",
    "lodash-fp/no-chain": "error",
    "lodash-fp/no-extraneous-args": "error",
    "lodash-fp/no-extraneous-function-wrapping": "error",
    "lodash-fp/no-extraneous-iteratee-args": "error",
    "lodash-fp/no-extraneous-partials": "error",
    "lodash-fp/no-for-each": "off",
    "lodash-fp/no-partial-of-curried": "error",
    "lodash-fp/no-single-composition": "error",
    "lodash-fp/no-submodule-destructuring": "error",
    "lodash-fp/no-unused-result": "error",
    "lodash-fp/prefer-compact": "error",
    "lodash-fp/prefer-composition-grouping": "error",
    "lodash-fp/prefer-constant": [
      "error",
      {
        arrowFunctions: false,
      },
    ],
    "lodash-fp/prefer-flat-map": "error",
    "lodash-fp/prefer-get": "error",
    "lodash-fp/prefer-identity": [
      "error",
      {
        arrowFunctions: false,
      },
    ],
    // "lodash-fp/preferred-alias": "off",
    // "lodash-fp/use-fp": "error",
  },
};
