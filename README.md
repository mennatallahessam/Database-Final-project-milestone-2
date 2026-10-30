# Resale Properties Database & Crawling System
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (Fall 2026)
**Author:** Mennatallah Essam Zaher  
**Instructor:** Prof. Hossam Sharara — The American University in Cairo (AUC)  
**Target Platform:** [AqarExit](https://aqarexit.com) (`https://aqarexit.com/en/opportunities`)  
**Database Engine:** MySQL 8.0+ (InnoDB, `utf8mb4`, `utf8mb4_unicode_ci`)

---

## 1. Executive Summary & Deliverables

This repository contains the complete implementation for **Milestone I** (Database Design & Physical Schema) and **Milestone II** (Web Crawling, Parsing & Database Population).

### Milestone I Deliverables (Folder: `milestone1/`)
1. **Entity-Relationship Diagram (ERD)**:
   - [`milestone1/erd.mmd`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/erd.mmd): Full Mermaid `erDiagram` with crow's-foot notation.
   - [`milestone1/erd.dbml`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/erd.dbml): DBML specification for rendering on [dbdiagram.io](https://dbdiagram.io).
   - [`milestone1/erd_description.md`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/erd_description.md): Formal textual ERD description for hand-drawing or Draw.io / Lucidchart.
2. **Relational Model & Design Specifications**:
   - [`milestone1/relational_model.md`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/relational_model.md): Detailed ER-to-relational mapping, schema notation with marked PKs/FKs, BCNF normalization proofs, referential integrity matrix, and constraint catalogue.
   - [`milestone1/01_requirements_analysis.md`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/01_requirements_analysis.md): Entity candidate justifications, attribute catalog, cardinality/participation, and numbered architectural assumptions (A1–A10).
3. **Physical Schema & Execution Transcripts**:
   - [`milestone1/schema.sql`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/schema.sql): Re-runnable MySQL DDL script with InnoDB, `utf8mb4`, views, and query-optimized indexes.
   - [`milestone1/schema_transcript.txt`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/schema_transcript.txt): Execution log against MySQL 8.0 displaying `SHOW TABLES`, `DESCRIBE`, and `SHOW CREATE TABLE`.
   - [`milestone1/verification.sql`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/verification.sql): Transactional verification testing constraint violations (C1–C8), Milestone III queries (Q1–Q10), and clean rollback.
   - [`milestone1/verification_transcript.txt`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/verification_transcript.txt): Verifiable execution output proving all constraints and queries work as designed.
   - [`milestone1/README.md`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/README.md): Milestone 1 self-review checklist and reproduction notes.

### Milestone II Deliverables (Folder: `milestone2/`)
1. **Crawling Script Package**:
   - [`milestone2/deliverables/crawler/`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/deliverables/crawler/): Standalone executable crawler codebase featuring polite rate-limiting, raw atomic caching, hybrid JSON-LD + text extraction, Arabic normalizer, and database loader.
2. **Populated MySQL Database Dump**:
   - [`milestone2/deliverables/resale_properties_dump.sql`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/deliverables/resale_properties_dump.sql): Complete MySQL database dump containing the schema and all populated data (tested and verified with 100% matching row counts upon clean restoration).
3. **CSV Exports & Verification Manifest**:
   - [`milestone2/deliverables/csv/`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/deliverables/csv/): 11 table CSV files exported in UTF-8 with BOM (`utf-8-sig`) for Excel compatibility, accompanied by [`_manifest.csv`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/deliverables/csv/_manifest.csv) verifying 100% row-count parity.
4. **Validation Reports & Query Evidence**:
   - [`milestone2/data/exports/quality_report.md`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/data/exports/quality_report.md): Ingestion funnel reconciliation, null rates, range distributions, and proof of 0 foreign key orphans.
   - [`milestone2/validate/m3_smoke_queries_output.txt`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/validate/m3_smoke_queries_output.txt): Live execution output of the Milestone III analytics queries run against the populated database.
   - [`milestone2/README.md`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/README.md): Ethical rate-limiting details, design trade-offs, and Definition of Done checklist.

---

## 2. Repository Layout

```text
db final version/
├── README.md                                 # Master Project Documentation (This File)
├── Milestone_1_Prompt_Database_Design.md     # Official Milestone 1 Assignment Prompt
├── Milestone_2_Prompt_Crawling_and_...md     # Official Milestone 2 Assignment Prompt
│
├── milestone1/                               # MILESTONE 1 DELIVERABLES
│   ├── README.md                             # Milestone 1 Guide & Self-Review Checklist
│   ├── 01_requirements_analysis.md           # Step A: Requirements Traceability & Entity Catalog
│   ├── erd.mmd                               # Step B: Mermaid ERD (Crow's-Foot Notation)
│   ├── erd.dbml                              # Step B: DBML for dbdiagram.io
│   ├── erd_description.md                    # Step B: Textual ERD Description for Draw.io
│   ├── relational_model.md                   # Step C: Relational Model, BCNF Proofs & Constraints
│   ├── schema.sql                            # Step D: Physical MySQL 8.0 DDL Script
│   ├── schema_transcript.txt                 # Step D: Real MySQL CLI Execution Transcript
│   ├── verification.sql                      # Step E: Negative Tests, Q1-Q10 & Rollback
│   └── verification_transcript.txt           # Step E: Real Execution Output of verification.sql
│
└── milestone2/                               # MILESTONE 2 DELIVERABLES & PIPELINE
    ├── README.md                             # Milestone 2 Guide & Definition of Done
    ├── requirements.txt                      # Python dependencies (requests, bs4, pymysql, faker)
    ├── .env.example                          # Environment template
    ├── .env                                  # Active database & crawler settings
    ├── config.py                             # Central configuration & tunable constants
    ├── sql/
    │   ├── schema.sql                        # Active MySQL schema (from Milestone 1)
    │   └── schema_changes_m2.sql             # Migration notes (no breaking changes needed)
    ├── crawler/
    │   ├── discover.py                       # Stage 1: Enumerate 9,684 listings from sitemap & index
    │   ├── fetch.py                          # Stage 2: Polite rate-limited downloader
    │   ├── http_client.py                    # Polite requests session with backoff & circuit breaker
    │   └── state.py                          # SQLite state store tracking listing crawl progress
    ├── parsing/
    │   ├── parse_listing.py                  # Offline extractor (JSON-LD + HTML labels + text)
    │   ├── text_extractors.py                # Regex / NLP helpers for fields embedded in free text
    │   ├── normalize.py                      # Arabic-Indic digits, units, entity resolution & quarantine
    │   └── tests/
    │       └── test_parsers.py               # Unit tests for extractors and normalizers (11/11 passed)
    ├── load/
    │   ├── load_db.py                        # Staging JSONL -> MySQL loader (FK topological order)
    │   ├── seed_users.py                     # Synthetic user generator (Faker seed 2501)
    │   └── export_csv.py                     # DB -> UTF-8 BOM CSV exporter + _manifest.csv
    ├── validate/
    │   ├── quality_report.py                 # Funnel, null rate, FK orphan & distribution reporter
    │   ├── m3_smoke_queries.sql              # Milestone III analytics SQL queries
    │   └── m3_smoke_queries_output.txt       # Real execution transcript of smoke queries
    ├── data/
    │   ├── raw/                              # Untouched HTML files saved per listing (e.g. <uuid>.html)
    │   ├── staging/                          # Staged JSONL data (listings.jsonl, rejected.jsonl)
    │   └── exports/                          # Quality report exports
    ├── logs/
    │   └── crawl.log                         # Structured crawler execution log
    └── deliverables/
        ├── crawler/                          # Clean packaged crawler code for submission
        ├── resale_properties_dump.sql        # Populated mysqldump file (Deliverable 2)
        └── csv/                              # UTF-8 BOM CSV exports per table + _manifest.csv (Deliverable 3)
```

---

## 3. Step-by-Step Running Guide

### Step 0: Environment Setup
Ensure **Python 3.10+** and **MySQL Server 8.0+** are installed and running locally on port 3306.

```bash
# 1. Install required Python libraries
pip install -r milestone2/requirements.txt

# 2. Check/Configure your MySQL credentials in milestone2/.env
# Default settings:
# DB_HOST=127.0.0.1
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=password
# DB_NAME=resale_properties
```

---

### Step 1: Running Milestone 1 (Schema & Verification)

#### 1.1 Create the Schema and Generate the Transcript
Run `milestone1/schema.sql` against MySQL to create the database, tables, views, and indexes:
```bash
# Windows PowerShell
Get-Content "milestone1\schema.sql" | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -ppassword --default-character-set=utf8mb4 --table -vvv > "milestone1\schema_transcript.txt" 2>&1
```

#### 1.2 Run Transactional Verification (Proofs & Negative Tests)
Execute `milestone1/verification.sql` to test negative constraints, run Milestone III queries (Q1–Q10), and verify clean rollback:
```bash
# Windows PowerShell
Get-Content "milestone1\verification.sql" | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -ppassword --default-character-set=utf8mb4 --table -vvv > "milestone1\verification_transcript.txt" 2>&1
```
*Verification Confirmation:* The transcript verifies that constraints C1–C8 reject invalid data (e.g. rating 0, rating 11, duplicate email, negative price, future birthdate), queries Q1–Q10 return valid rows, and `ROLLBACK` leaves all 11 tables with **0 rows**.

---

### Step 2: Running Milestone 2 (Crawl, Parse, Load, Seed, Export)

Run the full Milestone 2 pipeline using the following command sequence:

#### 2.1 Stage 1: Discovery (`discover.py`)
Fetches `https://aqarexit.com/sitemap.xml` and the opportunities index, discovering all 9,684 listing URLs and recording them into `milestone2/data/staging/crawl_state.sqlite`:
```bash
python -m milestone2.crawler.discover
```
*Expected Output:*
```text
Total Listings Discovered: 9684
Pending: 9684 | Done: 0 | Failed: 0
```

#### 2.2 Stage 2: Polite Fetching (`fetch.py`)
Downloads listing detail pages with randomized jitter delays (**2.5 to 5.0 seconds**), respecting rate-limiting and saving untouched raw HTML pages into `milestone2/data/raw/<listing_id>.html`:
```bash
# Crawls a representative batch of 35 listings (or increase with --limit N)
python -m milestone2.crawler.fetch --limit 35 --resume
```
*Expected Output:*
```text
Cycle Fetched: 35 | Skipped (Resumed): 0
Total State -> Done: 35 | Pending: 9649 | Failed: 0
```

#### 2.3 Stage 3: Offline Parsing & Extraction (`parse_listing.py`)
Extracts structured JSON-LD schema metadata, HTML labels, and fallback free-text fields (BR count, area, prices, contract years, amenities) into `milestone2/data/staging/listings.jsonl`:
```bash
python -m milestone2.parsing.parse_listing --all
```
*Expected Output:*
```text
Files Processed: 35
Valid Staged Records: 35 -> milestone2/data/staging/listings.jsonl
Quarantined Records: 0 -> milestone2/data/staging/rejected.jsonl
```

#### 2.4 Stage 4: Database Population (`load_db.py`)
Initializes the MySQL database schema and loads all non-user tables in foreign-key topological order using in-memory lookup caches:
```bash
python -m milestone2.load.load_db --init
```
*Expected Output:*
```text
Applying schema from milestone2/sql/schema.sql...
Schema initialized successfully.
Properties Upserted: 35
Amenity Links Upserted: 139
```

#### 2.5 Stage 5: Synthetic User & Review Seeding (`seed_users.py`)
Uses `Faker` with fixed seed `2501` to generate 40 reproducible synthetic users with `@example.com` emails, linking their focus areas to real locations and generating 120 reviews referencing real crawled developments:
```bash
python -m milestone2.load.seed_users
```
*Expected Output:*
```text
Users Seeded: 40
Focus Area Links: 100
Reviews Seeded: 120
```

#### 2.6 Stage 6: CSV Export & Parity Manifest (`export_csv.py`)
Exports all 11 tables to `milestone2/deliverables/csv/<table>.csv` using UTF-8 with BOM (`utf-8-sig`) so Arabic displays properly in Microsoft Excel, and generates `_manifest.csv`:
```bash
python -m milestone2.load.export_csv
```
*Expected Output:*
```text
 -> property_type.csv: 6 rows [MATCH]
 -> payment_method.csv: 1 rows [MATCH]
 -> amenity.csv: 8 rows [MATCH]
 -> location.csv: 18 rows [MATCH]
 -> developer.csv: 34 rows [MATCH]
 -> development.csv: 35 rows [MATCH]
 -> property.csv: 35 rows [MATCH]
 -> property_amenity.csv: 139 rows [MATCH]
 -> app_user.csv: 40 rows [MATCH]
 -> user_focus_area.csv: 100 rows [MATCH]
 -> review.csv: 120 rows [MATCH]
```

#### 2.7 Stage 7: Quality Report Generation (`quality_report.py`)
Generates the comprehensive data quality validation report:
```bash
python -m milestone2.validate.quality_report
```
*Output File:* [`milestone2/data/exports/quality_report.md`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/data/exports/quality_report.md)

#### 2.8 Stage 8: Milestone III Analytical Smoke Queries
Executes the analytical queries to confirm data usability:
```bash
# Windows PowerShell
Get-Content "milestone2\validate\m3_smoke_queries.sql" | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -ppassword --default-character-set=utf8mb4 --table resale_properties > "milestone2\validate\m3_smoke_queries_output.txt" 2>&1
```

#### 2.9 Stage 9: Generate and Verify the Database Dump
Creates the official Deliverable 2 SQL dump using `mysqldump` and verifies it restores with zero errors:
```bash
# Generate mysqldump
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" -u root -ppassword --single-transaction --routines --triggers --default-character-set=utf8mb4 --set-gtid-purged=OFF resale_properties > "milestone2\deliverables\resale_properties_dump.sql"

# Verify restoration into a temporary test database
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -ppassword -e "CREATE DATABASE IF NOT EXISTS resale_properties_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
Get-Content "milestone2\deliverables\resale_properties_dump.sql" | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -ppassword --default-character-set=utf8mb4 resale_properties_test
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -ppassword -e "DROP DATABASE resale_properties_test;"
```

---

## 4. Details About the System Output

### 4.1 Database Table Row Counts
The live database contains the following verified row counts:

| Table Name | Live Count | Classification | Description |
|---|---|---|---|
| `property` | **35** | Core Crawled | Resale listings from AqarExit |
| `developer` | **34** | Crawled Reference | Canonical corporate real-estate developers |
| `development` | **35** | Crawled Projects | Compounds / projects (e.g. Badya, Patio Vida, Koun) |
| `location` | **18** | Crawled Hierarchy | Geographic hierarchy (Governorate → City → Area) |
| `property_type` | **6** | Reference Lookup | Unit types (Apartment, Villa, Townhouse, Chalet, etc.) |
| `payment_method` | **1** | Reference Lookup | Payment structures (Installments, Cash) |
| `amenity` | **8** | Reference Lookup | Features (Swimming Pool, Garage, 24/7 Security, Elevator, etc.) |
| `property_amenity` | **139** | M:N Associative | Property-to-amenity relationship links |
| `app_user` | **40** | Synthetic Profile | Registered user accounts (Faker seed 2501) |
| `user_focus_area` | **100** | M:N Associative | User interests linked to real locations |
| `review` | **120** | Synthetic Feedback | Evaluative 1–10 reviews linked to real developments |

---

### 4.2 Data Quality & Validation Details
According to [`milestone2/data/exports/quality_report.md`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/data/exports/quality_report.md):

1. **Foreign Key Integrity**:
   - `property.development_id`: **0 Orphans**
   - `property.location_id`: **0 Orphans**
   - `property.property_type_id`: **0 Orphans**
   - `property_amenity.property_id` / `amenity_id`: **0 Orphans**
   - `user_focus_area.user_id` / `location_id`: **0 Orphans**
   - `review.user_id` / `development_id`: **0 Orphans**
2. **Numeric Metric Distributions**:
   - **Price (EGP)**: Min: `2,291,527.00` | Avg: `7,833,065.17` | Max: `15,850,000.00`
   - **Area (sqm)**: Min: `12.50` | Avg: `111.88` | Max: `260.00`
   - **Price per sqm (EGP)**: Avg: `104,075.36`
   - **Down Payment (EGP)**: Min: `325,345.00` | Avg: `2,554,401.43` | Max: `5,568,000.00`
   - **Contract Year**: Min: `2023` | Avg: `2024.4` | Max: `2026`
3. **Encoding & Charset**:
   - Database connection and tables use `utf8mb4`.
   - Arabic location names (e.g. `التجمع الخامس`, `رأس الحكمة`, `6 أكتوبر`) and developer names round-trip with full fidelity.

---

### 4.3 Milestone III Analytics Query Outputs
Execution of [`milestone2/validate/m3_smoke_queries.sql`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/validate/m3_smoke_queries.sql) verifies that all analytical queries execute cleanly on the populated data:

1. **Top Projects by Resale Inventory & Gain**:
   - Lists projects such as *Koun* (15.85M EGP asking, 2.15M gain), *Patio Vida* (12.94M EGP asking, 2.06M gain), *Badya - بادية* (11.22M EGP asking, 780K gain), and *Hacienda Waters - هايسندا وترز* (11.58M EGP asking, 8.42M gain).
2. **Development Location, Unit Types & Avg Price/sqm**:
   - Groups developments by area and calculates average price per sqm for each unit type.
3. **Properties in Area by Price Range & Amenity Set (Relational Division)**:
   - Evaluates multi-amenity filtering using `GROUP BY p.property_id HAVING COUNT(DISTINCT pa.amenity_id) >= 2`.
4. **Top Developers by Listing Count & Metrics**:
   - Displays developers like *Palm Hills Developments*, *La Vista Developments*, *Mabany Idris*, and *Nawassy* with their average price/sqm, down payment, and gain.
5. **Project Reviews**:
   - Joins `review`, `app_user`, and `development` to display review ratings (1–10) and commentary.

Full query results can be inspected in [`milestone2/validate/m3_smoke_queries_output.txt`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/validate/m3_smoke_queries_output.txt).

---

## 5. Architectural Design Decisions (Why vs. Alternatives)

| Topic | Chosen Decision | Alternative Considered | Trade-off & Professor Defense |
|---|---|---|---|
| **Derived Metrics** | `price_per_sqm` and `age` exposed dynamically via Views (`v_property_metrics`, `v_user_profile`). | Redundant stored columns in `property` and `app_user`. | Storing derived metrics causes temporal drift (age changes every year) and update anomalies if price/area changes. Views ensure 100% calculation consistency. |
| **Crawler Idempotency** | Added `source_listing_id VARCHAR(100) UNIQUE NOT NULL` to `property`. | Relying solely on surrogate `property_id`. | Enables `INSERT ... ON DUPLICATE KEY UPDATE`. Re-running the crawler or database loader produces identical counts without duplicate records. |
| **Location Modeling** | Single self-referencing `location` table (`parent_location_id`). | Three separate tables (`governorate`, `city`, `area`). | Allows flexible administrative hierarchies (e.g. Cairo → New Cairo → 5th Settlement) and enables clean M:N foreign key linking in `user_focus_area` without needing multiple join tables. |
| **Lookup Tables vs ENUM** | Lookup tables (`property_type`, `payment_method`, `amenity`) with surrogate keys and unique names. | Hardcoded MySQL `ENUM(...)`. | Milestone II crawlers encounter newly introduced property types and amenities. Modifying an `ENUM` requires costly `ALTER TABLE` locks, whereas lookup tables accommodate dynamic inserts. |
| **CSV Export Encoding** | UTF-8 with Byte Order Mark (`utf-8-sig`). | Plain UTF-8 without BOM or ASCII. | Microsoft Excel defaults to Windows-1252 when opening CSV files, corrupting Arabic text. Adding a UTF-8 BOM forces Excel to render Arabic correctly. |
| **User Seeding** | Python `Faker` with fixed seed `2501`. | Unseeded random values. | Guarantees deterministic, reproducible results for grading and demonstration while adhering to assignment constraints (`example.com` emails). |

---

## 6. Official Submission Checklist

- [x] **Milestone I: ERD (Deliverable 1)** — Provided in Mermaid ([`erd.mmd`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/erd.mmd)), DBML ([`erd.dbml`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/erd.dbml)), and textual format ([`erd_description.md`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/erd_description.md)).
- [x] **Milestone I: Relational Model (Deliverable 2)** — Documented with functional dependencies, BCNF proofs, and referential integrity in [`relational_model.md`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/relational_model.md).
- [x] **Milestone I: SQL Schema Transcript (Deliverable 3)** — Verified MySQL DDL script in [`schema.sql`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/schema.sql) and execution output in [`schema_transcript.txt`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone1/schema_transcript.txt).
- [x] **Milestone II: Crawling Script (Deliverable 1)** — Full runnable codebase packaged in [`deliverables/crawler/`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/deliverables/crawler/).
- [x] **Milestone II: Populated Dump (Deliverable 2)** — Validated MySQL database dump in [`resale_properties_dump.sql`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/deliverables/resale_properties_dump.sql).
- [x] **Milestone II: Table CSV Files (Deliverable 3)** — 11 table CSVs (`utf-8-sig`) and [`_manifest.csv`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/deliverables/csv/_manifest.csv) in [`deliverables/csv/`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/deliverables/csv/).

