# Better Billing — Permissions & User Stories

## User Stories

### 1) Dashboard (Index)
- **As an Fee Earner**, I want to view only my own unbilled time so that I can track what remains to bill.  
- **As an Associate Partner**, I want to view my own and my delegates’ unbilled time so that I can oversee team progress.  
- **As a Partner**, I want to view my own and my delegates’ unbilled time so that I can plan billing cycles efficiently.  
- **As a Billing user**, I want to view all dashboard metrics without click-through so that I can monitor overall billing without altering data.

### 2) Record Time
- **As an Fee Earner**, I want to record my own time so that my billable hours are captured accurately.  
- **As an Associate Partner**, I want to record my own time so that my work is tracked consistently.  
- **As a Partner**, I want to record my own time so that my client work is billable and transparent.

### 3) View Time
- **As an Fee Earner**, I want to view my own recorded time so that I can confirm what has been billed or remains unbilled.  
- **As an Associate Partner**, I want to view my own and my delegates’ time so that I can ensure all billable work is recorded correctly.  
- **As a Partner**, I want to review my own and delegates’ time entries so that I can oversee billing readiness and performance.  
- **As a Billing user**, I want to view all time entries in read-only mode so that I can verify entries before posting invoices.  
- **As an Admin**, I want to read all time entries so that I can assist in audits and maintain oversight without modifying data.

### 4) Edit Time
- **As an Fee Earner**, I want to edit my own unbilled time so that I can correct errors before invoicing.  
- **As an Associate Partner**, I want to edit my own unbilled time so that my records remain accurate.  
- **As a Partner**, I want to edit my own unbilled time so that client invoices reflect correct details.

### 5) Delete Time
- **As an Fee Earner**, I want to delete my own unbilled time so that I can remove accidental entries.  
- **As an Associate Partner**, I want to delete my own unbilled time so that I can maintain clean and accurate records.  
- **As a Partner**, I want to delete my own unbilled time so that unnecessary or duplicated entries are removed before billing.

### 6) Create Invoice (Draft)
- **As an Associate Partner**, I want to create draft invoices for myself and my delegates so that client billing can begin promptly.  
- **As a Partner**, I want to create draft invoices for myself and my delegates so that I can manage billing across my matters efficiently.

### 7) Post/Delete Invoice (Finalise)
- **As a Billing user**, I want to post or delete invoices so that I can finalise or correct client billing once partner approval is confirmed.

### 8) View Invoice
- **As an Associate Partner**, I want to view invoices for myself and my delegates so that I can monitor billing progress.  
- **As a Partner**, I want to view all invoices so that I can oversee billing activity across the firm.  
- **As a Billing user**, I want to view all invoices so that I can verify amounts and maintain records.

### 9) Mark Invoice as Paid (Future Scope)
- *(Not currently permitted to any role.)* **Planned**: As a Billing user, I want to mark invoices as paid so that ledger statuses reflect received payments.

---

## User Story Implementation

This section documents how the **core billing workflow** has been implemented in the Better Billing project to meet the outlined user stories.  
The system enables fee earners to record time and expenses, generate invoices, and give partners a clear overview of WIP (Work In Progress) and billing status.

### 1.1 Record Time
**Goal:** Allow fee earners to record hours worked on matters for accurate client billing.  
**Implementation Details:**  
- `TimeEntry` model: `matter`, `fee_earner`, `activity_code`, `hours_worked`, `narrative`.  
- `TimeEntryForm` validates positive duration, valid activity code, required narrative.  
- New entries link to an **open matter** and save as **unbilled (draft)**.  
- “Recent entries” shows the last 10 submissions.  
- Django messages confirm saves or validation errors.  
**Achieved:** Correctly updates matter’s unbilled totals.

### 1.2 Edit/Lock Time
**Goal:** Prevent editing/deletion once billed or included in a posted invoice.  
**Implementation Details:**  
- Editing disabled when linked invoice has `status="posted"`.  
- UI hides/disables edit/delete buttons when locked.  
- Attempted edits show “Locked – entry linked to posted invoice”.  
- Admin override allowed for audit purposes.  
**Achieved:** Financial data integrity preserved.

### 2.1 Generate Draft Invoice
**Goal:** Generate draft invoices from unbilled time/expenses.  
**Implementation Details:**  
- `Invoice` aggregates unbilled WIP/Expenses for a matter/client.  
- Drafts compute subtotals, VAT, totals (model properties).  
- Source items flagged as **drafted** to prevent reuse.  
- Drafts remain editable until partner approval.  
**Achieved:** Unbilled items flow cleanly into drafts.

### 2.2 Edit Narratives
**Goal:** Refine line-item narratives on draft invoices.  
**Implementation Details:**  
- Editable narrative fields at `InvoiceLine` level.  
- Updates stored independently of original time entries.  
- Validation limits and formatting checks.  
- Live preview refresh via AJAX.  
**Achieved:** Drafts update without altering source entries.

### 2.3 Approve & Post Invoice
**Goal:** Allow partners to approve and post invoices.  
**Implementation Details:**  
- “Post” visible to Partner role only.  
- Posting sets `status="posted"` and locks linked entries.  
- Posted invoices are read-only; excluded from new drafts.  
- Totals update in reports.  
**Achieved:** Approval/posting with proper access control.

### 2.4 Mark Invoice as Paid

**Goal:** Allow billing users to mark invoices as paid once payment has been received.
**Implementation Details:**
- “Mark as Paid” button is visible only to users with the Billing role.
- Action updates the linked Ledger record, setting status="paid".
- Idempotent logic prevents double payment marking.
- System messages confirm updates (“Invoice successfully marked as paid”).
- Once paid, the invoice and its ledger entry become read-only.

**Achieved:** Payment tracking integrated directly into the billing workflow, ensuring clear separation between posting and settlement stages.

### 3.1 WIP & Invoice Overview
**Goal:** High-level overview of WIP, drafts, and posted invoices.  
**Implementation Details:**  
- Dashboard totals for: unbilled time, drafts, posted invoices.  
- Grouping by matter (hours, values, VAT).  
- Drill-down into categories.  
- Aged-debt tracking intentionally excluded.  
- Access: partner-level only.  
**Achieved:** Clear billing overview.

---

## Technical Summary
- **Backend:** Django ORM, model forms, class-based views for CRUD.  
- **Validation:** Form checks + model `clean()` business rules.  
- **Frontend:** Django templates (DTL), Bootstrap, light JS for interactivity.  
- **Security:** Role-based permissions align with matrix above.  
- **Data Integrity:** Locking and cascades keep totals consistent.

## CRUD Implementation Overview

### TimeEntry (WIP)
**Model:** `TimeEntry(matter, fee_earner, activity_code, hours_worked, narrative, status, created_at, …)`  
**Form:** `TimeEntryForm` (positive durations, narrative required, valid activity codes; matter must be open)

| Operation | How it’s Achieved | Route / View | Template(s) | Notes / Permissions |
|---|---|---|---|---|
| Create | POST valid form → save to open `Matter`, mark **unbilled** | `POST /time/new` → `record_time` | `better_bill_project/record.html` | Messages for success/errors; recent 10 entries |
| Read | List + detail views (efficient with `select_related`) | `GET /time` (list), `GET /time/<id>` | `record.html`, `time_detail.html` | Ordered `-created_at` for audit |
| Update | Edit only while unbilled | `POST /time/<id>/edit` | `time_edit.html` | Blocked if linked to **posted** invoice |
| Delete | Delete only while unbilled | `POST /time/<id>/delete` | `time_confirm_delete.html` | Disallowed if drafted/posted |

### **Invoice (Draft → Posted → Paid)**
**Models:** `Invoice(...)`, `InvoiceLine(invoice, wip|expense, narrative_override, amount, …)`, `Ledger(invoice, status, paid_at, …)`

| Operation | How it’s Achieved | Route / View | Template(s) | Notes / Permissions |
|---|---|---|---|---|
| **Create** | Aggregates unbilled WIP/Expenses into a draft invoice and line items | `POST /invoices/draft/create?matter=<id>` | `invoices/draft.html` | Flags source entries as **drafted** to prevent reuse |
| **Read** | Displays draft, posted, and paid invoices with print/preview options | `GET /invoices`, `GET /invoices/<id>` | `invoices/list.html`, `invoices/detail.html` | Totals calculated via model properties; paid status reflected from ledger |
| **Delete** | Deletes an unposted draft or removes a line item | `POST /invoices/<id>/delete` | `invoices/confirm_delete.html` | Deleting a draft **unlocks** associated WIP/Expense items |
| **Post** | Partner approves and billing user posts invoice | `POST /invoices/<id>/post` | `invoices/detail.html` | Sets `status='posted'`; locks linked WIP/Expense entries from further edits |
| **Mark as Paid** | Billing user updates the invoice’s linked ledger entry to `status='paid'` and sets `paid_at=timezone.now()` | `POST /invoices/<id>/settle` | `invoices/detail.html` | Only visible to **Billing** role; prevents repeat marking; displays success message (“Invoice successfully marked as paid”) |

---

## Permissions & Locking Summary
- **Roles:** Fee Earner (create/edit own unbilled), Associate/Partner (oversight), Billing (finalise invoices), Admin (read-only audits).  
- **Locking Rules:**  
  - Time/Expense on a **posted** invoice → no update/delete.  
  - Draft invoices editable; **posted** invoices read-only.  
  - Attempted edits on locked records show a clear warning.

## Permissions Matrix

| Feature / Page | Fee Earner | Associate Partner | Partner | Billing | Admin |
|---|---|---|---|---|---|
| **Index (Dashboard)** | View own unbilled time only | View own + delegates | View own + delegates | View all · no click-through | No access |
| **Record Time** | Own | Own | Own | No access | No access |
| **View Time** | Own | Own + delegates | Own + delegates | Read-only | Read-only |
| **Edit Time** | Own | Own | Own | No access | No access |
| **Delete Time** | Own | Own | Own | No access | No access |
| **Create Invoice** | No access | Yes · for self + delegates | Yes · for self + delegates | No access | No access |
| **Post/Delete Invoice** | No access | No access | No access | Yes | No access |
| **View Invoice** | No access | Yes | Yes | Yes | No access |
| **Mark Invoice as Paid** | No access | No access | No access | No access | No access |

> **Notes**  
> * “Delegates” means users assigned to the partner/associate partner for oversight.  
> * Billing can **finalise** invoices (post/delete) but not create or edit time.  
> * Admin is **read-only** for time to support audit; no invoice powers (per current scope).
