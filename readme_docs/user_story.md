# User Stories

## Project Summary – Better Billing

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

---

## Overall Status
All user stories from **1.1 through 3.1** have been successfully implemented and verified through functional testing.  
The application now provides a full workflow — from time and expense recording to invoicing and performance reporting.

## CRUD Implementation Overview

This project implements full (or intentionally constrained) CRUD for **Time Entries**, **Expenses**, and **Invoices** (drafts editable; posted read-only). Below is a concise breakdown of how each operation is achieved.

---

### TimeEntry (WIP)
**Model:** `TimeEntry(matter, fee_earner, activity_code, hours_worked, narrative, status, created_at, …)`  
**Form:** `TimeEntryForm` (validates duration > 0, required narrative, valid activity code; matter must be open)

| Operation | How it’s Achieved | Route / View | Template(s) | Notes / Permissions |
|---|---|---|---|---|
| **Create** | POST valid form → `form.save()` links to open `Matter` and marks as **unbilled/draft** | `POST /time/new` → `record_time` | `better_bill_project/record.html` | Success/error via Django messages; recent 10 entries shown |
| **Read** | List recent entries (with `select_related`) and detail view | `GET /time` (list), `GET /time/<id>` (detail) | `record.html` (list), `time_detail.html` | Ordered `-created_at`; quick audit visibility |
| **Update** | Edit form for unbilled entries only | `POST /time/<id>/edit` | `time_edit.html` | If linked to **posted** invoice → blocked with “Locked” |
| **Delete** | Delete unbilled entries | `POST /time/<id>/delete` | Confirm partial `time_confirm_delete.html` | Disallowed if entry is drafted into an approved/posted invoice |

---

### Expense
**Model:** `Expense(matter, amount, vat_flag, receipt, status, …)`  
**Form:** `ExpenseForm` (validates amount > 0; file type PDF/JPG/PNG; VAT derived when flagged)

| Operation | How it’s Achieved | Route / View | Template(s) | Notes / Permissions |
|---|---|---|---|---|
| **Create** | POST valid form; receipt uploaded to storage; VAT computed | `POST /expenses/new` → `expense_create` | `expenses/new.html` | Links to `Matter`; appears in unbilled expenses |
| **Read** | List and filter by matter; detail view for receipt preview | `GET /expenses` (list), `GET /expenses/<id>` (detail) | `expenses/list.html`, `expenses/detail.html` | Feeds draft invoice generator |
| **Update** | Edit amount/VAT/receipt while unbilled | `POST /expenses/<id>/edit` | `expenses/edit.html` | Locked once included on **posted** invoice |
| **Delete** | Delete while unbilled | `POST /expenses/<id>/delete` | `expenses/confirm_delete.html` | Disallowed once linked to **posted** |

---

### Invoice (Draft → Posted)
**Models:**  
- `Invoice(client|matter, status, subtotal, tax_rate, tax_amount@property, total@property, …)`  
- `InvoiceLine(invoice, wip|expense, narrative_override, amount, …)`  
**Forms/Logic:** Draft creation aggregates **unbilled** time + expenses; lines created with amounts & optional `narrative_override`

| Operation | How it’s Achieved | Route / View | Template(s) | Notes / Permissions |
|---|---|---|---|---|
| **Create** | “Create Draft” aggregates unbilled WIP/Expenses → `Invoice` + `InvoiceLine`s | `POST /invoices/draft/create?matter=<id>` | `invoices/draft.html` | Source rows flagged as **drafted** to avoid duplication |
| **Read** | Draft list/detail; posted list/detail; print/preview | `GET /invoices`, `GET /invoices/<id>` | `invoices/list.html`, `invoices/detail.html` | Totals via model properties; VAT shown |
| **Delete** | Delete entire draft or remove a line | `POST /invoices/<id>/delete`, `POST /invoices/<id>/lines/<line_id>/delete` | `invoices/confirm_delete.html` | Deleting draft unlocks its WIP/Expenses |
| **Post** | Partner-only “Post” locks invoice + linked entries | `POST /invoices/<id>/post` | `invoices/detail.html` | Changes `status='posted'`; all linked entries read-only |

---

## Permissions & Locking Summary
- **Roles:** Fee Earner (create/edit own unbilled), Partner (approve/post), Admin (override unlocks when required).
- **Locking Rules:**  
  - Time/Expense on a **posted** invoice → **no Update/Delete**.  
  - Draft invoices editable; **posted invoices read-only**.  
  - Attempted edits on locked records show “Locked – entry linked to posted invoice”.

---

## Validation & Integrity
- **Forms:** Business rules at form level (positive amounts/hours, narrative required, acceptable files).  
- **Models:** Calculations via properties (`tax_amount`, `total`) to keep totals consistent.  
- **Views:** Guard rails (e.g., check status before allowing Update/Delete).  
- **Querysets:** `select_related`/`prefetch_related` for efficient lists (recent time entries, invoice lines).  
- **Messages/UI:** Success and error messages; conditional buttons (hide edit/delete when locked).

---

## Reuse & UX Patterns
- **Shared partials** for forms and line tables.  
- **Recent activity** widget (last 10 time entries) for quick feedback.  
- **AJAX** for narrative edits/preview refresh in drafts.  
- **Consistent routes** and CSRF-protected POST actions for all mutations.


