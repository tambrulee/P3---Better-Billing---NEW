The data model was carefully planned to mirror real-world billing relationships:

- **Client** → one-to-many → **Matters**  
- **Matter** → one-to-many → **Time Entries** and **WIP**  
- **WIP** → one-to-many → **InvoiceLines**  
- **Invoice** aggregates **WIP** for billing  

Each model includes appropriate foreign keys, validation, and string representations for clarity in the admin panel and throughout the app.  

The database is managed in PostgreSQL (configured in `DATABASE_URL`), with environment-specific settings stored centrally in `settings.py` and environment variables loaded via **`python-dotenv`**.  

I also documented the schema in the README with entity relationships and field descriptions, making the structure easy to understand and maintain.

**Evidence:**
- Normalised relational schema (ERD diagram)  
- Centralised database configuration  
- PostgreSQL in production, SQLite in development  
- `.env` for environment variables  
- `requirements.txt` and `Procfile` for dependencies and deployment  

[Screenshot: ERD Diagram of Models]  
[Link: README Schema Section]