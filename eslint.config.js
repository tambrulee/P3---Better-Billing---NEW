// eslint.config.js — CommonJS flat config for ESLint v9
const js = require("@eslint/js");

/** @type {import('eslint').Linter.FlatConfig[]} */
module.exports = [
  // Global ignores (replacement for .eslintignore)
  {
    ignores: [
      "node_modules/**",
      "dist/**",
      "build/**",
      ".venv/**",
      "venv/**",

      // Django/admin/vendor & dumps
      "assets/admin/**",
      "**/vendor/**",
      "**/xregexp/**",
      "site_dump/**",

      // Minified or hashed bundles
      "**/*.min.*.js",
      "**/*.min.js",
      "**/*.[a-f0-9]*.js"
    ]
  },

  // Base recommended rules
  js.configs.recommended,

  // Your browser JS
  {
    files: [
      "assets/js/**/*.js",
      "better_bill_project/static/js/**/*.js"
    ],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "script", // change to "module" if you use import/export
      globals: {
        // Browser globals you use
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
        CSS: "readonly",
        console: "readonly"
      }
    },
    rules: {
      eqeqeq: "error",
      curly: "error",
      "no-redeclare": "error",
      "no-undef": "error",
      "no-control-regex": "warn",
      "no-useless-escape": "warn",
      "no-unused-vars": ["warn", { args: "none", varsIgnorePattern: "^_" }]

/* If you want to discourage logs in production, uncomment:
      // "no-console":
      //   process.env.NODE_ENV === "production" ? "warn" : "off"
*/
    }
  }
];
