# Milestone 1: Resale Properties Database Design & Physical Implementation
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (Fall 2026)
**Author:** Mennatallah Essam Zaher  
**Instructor:** Prof. Hossam Sharara (The American University in Cairo)

---

## 1. Official Deliverable Mapping

| Deliverable | Description | Corresponding Files in `milestone1/` | Status |
|---|---|---|---|
| **Deliverable 1** | **Entity-Relationship Diagram (ERD)** | 1. [`erd.mmd`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/erd.mmd) (Mermaid ERD)<br>2. [`erd.dbml`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/erd.dbml) (DBML for dbdiagram.io)<br>3. [`erd_description.md`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/erd_description.md) (Textual ERD for Draw.io / hand-drawing) | Completed & Verified |
| **Deliverable 2** | **Relational Model** | [`relational_model.md`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/relational_model.md) (ER-to-Relational mapping, Schema, BCNF Normalization proofs, Referential Integrity matrix, Constraint catalog) | Completed & Verified |
| **Deliverable 3** | **SQL Creation Transcript** | 1. [`schema.sql`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/schema.sql) (Complete re-runnable MySQL DDL)<br>2. [`schema_transcript.txt`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/schema_transcript.txt) (Execution transcript with SHOW TABLES, SHOW CREATE TABLE, DESCRIBE) | Executed on MySQL 8.0 & Verified |
| **Verification & Proofs** | **Transactional Verification** | 1. [`verification.sql`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/verification.sql) (Sample data, constraint rejections, Milestone III Q1-Q10 proofs, clean rollback)<br>2. [`verification_transcript.txt`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/verification_transcript.txt) (Execution output) | Executed on MySQL 8.0 & Verified |

---

## 2. Design Assumptions List

| # | Assumption Topic | Architectural Decision & Rationale |
|---|---|---|
| **A1** | **User Age Storage** | `age` is **not** stored as a redundant column. Storing static age violates 3NF and causes temporal drift. It is dynamically derived via the `v_user_profile` view using `TIMESTAMPDIFF(YEAR, birthdate, CURDATE())`. |
| **A2** | **Price per sqm** | `price_per_sqm` is a derived attribute computed dynamically via `v_property_metrics` (`price / area_sqm`). This prevents data divergence upon updates. |
| **A3** | **Multiple Reviews** | Users are allowed to submit multiple reviews over time for a development project (e.g. pre-construction and post-delivery feedback), tracked by surrogate `review_id`. |
| **A4** | **No Authentication Passwords** | Per project instructions, authentication credentials (passwords/hashes) are omitted as the prompt only specifies demographic and focus attributes. |
| **A5** | **Standalone Properties** | Properties can exist outside of master-planned development projects (`property.development_id` is nullable). |
| **A6** | **Optional Developer** | Some developments may be unbranded or municipal (`development.developer_id` is nullable). |
| **A7** | **Self-Referencing Location** | Geographic hierarchy is unified into a single self-referencing `location` table with `parent_location_id` (`governorate` → `city` → `area`), allowing variable administrative depths. |
| **A8** | **Lookup Tables** | Dedicated lookup tables (`property_type`, `payment_method`, `amenity`) with surrogate keys and `UNIQUE` constraints are used instead of hardcoded `ENUM`s, facilitating crawler discovery in Milestone II without requiring DDL alterations. |
| **A9** | **Reserved Keyword Avoidance** | The user table is named `app_user` rather than `user` to prevent conflicts with SQL standard reserved keywords and MySQL's built-in `USER()` function. |
| **A10** | **Crawler Natural Key** | Added `source_listing_id VARCHAR(100) UNIQUE NOT NULL` and `source_url` on `property` to guarantee crawler idempotency for Milestone II (`INSERT ... ON DUPLICATE KEY UPDATE`). |

---

## 3. How to Reproduce & Execute

### Prerequisites
- MySQL Server 8.0+ running on port 3306 (or Docker container `mysql:8.0`).
- Credentials configured (e.g. user `root`, password `password`).

### Reproduction Commands
```bash
# 1. Execute schema creation and generate transcript
mysql -u root -p --default-character-set=utf8mb4 --table -vvv < milestone1/schema.sql > milestone1/schema_transcript.txt

# 2. Execute verification script (inserts sample data, tests Q1-Q10, rolls back)
mysql -u root -p --default-character-set=utf8mb4 --table -vvv < milestone1/verification.sql > milestone1/verification_transcript.txt
```

---

## 4. Self-Review Quality Checklist

- [x] **YES** — Every item in Section 1 (area, location, development, type, bedrooms, bathrooms, amenities, description, payment method, down payment, gain over current value, development name/location/developer, user email/username/gender/age/birthdate/areas of focus, review rating 1-10 + text) maps to a column or table.
- [x] **YES** — No multi-valued attribute stored in a single column (`user_focus_area` and `property_amenity` resolve all M:N relationships).
- [x] **YES** — Every table is normalized to BCNF / 3NF.
- [x] **YES** — Every M:N has an associative table with a composite PK.
- [x] **YES** — Every FK has explicit `ON DELETE` / `ON UPDATE` actions.
- [x] **YES** — Rating is constrained to 1..10 at the database level (`ck_review_rating`).
- [x] **YES** — `property.development_id` is nullable.
- [x] **YES** — A crawler-friendly unique key exists on `property` (`source_listing_id`).
- [x] **YES** — Price per sqm and age are derived via views (`v_property_metrics`, `v_user_profile`), not stored redundantly.
- [x] **YES** — All 10 Milestone III functionalities are demonstrably answerable (Q1..Q10 verified).
- [x] **YES** — `schema.sql` runs from scratch with zero errors and zero warnings.
- [x] **YES** — The final database is confirmed empty after verification (`0 rows` across all tables).
- [x] **YES** — The ERD (3 forms), relational model, and SQL transcript all agree with one another.
- [x] **YES** — No superfluous tables or columns exist.

