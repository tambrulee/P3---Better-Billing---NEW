# User Stories
1) Matters & Clients

Create Matter

As a fee earner, I want to create a new matter linked to a client, so that time and costs are tracked correctly.
AC: Given a client exists, When I submit matter name/type/responsible solicitor, Then a unique matter ID is created and shown on the matter page.

Search & Filter Matters

As a fee earner, I want to search matters by client, status, and date, so that I can find active work quickly.
AC: Given filters, When I apply them, Then only matching matters display and the result count updates.

Matter Status

As a practice manager, I want to mark matters as Open/On Hold/Closed, so that billing is controlled.
AC: Given a matter, When I change status to Closed, Then new time entries are prevented and users see a warning.

2) Time & Expense Tracking

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

3) Rates & Pricing

Rate Cards

As a practice manager, I want to set hourly rates by role and override per matter, so that billing matches agreements.
AC: Given a matter override, When time is added, Then the overridden rate is used on the invoice preview.

Fixed/Cap Fees

As a fee earner, I want to set fixed fees or fee caps on a matter, so that invoices respect limits.
AC: Given a fee cap, When cumulative billable time exceeds the cap, Then the system warns and caps billable amount.

4) Invoicing

Generate Draft Invoice

As a fee earner, I want to generate a draft invoice from unbilled time/expenses, so that I can review before sending.
AC: Given unbilled items, When I click “Create Draft,” Then a draft with line items, totals, and VAT is produced.

Edit Narratives

As a fee earner, I want to edit line-item narratives on the draft, so that clients see clear descriptions.
AC: Given a draft invoice, When I edit a narrative and save, Then the PDF preview reflects the change.

Invoice Approval Workflow

As a practice manager, I want approve/reject with comments, so that quality control is enforced.
AC: Given a draft invoice, When I click Approve, Then status becomes “Approved” and entries become locked.

Send & PDF

As a fee earner, I want to email a branded PDF to the client, so that billing is formalized.
AC: Given an approved invoice, When I click Send, Then a PDF is generated and an email log entry is created.

Credit Notes

As a practice manager, I want to issue credit notes, so that billing errors can be corrected.
AC: Given a posted invoice, When I create a credit note, Then balances update and an audit link connects both docs.

5) Payments & Trust (Client) Account

Record Payments

As a cashier, I want to record payments (bank/card) against invoices, so that balances reduce.
AC: Given an invoice, When I record a payment, Then outstanding amount updates and a receipt can be produced.

Trust Deposits & Transfers

As a cashier, I want to record client account deposits and transfer to office account on billing, so that compliance is met.
AC: Given trust funds and an approved invoice, When I transfer, Then the trust ledger decreases and invoice balance reduces accordingly.

WIP & Aged Debt

As a practice manager, I want WIP and aged receivables views, so that I can chase overdue balances.
AC: Given outstanding items, When I open reports, Then totals are grouped by aging buckets (0–30, 31–60, etc.).

6) Compliance, Security & Audit

Role-Based Access

As a system admin, I want roles (Admin, Manager, Fee Earner, Cashier, Read-Only), so that data access is controlled.
AC: Given user role, When accessing restricted pages, Then unauthorized views/actions are blocked.

Audit Trail

As a auditor, I want an immutable audit log of key events, so that I can verify compliance.
AC: Given actions (create/edit/approve/post/transfer), When they occur, Then entries are timestamped with user and before/after values.

GDPR/Data Retention

As a admin, I want to anonymize or delete client data after retention periods, so that we comply with GDPR.
AC: Given a matter closed > retention period, When I run retention, Then PII is anonymized except legally required records.

7) Reporting & Analytics

Billable Utilization

As a practice manager, I want dashboards for hours billed vs target per fee earner, so that productivity is visible.
AC: Given time data, When I select a month, Then charts show billed hours, targets, and variance.

Realization Rates

As a practice manager, I want actual billed vs standard rates, so that I can see discount impact.
AC: Given rate data, When I run the report, Then realization % is calculated per matter and overall.

8) Admin & Configuration

Tax & Currencies

As a admin, I want to configure VAT rate and currency symbol, so that totals calculate correctly.
AC: Given a VAT rate change, When I update settings, Then new invoices use the new rate and show it on the PDF.

Activity Codes & Templates

As a admin, I want to manage activity codes and invoice templates, so that entries and documents are standardized.
AC: Given a new activity code, When saved, Then it appears in time-entry dropdowns immediately.

Client Contacts

As a admin, I want to store billing contacts and email preferences, so that invoices route to the right person.
AC: Given a client billing contact, When I send an invoice, Then it emails the configured recipient(s).

Non-Functional Requirements (quick list)

Security: Encrypted at rest/in transit; RBAC; strong password policy.

Auditability: Immutable logs for financial actions.

Reliability: 99.9% uptime target (project sim: graceful error states).

Performance: List pages load < 2s with 5k records.

Usability: Accessible forms (WCAG AA), clear validation.

Data Protection: GDPR-compliant retention & right-to-erasure workflow.

Nice-to-Have (stretch)

Bank feed import (CSV) for payments reconciliation.

Basic LEDES export or CSV invoice export.

Client portal for viewing invoices and making payments.

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