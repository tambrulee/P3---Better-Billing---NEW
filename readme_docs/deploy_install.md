## Deploying to GitHub via VS Code

1. **Initialize Git Repository**
   - Open your project folder in VS Code.  
   - Go to the **Source Control** panel (left sidebar).  
   - Click **“Initialize Repository”** to create a new local Git repository if one doesn’t already exist.

2. **Stage and Commit Changes**
   - Click the `+` icon beside files or choose **“Stage All Changes.”**  
   - Enter a commit message such as `Initial commit` and click the **Commit** button.

3. **Publish to GitHub**
   - Click **“Publish Branch”** in the Source Control panel.  
   - Sign in to GitHub when prompted.  
   - Choose **“Publish to GitHub”** and confirm the repository name.  
   - VS Code will create the GitHub repo and push all files automatically.

4. **Sync Future Changes**
   - After updates, commit and use **“Sync Changes”** to push new commits to GitHub.

💡 **Tip:**  
Include a `.gitignore` file before publishing to exclude sensitive and unnecessary files such as:


## Setting Up Django Locally
 
 Open your terminal and run:
 
 ```
 python3 -m venv .venv
 source .venv/bin/activate      # Mac/Linux  
 .venv\Scripts\activate         # Windows
 ```
 
 Install Django and required packages:
 
 ```
 pip install django gunicorn psycopg2-binary dj-database-url python-dotenv whitenoise
 ```
 
 Create your Django project and app:
 
 ```
 django-admin startproject better_billing  
 cd better_billing  
 python manage.py startapp better_bill_project
 ```
 
 Apply migrations and create a superuser:
 
 ```
 python manage.py makemigrations  
 python manage.py migrate  
 python manage.py createsuperuser
 ```
 
 Set up environment variables:
 
 Create a `.env` file in your project root and add:
 ```
 SECRET_KEY=your_secret_key  
 DEBUG=True  
 DATABASE_URL=sqlite:///db.sqlite3
 ```
 
 Load your environment variables in `settings.py`:
 ```
 from dotenv import load_dotenv  
 load_dotenv()
 ```
 
 Run the development server:
 
 ```
 python manage.py runserver
 ```
 
 Visit http://127.0.0.1:8000/ to confirm the project is running.
 
 ---
 
 ## Deploying to Heroku
 
 Install and log in to the Heroku CLI:
 
 ```
 brew tap heroku/brew && brew install heroku  
 heroku login
 ```
 
 Prepare Django for deployment:
 
 Create a `Procfile` in your root directory:
 ```
 web: gunicorn better_billing.wsgi
 ```
 
 Update your static file configuration in `settings.py`:
 ```
 STATIC_ROOT = BASE_DIR / 'staticfiles'  
 STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  
 MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
 ```
 
 Ensure your `ALLOWED_HOSTS` includes your Heroku domain:
 ```
 ["better-billing-app.herokuapp.com"]
 ```
 
 Create a Heroku app:
 
 ```
 heroku create better-billing-app
 ```
 
 Set config variables:
 
 ```
 heroku config:set SECRET_KEY='your_secret_key'  
 heroku config:set DEBUG=False  
 heroku config:set DISABLE_COLLECTSTATIC=1  # optional for first deployment
 ```
 
 Deploy to Heroku:
 
 ```
 git remote add heroku https://git.heroku.com/better-billing-app.git  
 git push heroku main
 ```
 
 Run migrations and create an admin user:
 
 ```
 heroku run python manage.py migrate  
 heroku run python manage.py createsuperuser
 ```
 
 Enable collectstatic (after first deploy):
 
 ```
 heroku config:unset DISABLE_COLLECTSTATIC  
 git commit --allow-empty -m "Trigger collectstatic"  
 git push heroku main
 ```
 
 Open the live app:
 
 ```
 heroku open
 ```
 
  **Deployment complete:**  
 Your Django app is now fully deployed to Heroku and linked to your GitHub repository for future updates.