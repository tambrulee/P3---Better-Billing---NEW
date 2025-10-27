# ESLint Setup and Fixes

This document explains the issues encountered while setting up ESLint for the **Better Billing** project, and how each one was resolved.

---

## 1️⃣ Problem: “Could not find config file”
**Error**
```
Error: Could not find config file.
```
**Cause**  
ESLint was installed but had no configuration file at the project root.

**Fix**
- Installed ESLint locally:
  ```bash
  npm i -D eslint
  ```
- Created a config file in the project root.  
  Since the project uses ESLint v9+, we used the **Flat Config** system (the new default).

---

## 2️⃣ Problem: “ESLintEmptyConfigWarning – Running ESLint with an empty config”
**Cause**  
The initial config file was empty or exported nothing.

**Fix**
- Added a complete configuration exporting an array of rules, using:
  ```js
  module.exports = [ require("@eslint/js").configs.recommended, { … } ];
  ```
- Verified ESLint ran with the new config.

---

## 3️⃣ Problem: “Module type not specified / Reparsing as ES module”
**Error**
```
[MODULE_TYPELESS_PACKAGE_JSON] Warning: Module type of file …eslint.config.js is not specified…
```
**Cause**  
The config used ES module syntax (`export default`) while Node treated the file as CommonJS.

**Fix Options**
- **Simplest:** use CommonJS syntax (`require` + `module.exports`).
- **Alternative:** rename the file to `eslint.config.mjs` or add `"type": "module"` in `package.json`.

---

## 4️⃣ Problem: “The .eslintignore file is no longer supported”
**Cause**  
In ESLint v9+, `.eslintignore` is deprecated in favor of the `ignores` property in the flat config.

**Fix**
- Deleted `.eslintignore`.
- Moved all ignore patterns into the config file:
  ```js
  {
    ignores: [
      "node_modules/**",
      "dist/**",
      "build/**",
      "assets/admin/**",
      "**/vendor/**",
      "**/*.min.*.js"
    ]
  }
  ```

---

## 5️⃣ Problem: “no-undef” errors for browser globals (`fetch`, `URLSearchParams`, etc.)
**Cause**  
By default, ESLint assumes Node.js and doesn’t know browser APIs.

**Fix**
Added `globals` for browser objects:
```js
globals: {
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
```
This cleared hundreds of false `no-undef` errors.

---

## 6️⃣ Problem: Vendor and hashed JS files causing thousands of errors
**Cause**  
ESLint was linting everything, including Django admin, vendor bundles, and hashed builds.

**Fix**
Restricted ESLint to our source directories only:
```js
files: [
  "assets/js/**/*.js",
  "better_bill_project/static/js/**/*.js"
]
```
and ignored hashed/minified bundles using glob patterns.

---

## 7️⃣ Problem: “console is not defined”
**Cause**  
`console` was not declared in the globals list.

**Fix**
Added `console: "readonly"` under globals.

---

## 8️⃣ Problem: npm audit failed (`getaddrinfo ENOTFOUND registry.npmjs.org`)
**Error**
```
npm warn audit request to ... failed, reason: getaddrinfo ENOTFOUND registry.npmjs.org
```
**Cause**  
A temporary network or DNS issue prevented npm from reaching the registry.

**Fix**
- Checked the registry and proxy settings:
  ```bash
  npm config get registry
  npm config ls -l | grep -i proxy
  ```
- Reset to the default registry:
  ```bash
  npm config set registry https://registry.npmjs.org/
  npm config delete proxy
  npm config delete https-proxy
  ```
- Retried:
  ```bash
  npm audit fix
  ```

---

## Final Working Setup

**`eslint.config.js`**
```js
const js = require("@eslint/js");

module.exports = [
  {
    ignores: [
      "node_modules/**",
      "dist/**",
      "build/**",
      ".venv/**",
      "venv/**",
      "assets/admin/**",
      "**/vendor/**",
      "**/xregexp/**",
      "site_dump/**",
      "**/*.min.*.js",
      "**/*.min.js",
      "**/*.[a-f0-9]*.js"
    ]
  },
  js.configs.recommended,
  {
    files: ["assets/js/**/*.js", "better_bill_project/static/js/**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "script",
      globals: {
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
      "no-unused-vars": ["warn", { args: "none", varsIgnorePattern": "^_" }]
    }
  }
];
```

**VS Code setting**
```json
// .vscode/settings.json
{ "eslint.useFlatConfig": true }
```

**Run Commands**
```bash
npm run lint
npm run lint:fix
```

---

## Summary

| Issue | Cause | Resolution |
|--------|--------|-------------|
| Missing config | No ESLint config file | Added flat config |
| Empty config warning | File exported nothing | Populated config array |
| Module type warning | ESM syntax in `.js` | Used CommonJS syntax |
| `.eslintignore` deprecated | ESLint v9 | Moved patterns into `ignores` |
| `no-undef` for browser APIs | ESLint assumes Node | Declared browser globals |
| Vendor/minified files flagged | Linted everything | Added ignore globs |
| `console` undefined | Not declared | Added `console` global |
| `npm audit` failed | Network/DNS | Reset registry + retry |
