# Data Population and Generation Report

## 1. Data Source and Type
All data utilized to populate the database tables was synthetically generated. Rather than using external open-source clinical datasets (such as MIMIC-III) which would introduce unnecessary structural mismatches and unrelated data columns, we engineered a native dataset from the ground up. This approach guarantees full compatibility with our custom hospital management schema and satisfies all clinical entity requirements.

## 2. Generation Methodology & Tools
The mock data was generated using a custom automated Python script utilizing core structural programming elements (`random` and `datetime` libraries). 

### Artificial Intelligence (AI) Prompt Utilization
AI was utilized as a guided teaching tool to draft the initial procedural loop blocks for the generation framework. The specific engineering prompt used was:
> *"Generate a modular Python script template using standard libraries to create relational data insertion rows for a hospital database containing independent entities (Physicians, Patients, Nurses, ICD-9 Lookup Dictionary) and downstream dependent tables (Admissions, Triage Assessments, Diagnoses, ICU Stays, Clinical Notes) while maintaining perfect structural constraints."*

## 3. Data Cleaning, Transformation, and Bug Fixes
Because the data was synthesized to natively target our specific database structures, extensive pre-import cleanup was avoided. However, deep structural transformations were required to handle real database constraints discovered during individual insertion tests:

* **Entity Field Mismatches (Physicians):** The initial script generation attempted to pass a combined `'name'` string variable into a single column. Upon manual review of our database schema, it was corrected to break down names into distinct `first_name` and `last_name` fields to match the table properties perfectly.
* **Primary Key Constraint Fixes (`admission_pkey`):** Manual testing revealed immediate transaction failures (`duplicate key value violates unique constraint "admission_pkey"`) caused by pre-existing data rows in the database. Instead of copying bulk automated workarounds, we systematically investigated the query stack and manually adapted the record values (e.g., shifting conflicting IDs) to preserve index uniqueness.
* **Referential Integrity Validation:** Every downstream record (such as `triage_assessment` or `clinical_note`) was strictly transformed to pass a foreign key matching a valid, existing `admission_id` or `physician_id`.

## 4. Import Methodology
The transformed data was compiled cleanly into an independent SQL population script (`populate_all_hospital.sql`). 
* **Database Management System:** PostgreSQL
* **Execution Interface:** pgAdmin 4 (Query Tool Browser)
* **Transaction Safety:** The entire dataset was enclosed inside a single atomic transaction block (`BEGIN;` and `COMMIT;`). This ensured that if any individual row failed a check, the database engine safely rolled back the stack, avoiding partial or corrupted tables.
