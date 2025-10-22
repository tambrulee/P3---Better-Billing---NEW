I deployed *Better Billing* to **Heroku**, ensuring the production version mirrored my local build.  
Deployment was handled through Git and the VS Code Source Control panel, connecting directly to the GitHub repository.  

The process included:
1. Freezing dependencies into `requirements.txt`  
2. Adding a `Procfile` to specify the Gunicorn web server  
3. Using **Whitenoise** for static file management  
4. Configuring the **DATABASE_URL** and secret keys through environment variables  
5. Setting `DEBUG = False` in production  

The deployment section in my README clearly documents each step and references environment setup, GitHub integration, and Heroku configuration.  
All commented-out code and unused files were removed for a clean final build.

**Evidence:**
- Heroku deployment with Gunicorn + Whitenoise  
- `.env` securely storing credentials  
- Clean, validated production build  
- README section documenting full deployment  