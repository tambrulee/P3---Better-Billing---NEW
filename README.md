# Welcome to the Better Billing Project

## 📑 Project Documentation

## What is Better Billing?

**Better Billing** is a full-stack Django web application designed to streamline legal billing processes.  

It allows **Fee Earners** to record and manage time entries, raise **draft invoices**, and monitor **work in progress (WIP)**, while **Partners** can post final invoices.  
The project was developed using **Django**, **PostgreSQL**, and **Bootstrap**, and deployed securely to **Heroku** with environment variables managed via `.env` for secret keys and database credentials.

The app’s goal was to make time recording and billing more intuitive and transparent for fee earners in a law firm environment. It models real-world relationships between **Clients**, **Matters**, **Time Entries**, **WIP**, and **Invoices**, offering complete CRUD functionality across all core data entities.

## How Better Billing works 
Lawyers (fee earners) input their time worked with a description of the work performed submitted against a client, matter and activiy code. The administrator, in this scenario the Partners, can then pick up and review the time entries then push them to an randomly generated invoice number. 

The user interactions create data that is pushed into the database via the Record Time interface, data is then fed through to WIP and eventually onto the Invoice/Ledger tables. In line with CRUD principles the user can create, read, update and entries based on permissions. 

## Dependencies
I designed the front end with **Bootstrap** to ensure full responsiveness and consistency across screen sizes. Accessibility guidelines were followed by using semantic HTML, ARIA labels, and high-contrast colour combinations. The UX was intentionally simple and linear, reducing friction when entering time or generating invoices.

For the back end, I built a **Django project** with clearly structured apps, models, and views.  
I implemented custom HTML templates that respond dynamically to user actions, such as form submissions and validation errors, using Django’s template logic and conditional rendering.  

Data is persisted through PostgreSQL, and user interactions—like saving a Time Entry or creating an Invoice—trigger database updates and instant feedback via Django’s **messages framework**.  
This provides users with immediate confirmation of actions (e.g., “Time entry saved successfully.”).

I also followed **PEP8** conventions throughout my Python code, using descriptive variable names, consistent indentation, and comments for readability. HTML and CSS were validated using W3C and Jigsaw validators.

## Set & Up and Installations

[Click here to read through installation and deployment steps for Github, Django and Heroku](/readme_docs/deploy_install.md)

## NB:
This version of the application works well in a small law firm scenario. It can be scaled or linked to APIs and additional features can be added to handle matter maintainance and rates, for example. Currently, the app relies on the business user having applications and/or databases that could handle the matter, personnel, rates, roles databases. 

### Design, Development & Implementation

- #### [User Stories](/readme_docs/user_story.md)

- #### [UX](/readme_docs/ux.md)

- #### [Testing](/readme_docs/testing.md)

### Data Model Management

- #### [Database Models & Schema](/readme_docs/db_schema.md)

### Queries & Data Manipulation

- #### [CRUD](/readme_docs/crud.md)

### Deployment

- #### [Heroku](/readme_docs/heroku.md)

### Security

- #### [Repository Management](/readme_docs/git.md)

### Issues & Fixes
- #### [Bugs](/readme_docs/bugs.md)

# Sources

View all reading materials and sources [here](/readme_docs/sources.md)


