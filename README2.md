## How I Achieved the Assessment Criteria (Distinction-Level Reflection)

### **Project Overview**

**Better Billing** is a full-stack Django web application designed to streamline legal billing processes.  
It allows **Fee Earners** to record and manage time entries, raise **draft invoices**, and monitor **work in progress (WIP)**, while **Partners** can post final invoices.  
The project was developed using **Django**, **PostgreSQL**, and **Bootstrap**, and deployed securely to **Heroku** with environment variables managed via `.env` for secret keys and database credentials.

The app’s goal was to make time recording and billing more intuitive and transparent for fee earners in a law firm environment. It models real-world relationships between **Clients**, **Matters**, **Time Entries**, **WIP**, and **Invoices**, offering complete CRUD functionality across all core data entities.

---

## **Learning Outcome 1 – Design, Develop and Implement a Back End**

I designed the front end with **Bootstrap** to ensure full responsiveness and consistency across screen sizes. Accessibility guidelines were followed by using semantic HTML, ARIA labels, and high-contrast colour combinations. The UX was intentionally simple and linear, reducing friction when entering time or generating invoices.

For the back end, I built a **Django project** with clearly structured apps, models, and views.  
I implemented custom HTML templates that respond dynamically to user actions, such as form submissions and validation errors, using Django’s template logic and conditional rendering.  

Data is persisted through PostgreSQL, and user interactions—like saving a Time Entry or creating an Invoice—trigger database updates and instant feedback via Django’s **messages framework**.  
This provides users with immediate confirmation of actions (e.g., “Time entry saved successfully.”).

I also followed **PEP8** conventions throughout my Python code, using descriptive variable names, consistent indentation, and comments for readability. HTML and CSS were validated using W3C and Jigsaw validators.

**Evidence:**
- Responsive Bootstrap templates with semantic structure  
- Django views and forms providing full CRUD functionality  
- User feedback on save/update/delete actions  
- PEP8-compliant codebase  

[Screenshot: Responsive Time Entry Form]  
[Screenshot: WIP List View]  

---

## **Learning Outcome 2 – Model and Manage Data**

The data model was carefully planned to mirror real-world billing relationships:

- **Client** → one-to-many → **Matters**  
- **Matter** → one-to-many → **Time Entries** and **WIP**  
- **WIP** → one-to-many → **InvoiceLines**  
- **Invoice** aggregates **WIP** for billing  

Each model includes appropriate foreign keys, validation, and string representations for clarity in the admin panel and throughout the app.  

The database is managed in PostgreSQL (configured in `DATABASE_URL`), with environment-specific settings stored centrally in `settings.py` and environment variables loaded via **`python-dotenv`**.  

I also documented the schema in the README with entity relationships and field descriptions, making the structure easy to understand and maintain.

**Evidence:**
- Normalised relational schema (ERD diagram)  
- Centralised database configuration  
- PostgreSQL in production, SQLite in development  
- `.env` for environment variables  
- `requirements.txt` and `Procfile` for dependencies and deployment  

[Screenshot: ERD Diagram of Models]  
[Link: README Schema Section]

---

## **Learning Outcome 3 – Query and Manipulate Data**

I implemented full CRUD operations across the application:

- **Create:** New Clients, Matters, Time Entries, WIP, and Invoices can be added via Django forms.  
- **Read:** Lists and detailed record pages show data retrieved dynamically using Django ORM queries and `select_related` for performance.  
- **Update:** Time Entries and draft Invoices can be edited by fee earners before posting.  
- **Delete:** Only authorised users can delete draft records, ensuring data integrity.

Each CRUD action triggers immediate reflection in the UI—recent entries update on save, and success messages confirm completion.  

Data validation prevents mismatched records (e.g., a Matter cannot be assigned to a Client that doesn’t own it), demonstrating defensive coding and robust data handling.

**Evidence:**
- Working CRUD forms and views  
- Data validation via model `clean()` methods  
- Real-time UI updates on CRUD actions  
- Toast and message feedback after user actions  

[Screenshot: CRUD Flow Example]  

---

## **Learning Outcome 4 – Deploy a Full Stack Application**

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

[Screenshot: Heroku Live App]  
[Link: README Deployment Section]

---

## **Learning Outcome 5 – Identify and Apply Security Features**

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

[Link: GitHub Repository]  

---

## **Summary**

Overall, *Better Billing* demonstrates a professional-grade Django application that models real-world billing workflows with a strong focus on usability, data integrity, and clean code.  
It includes all CRUD operations, responsive design, robust deployment, and effective documentation.  

The project showcases craftsmanship in code and structure, meeting the **Distinction criteria** through:
- A clear, justified real-world rationale  
- A well-designed relational schema  
- A professional front end with Bootstrap responsiveness  
- Fully functioning CRUD features  
- Secure, tested, and deployed codebase

---

## **Next Steps (Testing Section Placeholder)**

In the following section, I will include:
- A **manual testing table** documenting all core features (Clients, Matters, Time Entries, WIP, Invoices)  
- Screenshots and notes of test outcomes  
- Descriptions of any minor bugs and fixes applied  

[Testing section to follow below →]
