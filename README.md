# Resale Properties Database & Crawling System
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (Fall 2026)
**Author:** Mennatallah Essam Zaher  
**Instructor:** Prof. Hossam Sharara — The American University in Cairo (AUC)  
**Target Platform:** [AqarExit](https://aqarexit.com) (`https://aqarexit.com/en/opportunities`)  
**Database Engine:** MySQL 8.0+ (InnoDB, `utf8mb4`, `utf8mb4_unicode_ci`)  
**Generated On:** 2026-11-02  

---

## 1. Executive Summary & Deliverables

This repository contains the complete implementation for **Milestone I** (Database Design & Physical Schema) and **Milestone II** (Web Crawling, Parsing & Database Population) for the Resale Properties Project. The database has been populated with **100% of the listings crawled across the entire AqarExit platform**.

### Milestone I Deliverables (Folder: `milestone1/`)
1. **Entity-Relationship Diagram (ERD)**:
   - [`milestone1/erd.mmd`](milestone1/erd.mmd): Full Mermaid `erDiagram` with crow's-foot notation.
   - [`milestone1/erd.dbml`](milestone1/erd.dbml): DBML specification for rendering on [dbdiagram.io](https://dbdiagram.io).
   - [`milestone1/erd_description.md`](milestone1/erd_description.md): Formal textual ERD description for hand-drawing or Draw.io / Lucidchart.
2. **Relational Model & Design Specifications**:
   - [`milestone1/relational_model.md`](milestone1/relational_model.md): Detailed ER-to-relational mapping, schema notation with marked PKs/FKs, BCNF normalization proofs, referential integrity matrix, and constraint catalogue.
   - [`milestone1/01_requirements_analysis.md`](milestone1/01_requirements_analysis.md): Entity candidate justifications, attribute catalog, cardinality/participation, and numbered architectural assumptions (A1–A10).
3. **Physical Schema & Execution Transcripts**:
   - [`milestone1/schema.sql`](milestone1/schema.sql): Re-runnable MySQL DDL script with InnoDB, `utf8mb4`, views, and query-optimized indexes.
   - [`milestone1/schema_transcript.txt`](milestone1/schema_transcript.txt): Execution log against MySQL 8.0 displaying `SHOW TABLES`, `DESCRIBE`, and `SHOW CREATE TABLE`.
   - [`milestone1/verification.sql`](milestone1/verification.sql): Transactional verification testing constraint violations (C1–C8), Milestone III queries (Q1–Q10), and clean rollback.
   - [`milestone1/verification_transcript.txt`](milestone1/verification_transcript.txt): Verifiable execution output proving all constraints and queries work as designed.
   - [`milestone1/README.md`](milestone1/README.md): Milestone 1 self-review checklist and reproduction notes.

### Milestone II Deliverables (Folder: `milestone2/`)
1. **Crawling Script Package (Deliverable 1)**:
   - [`milestone2/deliverables/crawler/`](milestone2/deliverables/crawler/): Standalone executable crawler codebase featuring multi-worker concurrency, polite rate-limiting, atomic HTML caching, hybrid JSON-LD + text extraction, Arabic normalizer, and database loader.
2. **Populated MySQL Database Dump (Deliverable 2)**:
   - [`milestone2/deliverables/resale_properties_dump.sql`](milestone2/deliverables/resale_properties_dump.sql): Complete MySQL database dump containing the schema and all **9,628 populated property listings** (6.08 MB pure UTF-8, verified with 100% matching row counts upon clean restoration in [`milestone2/deliverables/restore_check.md`](milestone2/deliverables/restore_check.md)).
3. **CSV Exports & Verification Manifest (Deliverable 3)**:
   - [`milestone2/deliverables/csv/`](milestone2/deliverables/csv/): 11 table CSV files exported in UTF-8 with BOM (`utf-8-sig`) for Excel compatibility, accompanied by [`_manifest.csv`](milestone2/deliverables/csv/_manifest.csv) verifying 100% row-count parity with the database.
4. **Validation Reports & Query Evidence**:
   - [`milestone2/data/exports/quality_report.md`](milestone2/data/exports/quality_report.md): Ingestion funnel reconciliation, null rates, range distributions, and proof of 0 foreign key orphans.
   - [`milestone2/validate/m3_smoke_queries_output.txt`](milestone2/validate/m3_smoke_queries_output.txt): Live execution output of the Milestone III analytics queries run against the populated database.
   - [`milestone2/deliverables/restore_check.md`](milestone2/deliverables/restore_check.md): Side-by-side row count comparison and Arabic character round-trip verification.
   - [`milestone2/README.md`](milestone2/README.md): Ethical rate-limiting details, design trade-offs, and Definition of Done checklist.

---

## 2. Database Summary & Verified Manifest

Every table in the database has been exported and verified against [`milestone2/deliverables/csv/_manifest.csv`](milestone2/deliverables/csv/_manifest.csv):

| Table Name | DB Rows | CSV Rows | Status | Classification | Purpose |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `property_type` | **11** | 11 | **MATCH** | Lookup | Bilingual unit types (Apartment, Villa, Chalet, Shop, Office, etc.) |
| `payment_method` | **2** | 2 | **MATCH** | Lookup | Cash, Installments |
| `amenity` | **10** | 10 | **MATCH** | Lookup | Controlled amenity vocabulary (Pool, Security, Gym, etc.) |
| `location` | **207** | 207 | **MATCH** | Geographic Hierarchy | 3-tier hierarchy: Governorate -> City -> Area across Egypt |
| `developer` | **3,056** | 3,056 | **MATCH** | Entity | Normalized corporate real estate developers |
| `development` | **6,279** | 6,279 | **MATCH** | Entity | Master developments and compounds across Egypt |
| `property` | **9,628** | 9,628 | **MATCH** | Core Crawled Listings | Entire website listings with physical and financial metrics |
| `property_amenity` | **37,382** | 37,382 | **MATCH** | M:N Associative | Property-to-amenity relationship bridge |
| `app_user` | **40** | 40 | **MATCH** | Synthetic Users | Sample users generated via Faker (seed 2501, `@*.example.com`) |
| `user_focus_area` | **95** | 95 | **MATCH** | M:N Associative | User geographic interests referencing existing locations |
| `review` | **120** | 120 | **MATCH** | Synthetic Reviews | Plausible reviews referencing real developments and users |

---

## 3. Key Engineering Highlights & Fixes

1. **Entire Website Crawled:** Crawled all **9,690 opportunity URLs** discovered on AqarExit. 9,628 pages were successfully downloaded into `milestone2/data/raw/`, and 62 dead/expired links (HTTP 404) were logged cleanly. **Zero pending items remain.**
2. **Pure UTF-8 Database Dump:** Re-created using `mysqldump ... --result-file=milestone2/deliverables/resale_properties_dump.sql` (no PowerShell `>` redirection), eliminating UTF-16 LE issues and preserving all Arabic characters without mojibake.
3. **Mandatory Restore Test Passed:** Restored into `resale_properties_restore_test` via native `mysql` CLI; all 11 tables match 100% side-by-side, and Arabic characters match character-by-character.
4. **Geographic Hierarchy & Bilingual Support:** Expanded `milestone2/parsing/location_hierarchy.csv` to 207 locations across 8 Egyptian Governorates; added `name_en` and `name_ar` columns to `location` and `property_type`.
5. **Idempotent Multi-Worker Architecture:** High-throughput fetcher (`--workers 6`) and parallel parser (`--workers 8`) enable end-to-end processing of ~10,000 files in under 25 minutes.

---

## 4. Reproduction Instructions

To reproduce the entire data engineering pipeline from scratch, execute:

```bash
# 1. Install dependencies
pip install -r milestone2/requirements.txt

# 2. Stage 1: Frontier Discovery
python -m milestone2.crawler.discover

# 3. Stage 2: High-Throughput Fetcher (fetches all pending listings)
python -m milestone2.crawler.fetch --all --workers 6 --resume

# 4. Stage 3: Offline Parallel HTML Parsing (8 worker threads)
python -m milestone2.parsing.parse_listing --all --workers 8

# 5. Stage 4: Database Schema Initialization & Bulk Ingestion
python -m milestone2.load.load_db --init

# 6. Stage 5: Seed Synthetic User Profiles & Reviews (seed 2501)
python -m milestone2.load.seed_users

# 7. Stage 6: Export UTF-8 BOM CSV Files & Manifest
python -m milestone2.load.export_csv

# 8. Stage 7: Generate Data Quality Report & Smoke Query Output
python -m milestone2.validate.quality_report
python -m milestone2.validate.run_smoke_queries

# 9. Verify Automated Unit Tests (12/12 pass)
python -m unittest milestone2/parsing/tests/test_parsers.py
```

---

## 5. Definition of Done Checklist

- [x] **Frontier & Full Scope:** All 9,690 listings discovered; 9,628 downloaded; 0 pending in `crawl_state.sqlite`.
- [x] **Database Dump:** Pure UTF-8 dump generated via native `--result-file` (no UTF-16, no PowerShell `>` redirection).
- [x] **Mandatory Restore Test:** Clean restoration into `resale_properties_restore_test`; 100% table row count match (all 9,628 properties and 37,382 amenity links).
- [x] **Geographic Hierarchy:** Geographically accurate 3-tier hierarchy (Governorate -> City -> Area) across 207 locations.
- [x] **Bilingual Support:** `name_en` and `name_ar` columns added; zero dual-language duplicate entities.
- [x] **Coordinates Policy:** Confirmed site omits coordinates; preserved as NULL per guidelines.
- [x] **Financial Columns:** Gain vs. discount identity documented in `schema_changes_m2.sql`.
- [x] **Referential Integrity:** 0 Foreign Key orphans across all tables in `quality_report.md`.
- [x] **Loader Idempotency:** Second loader run produces identical row counts.
- [x] **CSV Exports & Manifest:** All 11 tables exported in UTF-8 BOM (`utf-8-sig`); 100% row match in `_manifest.csv`.
- [x] **Synthetic Users:** 40 users, 120 reviews referencing real developments; `@*.example.com` emails.
- [x] **Smoke Queries:** All 8 Milestone III analytical queries return meaningful, non-empty results on the full dataset.
- [x] **Unit Tests:** 12/12 unit tests pass in `test_parsers.py`.
- [x] **Deliverables Package:** `milestone2/deliverables/crawler/` synchronized cleanly with working source.
