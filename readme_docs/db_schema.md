# Database Schema Overview

This document outlines the relationships and key structure of the Better Billing database schema, based on the Django models.

View the full database scheme [here](/readme_docs/DB%20Schema.pdf)

---

## Core Entities & Relationships

### Client
- **Fields:** `client_number` (unique), name, address fields, contact info.
- **Relationships:**
  - **Has many:** `Matter`, `TimeEntry`, `WIP`, `Invoice`, `Ledger` (via `ledger_entries`).

### Role
- **Fields:** `role` (unique), `rate`.
- **Relationships:**
  - **Has many:** `Personnel`.

### Personnel
- **Fields:** `initials` (unique), `name`, `role`, `user`, `line_manager`.
- **Relationships:**
  - `role` → Role (**many-to-one**, PROTECT)
  - `user` → Auth User (**one-to-one**, nullable, SET_NULL)
  - `line_manager` → Personnel (**self many-to-one**, nullable, SET_NULL)
  - **Has many:** `Matter` (as `lead_fee_earner`), `TimeEntry`, `WIP`

### Matter
- **Fields:** `matter_number` (unique), `description`, `opened_at`, `closed_at`.
- **Relationships:**
  - `client` → Client (**many-to-one**, PROTECT)
  - `lead_fee_earner` → Personnel (**many-to-one**, PROTECT)
  - **Has many:** `TimeEntry`, `WIP`, `Invoice`, `Ledger`.

### ActivityCode
- **Fields:** `activity_code` (unique), `activity_description`.
- **Relationships:**
  - **Has many:** `TimeEntry`, `WIP`.

### TimeEntry
- **Fields:** client, matter, fee_earner, activity_code, hours_worked, narrative.
- **Relationships:**
  - `client` → Client (**many-to-one**, PROTECT)
  - `matter` → Matter (**many-to-one**, PROTECT)
  - `fee_earner` → Personnel (**many-to-one**, PROTECT)
  - `activity_code` → ActivityCode (**many-to-one**, PROTECT)
  - **Has exactly one:** `WIP` (via WIP’s one-to-one).

### WIP (Work In Progress)
- **Fields:** client, matter, time_entry, fee_earner, activity_code, hours_worked, status.
- **Relationships:**
  - `time_entry` → TimeEntry (**one-to-one**, CASCADE)
  - `client`, `matter`, `fee_earner`, `activity_code` (**many-to-one**, PROTECT)
  - **Has many:** `InvoiceLine` (via `invoiced_lines`).

### Invoice
- **Fields:** `number` (unique), `invoice_date`, `tax_rate`, `notes`.
- **Relationships:**
  - `client` → Client (**many-to-one**, PROTECT)
  - `matter` → Matter (**many-to-one**, PROTECT)
  - **Has many:** `InvoiceLine` (CASCADE on delete)
  - **Has one:** `Ledger` (one-to-one, CASCADE).

### InvoiceLine
- **Fields:** invoice, wip, desc, hours, rate, amount.
- **Relationships:**
  - `invoice` → Invoice (**many-to-one**, CASCADE)
  - `wip` → WIP (**many-to-one**, PROTECT).

### Ledger
- **Fields:** invoice, client, matter, subtotal, tax, total, status.
- **Relationships:**
  - `invoice` → Invoice (**one-to-one**, CASCADE)
  - `client` → Client (**many-to-one**, PROTECT)
  - `matter` → Matter (**many-to-one**, nullable, PROTECT).

---

## Delete and Integrity Rules

- **PROTECT** used for key financial records (prevents deletion of referenced clients, matters, etc.).  
- **CASCADE** used for dependent, snapshot-based data (e.g., deleting an invoice deletes its lines).  
- Validation ensures consistent `client` / `matter` relationships across TimeEntry and WIP.  
- `Personnel.clean()` enforces manager role rules.

