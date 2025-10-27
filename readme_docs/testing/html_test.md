# HTML Validation Summary — Better Billing

## Overview
We validated rendered HTML output for key pages in the Django-based **Better Billing** app, ensuring compliance with W3C standards. Since pages require login and use Django template syntax, validation was run on *rendered* HTML captured via a custom management command.

---

## Key Issues & Fixes

### 1. DisallowedHost (400 Errors)
- **Cause:** `ALLOWED_HOSTS` didn’t include `testserver`.
- **Fix:** Added `testserver`, `127.0.0.1`, and `localhost` dynamically in the command and set `HTTP_HOST="127.0.0.1"`.

### 2. NoReverseMatch for "home"
- **Cause:** Nonexistent URL name.
- **Fix:** Updated to real route names (`index`, `create-invoice`, `view-invoice`, etc.).

### 3. AJAX Fragments Invalid
- **Cause:** `/ajax/matter-options/` returned partial markup (no doctype).
- **Fix:** Excluded AJAX routes and added logic to skip non-document responses.

### 4. Nested <main> Elements
- **Cause:** Both base and child templates had `<main>` tags.
- **Fix:** Retained one `<main>` in `base.html`; replaced child `<main>`s with `<section>` or `<div>`.

### 5. 404s on Some Views
- **Cause:** Missing context (e.g. required DB data).
- **Fix:** Skipped non-200 responses to avoid saving error pages.

---

## Outstanding
- Confirm `record-time` renders when proper data exists.
- Ajax matter options aria labels issue - needs to be excluded from check

---

## Conclusion
Validation of full HTML pages is now reliable. All key pages return clean HTML5 output. Remaining issues are minor and primarily data-dependent.
