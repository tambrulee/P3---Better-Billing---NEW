I implemented full CRUD operations across the application:

- **Create:** New Clients, Matters, Time Entries, WIP, and Invoices can be added via Django forms.  
- **Read:** Lists and detailed record pages show data retrieved dynamically using Django ORM queries and `select_related` for performance.  
- **Update:** Time Entries and draft Invoices can be edited by fee earners before posting.  
- **Delete:** Only authorised users can delete draft records, ensuring data integrity.

Each CRUD action triggers immediate reflection in the UI—recent entries update on save, and success messages confirm completion.  

Data validation prevents mismatched records (e.g., a Matter cannot be assigned to a Client that doesn’t own it), demonstrating defensive coding and robust data handling.

**Evidence:**
- Working CRUD forms and views  
- Data validation via model `clean()` methods  
- Real-time UI updates on CRUD actions  
- Toast and message feedback after user actions  