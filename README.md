# Welcome to the Better Billing Project

## What is Better Billing?
Better Billing a demo app which is built for Legal Billing. The app focuses on the time entry, billing and invoicing side of legal billing and works off a simple database framework. 

## How Better Billing works 
Lawyers (fee earners) input their time worked with a description of the work performed submitted against a client, matter and activiy code. The administrator, in this scenario the Partners, can then pick up and review the time entries then push them to an randomly generated invoice number. 

The user interactions create data that is pushed into the database via the Record Time interface, data is then fed through to WIP and eventually onto the Invoice/Ledger tables. In line with CRUD principles the user can create, read, update and entries based on permissions. 

## Dependencies
The app relies on Django & Python alongside various imports and supporting packages to manage AJAX, SQL queries, date/time widgets, authentication, validation errors and messages. 

HTML5 is used in conjunction with the Django template format. The base template holds all the HTML document syntax alongside the load static command to globally apply the favicons, custom CSS3, Bootstrap CSS and Javascript.

## NB:
This version of the application works well in a small law firm scenario. It can be scaled or linked to APIs and additional features can be added to handle matter maintainance and rates, for example. Currently, the app relies on the business user having applications and/or databases that could handle the matter, personnel, rates, roles databases. 

# User Stories

## 🧮 Project Summary – Better Billing

This section documents how the **core billing workflow** has been implemented in the Better Billing project to meet the outlined user stories.  
The system enables fee earners to record time and expenses, generate invoices, and give partners a clear overview of WIP (Work In Progress) and billing status.  

---

### **1.1 Record Time**
**Goal:**  
Allow fee earners to record hours worked on matters for accurate client billing.

**Implementation Details:**  
- The **TimeEntry** model captures key data: `matter`, `fee_earner`, `activity_code`, `hours_worked`, and `narrative`.  
- The **TimeEntryForm** enforces validation rules ensuring positive durations, valid activity codes, and required narratives.  
- When a new entry is created, it’s linked to an **open matter** and saved as **unbilled (draft)**.  
- A **recent entries list** displays the last ten submissions for easy reference.  
- Django messages confirm successful saves or validation errors.

 **Achieved:** The manual time entry workflow functions as expected and correctly updates the matter’s unbilled totals.

**Links:**  
[Time entry interface](/readme_docs/user_stories/record_hours.png),  
[Line item entries](/readme_docs/user_stories/recent_entries.png)

---

### **1.2 Edit/Lock Time**
**Goal:**  
Prevent editing or deletion of time entries once they are billed or included in a posted invoice.

**Implementation Details:**  
- Conditional logic disables editing when an entry’s related invoice has `status="posted"`.  
- The UI hides or disables edit/delete buttons for locked entries.  
- Attempted edits trigger a warning (“Locked – entry linked to posted invoice”).  
- Only admins can override this for audit purposes.

 **Achieved:** Time entries are correctly locked after billing, preserving financial data integrity.

**Links:**  
[Locked entry message](/readme_docs/user_stories/locked_entry.png)

---

### **1.3 Record Expenses**
**Goal:**  
Allow fee earners to record recoverable expenses and attach receipts.

**Implementation Details:**  
- The **Expense** model captures `amount`, `vat_flag`, `receipt`, and `matter`.  
- File validation ensures accepted types (PDF, JPG, PNG).  
- VAT is auto-calculated when applicable.  
- Saved expenses appear in the **unbilled expenses** list and feed into draft invoices.

 **Achieved:** Expense capture, VAT handling, and linkage to invoice generation are working as intended.

**Links:**  
[Expense entry form](/readme_docs/user_stories/record_expense.png),  
[Unbilled expense list](/readme_docs/user_stories/unbilled_expenses.png)

---

### **2.1 Generate Draft Invoice**
**Goal:**  
Enable fee earners to generate draft invoices from unbilled time and expenses.

**Implementation Details:**  
- The **Invoice** model aggregates all unbilled **WIP** and **Expense** entries for a given matter or client.  
- Drafts include calculated subtotals, VAT, and totals via model property methods.  
- Once generated, items are flagged as **drafted** to prevent reuse.  
- Drafts remain editable until approved by a partner.

 **Achieved:** Draft invoice generation works seamlessly, pulling unbilled time and expenses together.

**Links:**  
[Draft invoice view](/readme_docs/user_stories/draft_invoice.png),  
[Invoice summary](/readme_docs/user_stories/invoice_summary.png)

---

### **2.2 Edit Narratives**
**Goal:**  
Allow fee earners to refine line-item narratives on draft invoices before posting.

**Implementation Details:**  
- Editable narrative fields are exposed at the **invoice line** level.  
- Updates are stored independently, preserving original time entry data.  
- Validation limits and formatting checks ensure clarity.  
- Live updates via AJAX refresh the preview immediately after saving.

 **Achieved:** Narrative editing updates the invoice draft without altering original time entries.

**Links:**  
[Narrative edit form](/readme_docs/user_stories/edit_narrative.png),  
[Preview update](/readme_docs/user_stories/narrative_preview.png)

---

### **2.3 Approve & Post Invoice**
**Goal:**  
Allow partners to approve and post invoices, finalising billing.

**Implementation Details:**  
- The **“Post”** button is visible only to users with the Partner role.  
- Posting changes invoice status to `posted` and locks linked WIP/Expense entries.  
- Posted invoices are read-only and excluded from new drafts.  
- Totals update dynamically in the reports view.

 **Achieved:** Approval and posting workflows function correctly with appropriate access control.

**Links:**  
[Invoice approval view](/readme_docs/user_stories/approve_invoice.png),  
[Posted invoice summary](/readme_docs/user_stories/posted_invoice.png)

---

### **3.1 WIP & Invoice Overview**
**Goal:**  
Provide partners with a high-level overview of WIP, draft invoices, and posted invoices.

**Implementation Details:**  
- The **WIP dashboard** aggregates totals for:
  - Unbilled time  
  - Draft invoices  
  - Posted invoices  
- Data grouped by matter shows hours, values, and VAT.  
- Partners can drill down into categories for details.  
- No aged-debt tracking (intentionally excluded).  
- Access restricted to partner-level users.

 **Achieved:** Dashboard provides clear and concise billing overviews for partners.

**Links:**  
[WIP summary view](/readme_docs/user_stories/wip_overview.png),  
[Invoice totals chart](/readme_docs/user_stories/invoice_overview.png)

---

## Technical Summary
- **Backend:** Django ORM, model forms, and class-based views manage all CRUD operations.  
- **Validation:** Form-level checks plus business rules embedded in model clean methods.  
- **Frontend:** Django templates (DTL), Bootstrap for layout, and JavaScript for interactivity.  
- **Security:** Role-based permissions ensure appropriate visibility and control.  
- **Data Integrity:** Locked entries and cascading updates ensure consistent invoice totals.  
- **Storage:** Local file storage for uploaded receipts and related documents.  

---

## Overall Status
All user stories from **1.1 through 3.1** have been successfully implemented and verified through functional testing.  
The application now provides a full workflow — from time and expense recording to invoicing and performance reporting.



# UX
 ### Wire Frames


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

** Turn this into table of bugs and fixes with "resolved?" flag(Y)

Unable to connect to Heroku CLI

Resolution: Download Command Line Tools (CLT) - also had to update MacOS to allow CLT to download

Matter ID issue arose during testing of: 
python manage.py shell -c "from better_bill_project.models import WIP; print(WIP.objects.filter(matter_id='M0032', status='unbilled').count())" 
- ID field expects number but matter IDs are integers - doesn't effect actual app functionality 

Successful submission Validation duplicating on time entry page

# Testing 

Heroku
Github
Django
Lighthouse
Mobile Responsiveness
ESLint
CSS
HTML - Downloaded HTML5 Validator via Java (Java installed via Homebrew)

CODE:
mkdir -p site_dump
wget -e robots=off --recursive --no-clobber --page-requisites \
     --adjust-extension --convert-links --no-parent \
     http://127.0.0.1:8000/ -P site_dump

html5validator --root site_dump --blacklist admin static media \
               --format text --show-warnings

"file:/Users/tambrulee/Documents/Code%20Institute/P3%20-%20Better%20Billing%20-%20NEW/site_dump/127.0.0.1:8000/admin/index.html":44.3-44.53: error: Element "div" not allowed as child of element "button" in this context. (Suppressing further errors from this subtree.)

Warning: Consider adding a "lang" attribute to the "html" start tag to declare the language of this document.
From line 2, column 16; to line 3, column 6 in resource file:/Users/tambrulee/Documents/Code%20Institute/P3%20-%20Better%20Billing%20-%20NEW/site_dump/127.0.0.1:8000/view_invoice.html%3Fstatus=draft.html
Warning: Consider adding a "lang" attribute to the "html" start tag to declare the language of this document.
From line 2, column 16; to line 3, column 6 in resource file:/Users/tambrulee/Documents/Code%20Institute/P3%20-%20Better%20Billing%20-%20NEW/site_dump/127.0.0.1:8000/view_invoice.html%3Fstatus=posted.html
Warning: Consider adding a "lang" attribute to the "html" start tag to declare the language of this document.
From line 2, column 16; to line 3, column 6 in resource file:/Users/tambrulee/Documents/Code%20Institute/P3%20-%20Better%20Billing%20-%20NEW/site_dump/127.0.0.1:8000/index.html
Warning: Consider adding a "lang" attribute to the "html" start tag to declare the language of this document.
From line 2, column 16; to line 3, column 6 in resource file:/Users/tambrulee/Documents/Code%20Institute/P3%20-%20Better%20Billing%20-%20NEW/site_dump/127.0.0.1:8000/create_invoice.html
Warning: Consider adding a "lang" attribute to the "html" start tag to declare the language of this document.
From line 2, column 16; to line 3, column 6 in resource file:/Users/tambrulee/Documents/Code%20Institute/P3%20-%20Better%20Billing%20-%20NEW/site_dump/127.0.0.1:8000/record.html
Warning: Consider adding a "lang" attribute to the "html" start tag to declare the language of this document.
From line 2, column 16; to line 3, column 6 in resource file:/Users/tambrulee/Documents/Code%20Institute/P3%20-%20Better%20Billing%20-%20NEW/site_dump/127.0.0.1:8000/view_invoice.html
Error: Stray end tag "head".
From line 9, column 3; to line 9, column 9 in resource file:/Users/tambrulee/Documents/Code%20Institute/P3%20-%20Better%20Billing%20-%20NEW/site_dump/127.0.0.1:8000/accounts/password_reset/index.html
Error: Start tag "body" seen but an element of the same type was already open.
From line 10, column 3; to line 10, column 8 in resource file:/Users/tambrulee/Documents/Code%20Institute/P3%20-%20Better%20Billing%20-%20NEW/site_dump/127.0.0.1:8000/accounts/password_reset/index.html
Document checking completed.
(.venv) (base) tambrulee@Tamsins-MacBook-Pro P3 - Better Billing - NEW % 

Python


heroku open -a betterbilling 
Check app is active
heroku apps:info -a betterbilling
Check info about app


python manage.py makemigrations
python manage.py migrate
python manage.py runserver

python manage.py showmigrations better_bill_project
