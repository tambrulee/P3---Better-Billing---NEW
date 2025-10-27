 
## Heroku Deployment Issues & Resolutions
The below provides a detailed account of the issues encountered during the deployment of the *Better Billing* application to Heroku. The objective of this section is to demonstrate an understanding of common deployment challenges and how each was systematically identified, diagnosed, and resolved. Emphasis was placed on maintaining security, environmental consistency, and adherence to Django deployment best practices.

**Internal Server Error on Home Page**
- **Description:** Following a successful deployment, the application returned an 'Internal Server Error' when accessing the root URL.
- **Cause:** The issue was traced to a missing `SECRET_KEY` environment variable in the Heroku configuration, which Django requires for cryptographic signing.
- **Resolution:** Configured the `SECRET_KEY` in the Heroku environment settings under *Config Vars*. Updated `settings.py` to retrieve it securely from environment variables using `python-dotenv`.

**Static Files Not Loading**
- **Description:** CSS and JavaScript files were not loading in production after deployment.
- **Cause:** Heroku does not automatically serve static files in Django unless they are collected and managed via WhiteNoise or a similar tool.
- **Resolution:** Configured `STATIC_URL`, `STATIC_ROOT`, and `STATICFILES_DIRS` in `settings.py`. Installed and configured *WhiteNoise* in `MIDDLEWARE` to handle static file serving. Finally, ran `python manage.py collectstatic` and redeployed.

**PostgreSQL Database Configuration Issue**
- **Description:** The app failed to connect to the production database, resulting in errors during migration.
- **Cause:** The default SQLite configuration was still active in production, and the `DATABASE_URL` environment variable was not being parsed.
- **Resolution:** Integrated `dj-database-url` to parse the Heroku Postgres connection string. Updated the database configuration block in `settings.py` to automatically detect and apply the `DATABASE_URL` variable.

**ALLOWED_HOSTS Misconfiguration**
- **Description:** The application returned a 'DisallowedHost' error after deployment.
- **Cause:** The Heroku domain was not included in Django’s `ALLOWED_HOSTS` setting.
- **Resolution:** Added the Heroku app domain to `ALLOWED_HOSTS` within `settings.py`. This ensured that Django permitted HTTP requests from the deployed application’s domain.

**Procfile and Gunicorn Setup Errors**
- **Description:** The app failed to start on Heroku, displaying 'Error R10 (Boot timeout)' or 'No web processes running'.
- **Cause:** The `Procfile` was missing or incorrectly formatted, preventing Heroku from initiating the web server.
- **Resolution:** Created a valid `Procfile` containing `web: gunicorn better_bill_project.wsgi` to instruct Heroku how to run the app. Installed `gunicorn` and redeployed successfully.

**Collectstatic Command Failure**
- **Description:** Deployment failed due to an error running `collectstatic` on build.
- **Cause:** Heroku attempted to collect static files without the appropriate directories or configuration present.
- **Resolution:** Set `DISABLE_COLLECTSTATIC=1` temporarily in Heroku config vars to allow deployment to proceed. After confirming static settings locally, the variable was removed, and `collectstatic` was run manually to confirm success.

**Environment Variable Management (.env Not Loading)**
- **Description:** Local environment variables worked correctly, but production variables were not being applied on Heroku.
- **Cause:** Heroku does not use local `.env` files, so variables defined there were not accessible to the production environment.
- **Resolution:** All necessary environment variables were redefined in the Heroku dashboard’s *Config Vars* section, ensuring consistency between local and production settings.

**wkhtmltopdf Dependency Disabled**
- **Description:** Heroku builds failed when attempting to install `wkhtmltopdf` for PDF generation.
- **Cause:** The `wkhtmltopdf` package was deprecated and disabled on macOS and Heroku’s Linux buildpacks.
- **Resolution:** Replaced `wkhtmltopdf` with `reportlab` for generating PDF invoices. This solution offered native Python compatibility and ensured the feature worked reliably on Heroku.

**Buildpack and Cache Conflicts**
- **Description:** Occasionally, builds failed due to outdated dependencies cached in the Heroku environment.
- **Cause:** Heroku buildpacks stored outdated Python dependencies, leading to version mismatches during deployment.
- **Resolution:** Cleared Heroku’s build cache using the CLI (`heroku repo:purge_cache -a <app-name>`). Then redeployed the application to ensure a clean, consistent environment.

### Summary and Reflection
Resolving these Heroku deployment issues provided practical insight into the complexities of hosting Django applications in production. Each problem underscored the importance of environment-specific configuration, version control hygiene, and dependency management. Through iterative debugging and adherence to deployment best practices, the application was successfully stabilised and optimised for production reliability.


