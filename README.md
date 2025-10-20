# Welcome to the Better Billing Project

## What is Better Billing?
Better Billing a demo app which is built for Legal Billing. The app focuses on the time entry, billing and invoicing side of legal billing and works off a simple database framework. 

## How Better Billing works 
Lawyers (fee earners) input their time worked with a description of the work performed submitted against a client, matter and activiy code. The administrator, in this scenario the Partners, can then pick up and review the time entries then push them to an randomly generated invoice number. 

The user interactions create data that is pushed into the database via the Record Time interface, data is then fed through to WIP and eventually onto the Invoice/Ledger tables. In line with CRUD principles the user can create, read, update and entries based on permissions. 

## Dependencies
The app relies on Django & Python alongside various imports and supporting packages to manage AJAX, SQL queries, date/time widgets, authentication, validation errors and messages. 

HTML5 is used in conjunction with the Django template format. The base template holds all the HTML document syntax alongside the load static command to globally apply the favicons, custom CSS3, Bootstrap CSS and Javascript.

## Set & Up and Installations

[Click here to read through installation and deployment steps for Github, Django and Heroku](/readme_docs/deploy_install.md)

## NB:
This version of the application works well in a small law firm scenario. It can be scaled or linked to APIs and additional features can be added to handle matter maintainance and rates, for example. Currently, the app relies on the business user having applications and/or databases that could handle the matter, personnel, rates, roles databases. 

# User Stories
This section documents how the Minimum Viable Product has been implemented in the Better Billing project to meet the outlined user stories.  

The system enables fee earners to record time and expenses, generate invoices, and give partners a clear overview of WIP (Work In Progress) and billing status. [READ MORE](/readme_docs/user_story.md)

# Bugs

** Turn this into table of bugs and fixes with "resolved?" flag(Y)

Unable to connect to Heroku CLI

Resolution: Download Command Line Tools (CLT) - also had to update MacOS to allow CLT to download

Matter ID issue arose during testing of: 
python manage.py shell -c "from better_bill_project.models import WIP; print(WIP.objects.filter(matter_id='M0032', status='unbilled').count())" 
- ID field expects number but matter IDs are integers - doesn't effect actual app functionality 

Successful submission Validation duplicating on time entry page

# Testing 

## **Testing**

### **Testing Overview**

Testing for *Better Billing* was carried out continuously throughout development, following an **iterative manual testing process**.  
Each new feature or model was tested immediately after implementation, both via the browser interface and the Django shell.  
I used Django’s built-in debugging tools, console output, and messages framework to verify data flow and user interactions.  

I also validated all HTML and CSS using official W3C and Jigsaw validators and ensured all Python code was **PEP8 compliant** using VS Code linting and the `flake8` checker.  

Below is a summary of the main test procedures and outcomes.

---

### **Manual Testing Table**

| **Feature / Functionality** | **Test Description** | **Expected Result** | **Actual Result** | **Pass/Fail** |
|------------------------------|----------------------|----------------------|-------------------|---------------|
| **Client Creation** | Add a new client via form with valid data | Client saved and visible in Client List | Works as expected | Pass |
| **Client Validation** | Submit client form with missing name | Error message displayed, client not saved | Validation error shown as expected | Pass |
| **Matter Creation** | Create new matter linked to an existing client | Matter saved with correct client relationship | Saved correctly and visible in Matter List | Pass |
| **Matter Validation** | Try linking matter to wrong client | Error message: “Selected matter does not belong to the chosen client” | Error handled and displayed cleanly | Pass |
| **Time Entry Creation** | Enter hours, activity code, and narrative | New Time Entry saved and visible under correct Matter | Functions correctly | Pass |
| **Time Entry Validation** | Enter invalid or missing hours | Error message displayed | Validation successful | Pass |
| **Time Entry Edit** | Update an existing time entry | Updated details saved correctly | Changes persist as expected | Pass |
| **Time Entry Delete** | Delete existing record | Entry removed and success message shown | Works correctly | Pass |
| **WIP Creation** | WIP auto-linked to Matter and Fee Earner | Record created and correctly calculated | Works as expected | Pass |
| **WIP Validation** | Time Entry or Client mismatch | Error message raised and prevented save | Works as intended | Pass |
| **Invoice Draft Creation** | Create a draft invoice for WIP | Draft invoice created, total and tax calculated | Totals calculated correctly | Pass |
| **Invoice Posting** | Partner posts draft invoice | Status updated to “Posted” and removed from Draft list | Works correctly | Pass |
| **Subtotal / Tax Calculation** | Check rounding and tax calculation accuracy | Subtotal * tax_rate / 100 rounded to 2dp | Accurate and formatted correctly | Pass |
| **CRUD Reflections in UI** | Perform CRUD actions and refresh page | Data updates immediately in tables/views | Reflected correctly | Pass |
| **Navigation Links** | Test all links across navbar and footer | All pages reachable, no 404s | All links functional | Pass |
| **User Feedback** | Perform actions (add/edit/delete) | Toast or alert messages shown | Messages displayed as expected | Pass |
| **Responsive Design** | Resize browser and test on mobile | Layout adjusts, navigation collapses properly | Bootstrap responsiveness confirmed | Pass |
| **Form Usability** | Tab through fields and submit with Enter | Forms behave intuitively and validate on submit | Works correctly | Pass |
| **Database Integrity** | Run migrations, seed test data | All models linked correctly, no integrity errors | Works correctly | Pass |
| **Deployment (Heroku)** | Deploy to Heroku and test live app | App matches local functionality | Matches local build with no issues | Pass |
| **Environment Security** | Check for exposed keys or DEBUG mode | No credentials visible, DEBUG=False | Verified and secure | Pass |

---

### **Testing Reflection**

Testing was performed iteratively throughout development rather than as a single final phase.  
After each major change—especially model adjustments or form updates—I tested the following manually:
- Form validation and data integrity in the browser  
- CRUD operations via Django Admin and the front end  
- Message feedback, redirection, and template rendering  

When errors occurred, they were documented and resolved immediately.  
Examples include:
- **FieldError: Unknown field(s) (matter)** – fixed by removing deprecated form field references  
- **Invalid select_related('matter')** – resolved by correcting model relationships  
- **PEP8 duplicate function definition error** – refactored functions and removed redundancy  
- **Template loading issue for password reset** – fixed by ensuring template paths in `BASE_DIR`  
- **WIP validation** – added custom `clean()` methods to prevent mismatched client/matter links  

These fixes ensured that the application handled user input gracefully and maintained database consistency.

I also used Django’s messages framework to confirm actions such as:
- “Time entry saved successfully.”  
- “Please correct the errors below.”  
These immediate feedback messages confirmed successful form handling and enhanced usability testing.

Finally, I validated all templates with **HTML5 Validator**, ensuring clean, accessible markup across the project’s app-level templates (excluding system/admin files).

---

### **Validation Results**

| **Validation Type** | **Tool Used** | **Result** |
|----------------------|---------------|------------|
| HTML | HTML 5 Validator | No major errors |
| CSS | Jigsaw CSS Validator | No issues |
| Python | PEP8 / Flake8 | All code compliant |
| Database | Django ORM Migrations | Passed with no conflicts |
| Security | `.env` + `.gitignore` + `DEBUG=False` | Passed |

---

### **Conclusion**

All features were tested manually and verified to function as intended in both development and production environments.  
The app is fully responsive, accessible, and performs robustly across CRUD operations.  

Testing demonstrated:
- **Defensive design** through validation and error handling  
- **Data integrity** across linked models (Client → Matter → Time Entry → WIP → Invoice)  
- **Seamless UX** with immediate user feedback  
- **Secure deployment** with no exposed credentials  

Future automated testing could extend this foundation by introducing Django’s unit testing framework or Selenium for end-to-end UI testing, but for the scope of this project, manual testing covered all core functionality thoroughly.

---

**Evidence:**
- [Screenshot: Form Validation Example]  
- [Screenshot: CRUD Test Results]  
- [Screenshot: Responsive View on Mobile]  
- [Screenshot: Heroku Deployment Confirmation]  

Heroku
Github
Django
Lighthouse
Mobile Responsiveness
ESLint
CSS
HTML - Downloaded HTML5 Validator via Java (Java installed via Homebrew)


# Sources

Set up of django
https://docs.djangoproject.com/en/5.2/intro/tutorial01/

Resolving 404 error
https://docs.djangoproject.com/en/5.2/ref/views/#error-views

Linking SQL to django
https://docs.djangoproject.com/en/5.2/topics/db/sql/

Adding linking CSS to HTML in Django
https://medium.com/@sowaibaarshad/connecting-css-files-with-html-in-django-5dfb1d7039

Heroku CLI
https://dashboard.heroku.com/apps/betterbilling/deploy/heroku-git
https://devcenter.heroku.com/articles/heroku-cli

Removing CLT
https://mac.install.guide/commandlinetools/6#:~:text=Line%20Tools%20folder-,The%20simple%20and%20effective%20way%20to%20uninstall%20Xcode%20Command,is%20to%20delete%20its%20folder.&text=Use%20sudo%20for%20admin%20privileges,the%20password%20after%20entering%20it 

Command Line Tools (CTL)
https://mac.install.guide/commandlinetools/3

Download link via Apple Store
https://developer.apple.com/download/all/?q=xcode

## 📚 References & Sources

### 🧱 Frameworks & Core Technologies

- **Django Software Foundation.** [*Django Documentation*](https://docs.djangoproject.com/en/5.0/)  
  Used throughout the project for model definitions, views, URL routing, and form handling.

- **PostgreSQL Global Development Group.** [*PostgreSQL 16 Documentation*](https://www.postgresql.org/docs/)  
  Used as the relational database backend for managing Clients, Matters, Time Entries, and Invoices.

- **Bootstrap Team.** [*Bootstrap v5.3 Documentation*](https://getbootstrap.com/docs/5.3/)  
  Used for front-end styling, grid layout, and responsive design.

---

### ⚙️ Deployment & Environment

- **Heroku Dev Center.** [*Deploying Python and Django Apps on Heroku*](https://devcenter.heroku.com/categories/python-support)  
  Used for deploying the project to a live environment with PostgreSQL add-on and environment variable configuration.

- **GitHub Docs.** [*About GitHub Repositories and Source Control in VS Code*](https://docs.github.com/en/repositories)  
  Used to manage version control, commits, and deployment integration from VS Code.

- **Python Software Foundation.** [*venv — Creation of Virtual Environments*](https://docs.python.org/3/library/venv.html)  
  Used to isolate dependencies for local Django setup.

- **WhiteNoise Project.** [*Serving Static Files in Production*](http://whitenoise.evans.io/en/stable/)  
  Used to efficiently serve static files on Heroku.

---

### 🧩 Additional Libraries

- **dj-database-url.** [*dj-database-url on PyPI*](https://pypi.org/project/dj-database-url/)  
  Used to configure database connections using environment variables.

- **python-dotenv.** [*python-dotenv on PyPI*](https://pypi.org/project/python-dotenv/)  
  Used for managing environment variables locally during development.

- **gunicorn.** [*gunicorn on PyPI*](https://pypi.org/project/gunicorn/)  
  Used as the WSGI HTTP server for deployment on Heroku.

---

### 🧪 Testing & Validation

- **Django Software Foundation.** [*Testing in Django*](https://docs.djangoproject.com/en/5.0/topics/testing/)  
  Used as a reference for writing and running unit and integration tests.

- **validator.nu.** [*HTML5 Validator API*](https://validator.w3.org/nu/)  
  Used to validate HTML templates to ensure semantic accuracy and accessibility.

- **Code Institute.** [*Python Linter & PEP8 Guidelines*](https://pep8.org/)  
  Used to ensure PEP8 compliance throughout the project.

---

### 🧠 Tutorials & Learning References

- **Code Institute.** *Full Stack Development Course Materials (Django)*  
  Provided project structure, deployment patterns, and test writing methodology used as a base for this project.

- **Traversy Media.** [*Django Crash Course (YouTube)*](https://www.youtube.com/watch?v=e1IyzVyrLSU)  
  Helped reinforce understanding of CRUD operations and Django admin setup.

- **Corey Schafer.** [*Django Tutorial Series (YouTube)*](https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH)  
  Referenced for understanding model relationships and query optimization.

---

### 🧾 Formatting & Documentation

- **GitHub Docs.** [*Mastering Markdown*](https://guides.github.com/features/mastering-markdown/)  
  Used for README.md formatting and linking screenshots.


