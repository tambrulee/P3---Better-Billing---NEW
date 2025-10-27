# 🚀 My Deployment Process

## Deploying to GitHub via VS Code

I managed version control for this project entirely through **VS Code** and **GitHub**, using Git integration to keep my workflow simple and visual.

[Source Control & Repo](/readme_docs/source_control.png)

1. **Initialize Git Repository**  
   I opened my project folder in VS Code and went to the **Source Control** panel on the sidebar.  
   Since this was a new project, I clicked **“Initialize Repository”** to create a local Git repo.

2. **Stage and Commit Changes**  
   Once my files were ready, I staged them by clicking the `+` icon beside each file (or **“Stage All Changes”**).  
   I wrote an initial commit message like `Initial commit` and hit **Commit** to save my progress.

3. **Publish to GitHub**  
   With my first commit ready, I selected **“Publish Branch”** from the Source Control panel.  
   VS Code prompted me to sign in to GitHub — once I did, I chose **“Publish to GitHub”** and confirmed the repository name.  
   VS Code automatically created a new repo on GitHub and pushed all my local files there.

4. **Syncing Future Changes**  
   Whenever I made updates or fixes, I simply committed the changes and clicked **“Sync Changes”** to push them to GitHub.  
   This kept my remote repository fully in sync with my local version throughout development.

💡 **Tip I Followed:**  
Before publishing, I made sure to include a `.gitignore` file to exclude unnecessary or sensitive files such as `.env`, compiled files, and system cache directories.

---

## Setting Up Django Locally

Once my repository was initialized, I set up the Django project locally.

1. **Create and Activate a Virtual Environment**  
   In the terminal, I created a virtual environment and activated it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # Mac/Linux  
   .venv\Scripts\activate         # Windows
   ```

2. **Install Dependencies**  
   I installed Django and all required packages:
   ```bash
   pip install django gunicorn psycopg2-binary dj-database-url python-dotenv whitenoise
   ```

3. **Create the Django Project and App**  
   Then I created the project structure:
   ```bash
   django-admin startproject better_billing  
   cd better_billing  
   python manage.py startapp better_bill_project
   ```

4. **Apply Migrations and Create Superuser**  
   I ran migrations to set up the database and created an admin account:
   ```bash
   python manage.py makemigrations  
   python manage.py migrate  
   python manage.py createsuperuser
   ```

5. **Set Up Environment Variables**  
   I created a `.env` file in the project root and added:
   ```bash
   SECRET_KEY=your_secret_key  
   DEBUG=True  
   DATABASE_URL=sqlite:///db.sqlite3
   ```
   Then I loaded these variables in `settings.py`:
   ```python
   from dotenv import load_dotenv  
   load_dotenv()
   ```

6. **Run the Development Server**  
   Finally, I ran the project locally to confirm everything was working:
   ```bash
   python manage.py runserver
   ```
   I verified it by visiting **http://127.0.0.1:8000/** in my browser.

   [Local server connected](/readme_docs/heroku/runserver.png)

---

## Deploying to Heroku

When my project was stable, I deployed it to **Heroku** for live hosting.

1. **Install and Log Into the Heroku CLI**
   ```bash
   brew tap heroku/brew && brew install heroku  
   heroku login
   ```
   [Log in success](/readme_docs/heroku/heroku_cli.png)

2. **Prepare Django for Deployment**
   I created a `Procfile` in the root directory:
   ```bash
   web: gunicorn better_billing.wsgi
   ```

   Then I updated my static file settings in `settings.py`:
   ```python
   STATIC_ROOT = BASE_DIR / 'staticfiles'  
   STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  
   MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
   ```

   I also added my Heroku domain to `ALLOWED_HOSTS`:
   ```python
   ALLOWED_HOSTS = ["better-billing-app.herokuapp.com"]
   ```

3. **Create a Heroku App**
   ```bash
   heroku create better-billing-app
   ```

4. **Add Config Variables**
   I set my environment variables directly in Heroku:
   ```bash
   heroku config:set SECRET_KEY='your_secret_key'  
   heroku config:set DEBUG=False  
   heroku config:set DISABLE_COLLECTSTATIC=1
   ```

5. **Deploy to Heroku**
   I connected Heroku to my Git repo and pushed the code:
   ```bash
   git remote add heroku https://git.heroku.com/better-billing-app.git  
   git push heroku main
   ```

6. **Run Migrations and Create Admin**
   ```bash
   heroku run python manage.py migrate  
   heroku run python manage.py createsuperuser
   ```

7. **Enable Static Files**
   After the first deployment, I enabled static collection:
   ```bash
   heroku config:unset DISABLE_COLLECTSTATIC  
   git commit --allow-empty -m "Trigger collectstatic"  
   git push heroku main
   ```

8. **Open the Live App**
   ```bash
   heroku open
   ```

[App successfully deployed to Heroku](/readme_docs/heroku/heroku_deploy.png)

---

**Deployment Complete:**  
My Django app was successfully deployed to **Heroku**, connected to **GitHub** for version control, and fully ready for continuous updates.

## Errors & Bugs:
[View Heroku Deployment Issues & Resolutions here](/readme_docs/heroku.md)
