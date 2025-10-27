import js from "@eslint/js";

/** @type {import('eslint').Linter.FlatConfig[]} */
export default [
  js.configs.recommended,

  // Only lint YOUR scripts (adjust paths if needed)
  {
    files: [
      "assets/js/**/*.js",
      "better_bill_project/static/js/**/*.js"
    ],
    // extra guard: even inside those folders, skip minified/hashed
    ignores: [
      "**/*.min.*.js",
      "**/*.min.js",
      "**/*.[a-f0-9]*.js"
    ],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "script", // switch to "module" if you use ES modules
      globals: {
        // Common browser APIs you use
        window: "readonly",
        document: "readonly",
        location: "readonly",
        history: "readonly",
        navigator: "readonly",
        localStorage: "readonly",
        sessionStorage: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        fetch: "readonly",
        URLSearchParams: "readonly",
        CSS: "readonly"
      }
    },
    rules: {
      // tighten basics
      eqeqeq: "error",
      curly: "error",
      "no-redeclare": "error",
      "no-undef": "error",
      "no-control-regex": "warn",      // if you truly need \x00, change to "off"
      "no-useless-escape": "warn",
      "no-unused-vars": ["warn", { args: "none", varsIgnorePattern: "^_" }]
    }
  },

  // OPTIONAL: a tiny rule-set to silence leftover vendor bits if any slip through
  {
    files: ["**/vendor/**", "**/*.min.*.js", "**/*.[a-f0-9]*.js", "site_dump/**", "assets/admin/**"],
    rules: {
      "no-undef": "off",
      "eqeqeq": "off",
      curly: "off",
      "no-control-regex": "off",
      "no-useless-escape": "off",
      "no-unused-vars": "off",
      "no-redeclare": "off"
    }
  }
];
