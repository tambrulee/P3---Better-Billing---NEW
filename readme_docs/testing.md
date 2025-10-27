## **Testing**

### **Testing Overview**

Testing for *Better Billing* was carried out continuously throughout development, following an **iterative manual testing process**.  
Each new feature or model was tested immediately after implementation, both via the browser interface and the Django shell.  
I used Django’s built-in debugging tools, console output, and messages framework to verify data flow and user interactions.  

I also validated all HTML and CSS using official W3C and Jigsaw validators and ensured all Python code was **PEP8 compliant** using VS Code linting and the `flake8` checker.  

Below is a summary of the main test procedures and outcomes.

---

### **Manual Testing Table**

| **Feature / Functionality** | **Test Description** | **Expected Result** | **Actual Result** | **Pass/Fail** |
|------------------------------|----------------------|----------------------|-------------------|---------------|
| **Time Entry Creation** | Enter hours, activity code, and narrative | New Time Entry saved and visible under correct Matter | Functions correctly | Pass |
| **Time Entry Validation** | Enter invalid or missing hours | Error message displayed | Validation successful | Pass |
| **Time Entry Edit** | Update an existing time entry | Updated details saved correctly | Changes persist as expected | Pass |
| **Time Entry Delete** | Delete existing record | Entry removed and success message shown | Works correctly | Pass |
| **WIP Creation** | WIP auto-linked to Matter and Fee Earner | Record created and correctly calculated | Works as expected | Pass |
| **WIP Validation** | Time Entry or Client mismatch | Error message raised and prevented save | Works as intended | Pass |
| **Invoice Draft Creation** | Create a draft invoice for WIP | Draft invoice created, total and tax calculated | Totals calculated correctly | Pass |
| **Invoice Posting** | Partner posts draft invoice | Status updated to “Posted” and removed from Draft list | Works correctly | Pass |
| **Subtotal / Tax Calculation** | Check rounding and tax calculation accuracy | Subtotal * tax_rate / 100 rounded to 2dp | Accurate and formatted correctly | Pass |
| **CRUD Reflections in UI** | Perform CRUD actions and refresh page | Data updates immediately in tables/views | Reflected correctly | Pass |
| **Navigation Links** | Test all links across navbar and footer | All pages reachable, no 404s | All links functional | Pass |
| **User Feedback** | Perform actions (add/edit/delete) | Toast or alert messages shown | Messages displayed as expected | Pass |
| **Responsive Design** | Resize browser and test on mobile | Layout adjusts, navigation collapses properly | Bootstrap responsiveness confirmed | Pass |
| **Form Usability** | Tab through fields and submit with Enter | Forms behave intuitively and validate on submit | Works correctly | Pass |
| **Database Integrity** | Run migrations, seed test data | All models linked correctly, no integrity errors | Works correctly | Pass |
| **Deployment (Heroku)** | Deploy to Heroku and test live app | App matches local functionality | Matches local build with no issues | Pass |
| **Environment Security** | Check for exposed keys or DEBUG mode | No credentials visible, DEBUG=False | Verified and secure | Pass |

---

### **Testing Reflection**

Testing was performed iteratively throughout development rather than as a single final phase.  
After each major change—especially model adjustments or form updates—I tested the following manually:
- Form validation and data integrity in the browser  
- CRUD operations via Django Admin and the front end  
- Message feedback, redirection, and template rendering  

When errors occurred, they were documented and resolved immediately.  
Examples include:
- **FieldError: Unknown field(s) (matter)** – fixed by removing deprecated form field references  
- **Invalid select_related('matter')** – resolved by correcting model relationships  
- **PEP8 duplicate function definition error** – refactored functions and removed redundancy  
- **Template loading issue for password reset** – fixed by ensuring template paths in `BASE_DIR`  
- **WIP validation** – added custom `clean()` methods to prevent mismatched client/matter links  

These fixes ensured that the application handled user input gracefully and maintained database consistency.

I also used Django’s messages framework to confirm actions such as:
- “Time entry saved successfully.”  
- “Please correct the errors below.”  
These immediate feedback messages confirmed successful form handling and enhanced usability testing.

Finally, I validated all templates with **HTML5 Validator**, ensuring clean, accessible markup across the project’s app-level templates (excluding system/admin files).

---

### **Validation Results**

| **Validation Type** | **Tool Used** | **Result** |
|----------------------|---------------|------------|
| HTML | HTML 5 Validator | No major errors |
| CSS | Jigsaw CSS Validator | [No issues](/readme_docs/testing/css_check.png) |
| Python | PEP8 / Flake8 | [All code compliant](/readme_docs/testing/ruff_check.png) - [See all errors and fixes here](/readme_docs/testing/pep8_test.md) |
| Javascript | ESLint | [No issues](/readme_docs/testing/eslint_check.png) |
| Database | Django ORM Migrations | [Passed with no conflicts](/readme_docs/testing/django_check.png) |
| Security | `.env` + `.gitignore` + `DEBUG=False` | Passed |

---

### **Conclusion**

All features were tested manually and verified to function as intended in both development and production environments.  
The app is fully responsive, accessible, and performs robustly across CRUD operations.  

Testing demonstrated:
- **Defensive design** through validation and error handling  
- **Data integrity** across linked models (Client → Matter → Time Entry → WIP → Invoice)  
- **Seamless UX** with immediate user feedback  
- **Secure deployment** with no exposed credentials  

Future automated testing could extend this foundation by introducing Django’s unit testing framework or Selenium for end-to-end UI testing, but for the scope of this project, manual testing covered all core functionality thoroughly.

---

**Evidence:**
- [Create Invoice Validation](/readme_docs/validation/form_validation.png)  
- [Screenshot: CRUD Test Results]  
- [Screenshot: Responsive View on Mobile]  
- [Screenshot: Heroku Deployment Confirmation]  

HTML - Downloaded HTML5 Validator via Java (Java installed via Homebrew)
