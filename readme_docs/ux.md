# User Experience (UX) Design Overview

### Introduction

The *Better Billing* project was developed with a strong emphasis on user experience (UX), ensuring that the interface is intuitive, efficient, and suited to the needs of legal and financial professionals. This section evaluates how UX principles were applied throughout the design and development process, from initial layout considerations to testing and refinement.

**Applying Core UX Principles**

The project followed recognised UX principles such as clarity, consistency, feedback, and accessibility. Each interface component was designed to reduce cognitive load and provide a seamless workflow for users entering, reviewing, and managing billing data. Consistent button placement, typography, and spacing were achieved through the use of the Bootstrap framework, which ensured design harmony across all pages.

## Wireframes & User Experience Design

The **Better Billing** wireframes were designed to visualise the user journey from **login to ledger management**, ensuring a logical, minimal, and intuitive flow.  
The interface balances simplicity for everyday users with enough depth to support detailed billing workflows.

---

### 🧭 1. Entry & Authentication Flow

#### **Landing Page**
The landing page introduces the app’s two main entry points — **Log In** and **Create Account**.  
A hover-based navigation design provides a quick visual preview of each action, supported by a slideshow that adapts depending on which option the user selects.  

Users can immediately choose to:
- **Log In** (for returning users), or  
- **Create Account** (for new users entering firm data).  

This design keeps the initial interaction clean and straightforward while visually reinforcing brand identity through consistent typography and layout.

---

#### **Create Account**
The account creation form is a simple HTML input form connected to the **SQL database**.  
Each field (e.g. name, email, password, firm) is validated server-side, ensuring data integrity and preventing duplicate registrations.  
The wireframe shows the user experience as a linear process, keeping distractions minimal so users can onboard quickly.

#### **Log In**
The login screen contains fields for:
- **Email Address**  
- **Password**  

Python-based validation ensures proper credential verification before granting access.  
If a user enters invalid details, the interface returns real-time feedback, reducing friction and improving trust in the system.

---

### 💼 2. Main Application Workspace

After successful authentication, users are directed to the **Better Billing Dashboard** — the control centre for all billing-related operations.

#### **Dashboard**
The dashboard summarises:
- **Unbilled Time**
- **Paid Invoices**
- **Unpaid Invoices**

It provides at-a-glance financial visibility, allowing users (fee earners, partners, or billing staff) to track what’s pending, posted, or settled.  
Navigation elements are fixed at the top — **Ledger**, **Workspace**, and **Billing** — for quick access between workflows.

---

### 🧾 3. Workspace — Time & Invoice Management

#### **Workspace (Time Entry Area)**
This view allows users to input activities, hours, and rates.  
Each row includes editable fields:
- **Activity Description**
- **Hours (0.1 increments)**
- **Rate**
- **Line Total (calculated as Hours × Rate)**

Users can click **Add** to duplicate entry rows dynamically.  
The **“Create Invoice”** button remains greyed out until unbilled time entries exist — a simple but effective UX safeguard preventing empty invoice generation.

When users press **Submit**, data is pushed into the **WIP (Work In Progress)** table in the database, where it becomes eligible for invoicing.

---

#### **Create Invoice**
In this stage, users can select items from WIP to generate an invoice.  
Once selected, pressing **Submit** pushes this data into the **Ledger** table.  

Each invoice contains:
- Automatically generated **Invoice Number**
- Calculated totals (including line items and VAT)
- Associated **Due Date** and **Status**

This flow ensures each stage — recording time, reviewing, and billing — is fully traceable within the database.

---

### 📒 4. Ledger View — Tracking and Settlement

The **Ledger** view consolidates all posted invoices with key financial details:
| Field | Example | Purpose |
|--------|----------|----------|
| Invoice Number | 903864993 | Unique reference for tracking |
| Total | £456.50 | Invoice amount |
| Due Date | 24/08/2025 | Payment due date |
| Status | Posted / Paid | Indicates settlement progress |
| Paid Date | — | Updated when payment received |

Users can submit updates here (e.g. marking invoices as paid) and view historical financial data across all clients and matters.

---

### 🧾 5. Invoice Viewer

The **Invoice Viewer** provides a detailed look at each invoice.  
It displays:
- Individual **line items** with hours, rates, and totals  
- **Narratives** such as “Conference preparation” or “Drafting tender for bid proposal”  
- A **“View PDF”** button to open a downloadable invoice version  

This section connects the user’s activity-based work with the final billing output, closing the workflow loop.

---

### 🧩 6. Design Principles & UX Goals

- **Clarity over complexity** — Each stage focuses on a single function (record → review → bill → settle).  
- **Logical data flow** — Data progresses linearly from Time Entry → WIP → Invoice → Ledger, reflecting real-world billing operations.  
- **Error prevention** — Greyed-out buttons, validation, and confirmation messages guide users through correct actions.  
- **Consistency** — Uniform layout and spacing across all modules (Dashboard, Workspace, Ledger) make navigation effortless.  
- **Scalability** — The structure supports future modules (e.g. Matter Management, Reporting, Rate Tables).

---

**Use of Bootstrap and Custom CSS**

Bootstrap provided a strong foundation for responsive design, ensuring compatibility across desktop, tablet, and mobile devices. Custom CSS was added to enhance branding and tailor the visual hierarchy—using colour accents, card components, and subtle shadows to distinguish sections and guide user attention. The combination of Bootstrap’s grid system and custom styling promoted both efficiency and aesthetic appeal.

**Information Architecture and Navigation**

The interface was structured around a clear and predictable navigation model. Users can easily move between clients, matters, time entries, and invoices without confusion. Each page follows a logical hierarchy with consistent placement of navigation elements, form inputs, and buttons. Breadcrumbs and headers provide contextual cues that help users understand where they are within the system.

**Feedback and Validation**

User feedback mechanisms were built into key workflows. For example, when invoices are created or time entries are submitted, Bootstrap-styled alert messages confirm the success or failure of an action. Validation errors are displayed inline, using clear language and accessible colours to ensure users can correct mistakes quickly. This reinforces the UX principle of *visibility of system status*.

Examples of user validation messages:

- [Invoice creation successful](/readme_docs/validation/create_inv.png)
- [Time entry successful](/readme_docs/validation/time_entry.png)
- [WIP not available for selection](/readme_docs/validation/create_inv.png)


**Accessibility and Readability**

Accessibility was a key design consideration. The application maintains high colour contrast ratios, legible typography, and large interactive targets to support usability for all users. Semantic HTML tags and ARIA attributes were used where appropriate to improve screen reader compatibility and ensure compliance with accessibility best practices.

**Testing and Iterative Improvement**

The interface was demoed to family members to gather initial feedback on usability, clarity, and flow. Their observations helped identify minor improvements such as spacing adjustments and button alignment refinements. This informal user testing process demonstrated an iterative approach to UX—using real feedback to refine and enhance the design. Further testing with classmates could provide additional perspectives and help validate the user journey in varied contexts.

**Conclusion**
 
By integrating UX principles throughout the development process, *Better Billing* delivers a professional, user-friendly, and accessible platform. Every design decision—from layout and typography to feedback mechanisms—was informed by the goal of simplifying complex billing processes while maintaining a polished, trustworthy aesthetic appropriate for a legal and financial environment.
