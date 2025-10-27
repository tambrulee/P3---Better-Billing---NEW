# 🧾 Better Billing — Overview

Better Billing is a full-stack time recording and invoicing application built for law firms, where **fee earners** record their time, **partners** review and approve work, and **billing administrators** post final invoices.  

The project was developed using **Django**, **PostgreSQL**, and **Bootstrap**, and securely deployed to **Heroku**.  
Environment variables are managed through `.env` files to protect **secret keys** and **database credentials**.

---

## 🎯 Project Goal

The aim of Better Billing is to make **time recording** and **client billing** intuitive, transparent, and efficient for law firm teams.  

It accurately models real-world legal processes through linked data entities:  
**Clients → Matters → Time Entries → WIP (Work in Progress) → Invoices.**  

Each entity supports full **CRUD** functionality with role-based permissions, ensuring users can only view or modify what’s appropriate to their role.

---

## ⚙️ How Better Billing Works

1. **Fee Earners** log their time via the “Record Time” interface, adding a short narrative and linking it to a **Client**, **Matter**, and **Activity Code**.  
2. **Partners** (administrators) review submitted entries and generate draft invoices.  
3. **Billing users** can then **post** and **mark invoices as paid**, ensuring each stage of the billing cycle is traceable.  

All user actions feed data into the PostgreSQL database:
- Time entries flow into **WIP** tables.  
- WIP items are aggregated into **Invoices**.  
- Each invoice links to a **Ledger** record that tracks posting and payment status.  

This ensures a clear, auditable trail from recorded time through to payment, in line with legal billing practices.

---

## 🧩 Dependencies & Technical Stack

### **Frontend**
- **Bootstrap 5** used for layout, responsiveness, and consistent styling.  
- Accessibility compliance achieved with semantic HTML, ARIA labels, and strong colour contrast.
[Lighthouse testing - Home](/readme_docs/lighthouse/index_lh.png)  
[Lighthouse testing - Post Invoice](/readme_docs/lighthouse/post_in_lh.png)  
[Lighthouse testing - Create Invoice](/readme_docs/lighthouse/create_in_lh.png)  
[Lighthouse testing - Record Time](/readme_docs/lighthouse/record_lh.png)
[Lighthouse testing - View Invoice](/readme_docs/lighthouse/view_inv_lh.png)  
- UX designed for clarity and minimal friction — entering time or generating invoices takes only a few steps.

### **Backend**
- Built in **Django**, following the Model-View-Template (MVT) pattern.  
- Models clearly define relationships between clients, matters, and financial records.  
- Dynamic templates use Django’s conditional logic to provide instant visual feedback on user actions.  
- Persistent data stored in **PostgreSQL**, with validation and error handling performed at both form and model level.  

The system uses Django’s **messages framework** for real-time feedback (e.g., _“Time entry saved successfully”_), creating a smooth and transparent experience.

### **Code Quality**
- Fully **Flake 8 PEP8-compliant** Python.  
- Consistent variable naming, indentation, and inline documentation.  
- **HTML5Validator** and **Jigsaw** validators used for HTML and CSS validation.
- **ES Lint** used for JS validation

---

## 🧰 Setup & Installation

📄 [Click here to view detailed installation and deployment steps for GitHub, Django, and Heroku.](/readme_docs/deploy_install.md)

---

## ⚡ Notes on Scalability

This version of Better Billing is designed for **small law firm environments**.  
It can be easily scaled to connect with external **APIs** or expanded to include additional modules — for example:
- Matter and rate management  
- Role-based time approval  
- Integration with accounting or case management systems  

Currently, the app assumes access to internal databases for **Matters**, **Personnel**, and **Rates**, which can be extended in future releases.

---

## 🧱 Design, Development & Implementation

- #### [User Stories](/readme_docs/user_story.md)  
- #### [UX Design](/readme_docs/ux.md)  
- #### [Testing & QA](/readme_docs/testing.md)

---

## 🗄️ Data Model Management
- #### [Database Models & Schema](/readme_docs/db_schema.md)

---

## 🧯 Issues & Fixes
- #### [Bugs & Fixes](/readme_docs/bugs.md)

---

## 📚 Sources
View all research materials, tutorials, and supporting documentation  
👉 [here](/readme_docs/sources.md)
