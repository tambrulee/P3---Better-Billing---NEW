# Welcome to the Better Billing Project

Better Billing a demo app which is built for Legal Billing. The app focuses on the time entry, billing and invoicing side of legal billing and works off a simple database framework. 

Lawyers simply input their time worked with a description of the work performed submitted against a client, matter and activiy code. The billing team can then pick up and review the time entries then push them to an randomly generated invoice number. 

# User Stories
1) Time & Expense Tracking

Start/Stop Timer

As a fee earner, I want a start/stop timer on a matter, so that my time is captured accurately.
AC: Given a matter page, When I press Start and then Stop, Then a draft time entry with elapsed time is created.

Manual Time Entry

As a fee earner, I want to log time manually with activity code and narration, so that I can record offline work.
AC: Given I enter duration, rate, activity code, and narrative, When I save, Then the entry totals appear on the matter.

Edit/Lock Time

As a practice manager, I want to lock time after invoice approval, so that billed entries aren’t altered.
AC: Given an entry is on an approved invoice, When a user attempts edit/delete, Then the action is blocked with a message.

Record Expenses

As a fee earner, I want to add disbursements (e.g., court fees) with receipts, so that costs are billed.
AC: Given amount + VAT flag + receipt upload, When I save, Then expense appears in the matter’s unbilled list.

2) Invoicing

Generate Draft Invoice

As a fee earner, I want to generate a draft invoice from unbilled time/expenses, so that I can review before sending.
AC: Given unbilled items, When I click “Create Draft,” Then a draft with line items, totals, and VAT is produced.

Edit Narratives

As a fee earner, I want to edit line-item narratives on the draft, so that clients see clear descriptions.
AC: Given a draft invoice, When I edit a narrative and save, Then the PDF preview reflects the change.


3) Revenue


WIP & Aged Debt

As a practice manager, I want WIP and aged receivables views, so that I can chase overdue balances.
AC: Given outstanding items, When I open reports, Then totals are grouped by aging buckets (0–30, 31–60, etc.).

# MVP

# GIT and Heroku deployment

# CRUD

Create
- User can create line entries

Read
- User can read line entries & invoices

Update
- User can edit line entries & invoices

Delete
- User can purge line entries & reverse invoices*

*Line entries and invoices will not be fully deleted from the database but marked as reversed permanently

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


# Django & Heroku set up

1. Installed latest version of Python 
2. Used pip to install Django
3. 
Logged into Heroku - selected build new app
Under 'Deploy' I connected my repo

# Bugs

Unable to connect to Heroku CLI

Resolution: Download Command Line Tools (CLT) - also had to update MacOS to allow CLT to download

# Testing 

heroku open -a betterbilling 
Check app is active
heroku apps:info -a betterbilling
Check info about app


python manage.py makemigrations
python manage.py migrate
python manage.py runserver