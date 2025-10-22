Version control was managed using **Git and GitHub** throughout the project lifecycle.  
Each new feature or fix was committed separately with clear, descriptive commit messages, allowing easy traceability of the development process.  

Security measures included:
- Hiding secret keys and database URLs via `.env`  
- Adding `.env` and other sensitive files to `.gitignore`  
- Disabling `DEBUG` mode in production  
- Using Heroku’s config vars for secure key management  
- Ensuring user data validation and defensive design principles were followed  

The final repository is free from any exposed credentials or commented-out code.  

The README also provides a clear rationale for the project’s purpose, describing how it meets the needs of law firms by simplifying time tracking and billing transparency.

**Evidence:**
- Git commit history with clear messages  
- `.gitignore` including sensitive files  
- `DEBUG = False` in production  
- Secure deployment setup on Heroku  
- README explaining security and purpose  