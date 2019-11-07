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
  },
};
