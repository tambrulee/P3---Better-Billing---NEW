### Introduction
This document provides a detailed overview of the main bugs and issues encountered during the development of the *Better Billing* Django project. Each entry outlines the nature of the issue, its underlying cause, and the resolution steps undertaken. The documentation demonstrates systematic debugging practices, reflecting professional software engineering standards and academic rigour.

Static Files Not Loading (CSS Missing)
**Description:** After deploying to Heroku and running locally, CSS files were not appearing.
**Error Message:** Browser console showed 404 errors for `/static/css/style.css`.
**Cause:** Static files were not correctly collected or referenced due to improper static path configuration.
**Resolution:** Configured `STATIC_URL`, `STATICFILES_DIRS`, and `STATIC_ROOT` in `settings.py`, then ran `python manage.py collectstatic`. Also confirmed `{% load static %}` tag was present in all templates.

Heroku Internal Server Error ('/' route)
**Description:** Application deployed successfully but crashed upon visiting the home page.
**Error Message:** Internal Server Error: /
**Cause:** Environment variables were not properly configured in Heroku, leading to a missing `SECRET_KEY`.
**Resolution:** Added environment variables in Heroku dashboard and created a `.env` file locally using `python-dotenv`. Updated `settings.py` to securely load `SECRET_KEY` from environment variables.

Signal Warning — 'signals not accessed'
**Description:** VSCode and Pylance flagged unused imports for the signals module.
**Error Message:** ‘Module imported but not accessed’ warning.
**Cause:** Django signals file was not explicitly imported in the app’s `__init__.py`.
**Resolution:** Added `import billing.signals` in the app’s `ready()` method within `apps.py`, ensuring Django loaded signal handlers correctly on startup.

wkhtmltopdf Dependency Error
**Description:** Attempting to generate PDF invoices raised dependency errors on macOS.
**Error Message:** OSError: cannot load library 'libgobject-2.0-0'
**Cause:** The `wkhtmltopdf` dependency was deprecated on macOS (disabled via Homebrew).
**Resolution:** Switched to the `reportlab` package for PDF generation, ensuring cross-platform compatibility and better long-term support.

JavaScript Not Linking to Django Template
**Description:** Functions in `create_invoice.js` were not executing on the template page.
**Error Message:** No console output or errors visible in browser developer tools.
**Cause:** The script was not properly loaded due to an incorrect path reference or missing static tag.
**Resolution:** Placed the script in `static/js/`, referenced it via `{% static 'js/create_invoice.js' %}` in the template, and verified it loaded using browser dev tools.

CSS Layout Issue in 'Recent Entries' Section
**Description:** The recent entries table appeared too close to the preceding content.
**Error Message:** No explicit error, but visually inconsistent spacing.
**Cause:** Lack of top padding or margin between elements.
**Resolution:** Added Bootstrap spacing utility class `mt-4` above the recent entries section to improve layout readability.

Gitignore and Secret Key Exposure
**Description:** Sensitive configuration files were accidentally tracked by Git.
**Error Message:** Repository contained `settings.py` with exposed `SECRET_KEY`.
**Cause:** `.gitignore` was not properly configured before the initial commit.
**Resolution:** Added `.env`, `settings.py`, `pyproject.toml`, and other sensitive files to `.gitignore`. Then used `git rm --cached` to remove tracked files and recommitted the sanitized repository.

Model Reference Mismatch (Client–Matter Validation)
**Description:** Inconsistent client–matter relationships caused validation errors in WIP and TimeEntry forms.
**Error Message:** Selected matter does not belong to the chosen client.
**Cause:** The `clean()` method in the model did not validate cross-referenced relationships properly.
**Resolution:** Updated `clean()` to enforce consistency between `client`, `matter`, and `time_entry`, preventing invalid data entry.

Migration Conflicts During Model Changes
**Description:** Database migrations failed when modifying related models.
**Error Message:** django.db.migrations.exceptions.InconsistentMigrationHistory
**Cause:** Migrations were manually edited or generated out of sync with the database state.
**Resolution:** Rolled back conflicting migrations using `python manage.py migrate app zero`, deleted obsolete migration files, and regenerated fresh migrations with `makemigrations`.

Circular Import in Models
**Description:** Importing models across apps caused Django to throw circular import errors.
**Error Message:** ImportError: cannot import name 'ModelName' from partially initialized module
**Cause:** Two models referenced each other directly without deferred string-based model relationships.
**Resolution:** Replaced direct model imports with string references (e.g., `'app.ModelName'`) and adjusted type hints accordingly.

### Summary and Lessons Learned
Throughout the debugging process, systematic testing and documentation proved essential. Each issue reinforced the importance of version control hygiene, modular code organization, and proactive dependency management. By resolving these bugs methodically, the project evolved into a more stable, secure, and maintainable application.

