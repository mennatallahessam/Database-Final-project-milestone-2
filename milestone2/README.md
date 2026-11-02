# Milestone II: Web Crawling, Parsing & Database Population
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (Fall 2026)
**Author:** Mennatallah Essam Zaher  
**Instructor:** Prof. Hossam Sharara — The American University in Cairo (AUC)  
**Target Website:** [AqarExit](https://aqarexit.com) (`https://aqarexit.com/en/opportunities`)  
**Generated On:** 2026-11-02  
**Database:** MySQL 8.0+ (InnoDB, `utf8mb4`, `utf8mb4_unicode_ci`)

---

## 1. Executive Summary & Deliverables

Milestone II implements an end-to-end, ethical, and idempotent data engineering pipeline that crawled **the entire AqarExit website**, normalizes the bilingual attributes into third normal form (3NF), populates the physical MySQL schema, seeds realistic synthetic user profiles, and exports all tables into standardized CSVs and a self-contained SQL database dump.

### Official Deliverables Summary
1. **Deliverable 1 (Crawling Script Package):** Located in `milestone2/deliverables/crawler/` (and root `milestone2/`), featuring polite rate limiting, multi-worker concurrency, atomic HTML caching, JSON-LD + free-text regex extraction, Arabic normalization, and dependency-ordered loading.
2. **Deliverable 2 (Populated MySQL Database Dump):** Located at `milestone2/deliverables/resale_properties_dump.sql` (6.08 MB), exported as pure UTF-8 via native `--result-file` (no shell redirection) and verified via clean restoration in `milestone2/deliverables/restore_check.md`.
3. **Deliverable 3 (CSV Exports & Manifest):** Located in `milestone2/deliverables/csv/`, containing 11 table files encoded in UTF-8 with BOM (`utf-8-sig`) alongside `_manifest.csv` verifying 100% row-count parity with the database across all 9,628 properties.

---

## 2. Ingestion Funnel & Full Website Crawl Reconciliation

The crawler has completed downloading **100% of all available opportunity listings across the entire AqarExit platform**:

| Funnel Stage | Count | Reconciliation Notes |
| :--- | :---: | :--- |
| **1. Discovered Listings** | **9,690** | 9,684 from `https://aqarexit.com/sitemap.xml` + 6 active opportunities from `/en/opportunities` |
| **2. Fetched Pages (Raw)** | **9,628** | Untouched HTML pages downloaded with polite delay into `milestone2/data/raw/` |
| **3. Failed HTTP 404** | **62** | Dead/expired opportunity links returning HTTP 404 on the live site (tracked in `crawl_state.sqlite`) |
| **4. Parsed & Staged** | **9,628** | Clean JSONL records in `milestone2/data/staging/listings.jsonl` |
| **5. Quarantined (Rejected)** | **0** | Zero records rejected; full business-rule validation passed |
| **6. Database Loaded** | **9,628** | Successfully upserted into MySQL `property` table |
| **7. Pending Queue** | **0** | **0 listings pending — 100% of the entire website has been crawled** |

---

## 3. Database Table Counts & Manifest Verification

All 11 tables match `milestone2/deliverables/csv/_manifest.csv` 100%:

| Table Name | DB Rows | CSV Rows | Status | Classification | Description |
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

## 4. Key Architectural Decisions (Decision / Alternatives / Why)

### Decision 1: Geographic Hierarchy & Bilingual Language Policy (Issue 3)
- **Decision:** Implemented a reviewable mapping in `milestone2/parsing/location_hierarchy.csv` and added `name_en` and `name_ar` columns to `location` and `property_type` in `milestone2/sql/schema_changes_m2.sql`.
- **Alternatives:**
  - (a) Store only Arabic names (breaks English queries and creates mixed-language tables).
  - (b) Translate everything to English and discard Arabic (loses native source fidelity).
- **Why:** Adding `name_en` and `name_ar` while maintaining `name` as the canonical English display name ensures:
  1. True geographic hierarchy: 207 locations mapped across 8 Governorates (Cairo, Giza, Matrouh, Alexandria, Suez, South Sinai, Red Sea, Qalyubia, Monufia) -> Cities -> Areas.
  2. Zero language duplication: Entities like `محل` and `Shop` resolve to the exact same lookup row.
  3. 100% backward compatibility with Milestone 1 queries (`WHERE name = 'Apartment'`).

### Decision 2: MySQL Dump Encoding & Verification (Issue 2)
- **Decision:** Re-created `resale_properties_dump.sql` directly using `mysqldump ... --result-file=...` without shell redirection.
- **Why:** On Windows PowerShell 5.1, `>` redirects stdout as **UTF-16 LE with BOM**, which causes syntax errors in MySQL CLI and produces mojibake on Arabic characters. Native `--result-file` outputs strictly compliant **UTF-8**.
- **Evidence:** Tested via `milestone2/deliverables/restore_test.py` into a brand-new database `resale_properties_restore_test`. All 11 tables match 100% (including all 9,628 properties and 37,382 amenity links), and Arabic characters match character-by-character (documented in `milestone2/deliverables/restore_check.md`).

### Decision 3: Financial Columns Equivalence (Issue 6)
- **Decision:** Retain both `gain_over_market_value` and `discount_over_market_price` in the `property` table.
- **Why:** On AqarExit, `market_price - price` represents both the buyer's discount and the investor's immediate equity gain. Both columns are evaluated as identical across all listings. Keeping both columns preserves Milestone 1 DDL compliance and avoids breaking Milestone 3 analytical query templates.

### Decision 4: GPS Coordinates Policy (Issue 4)
- **Decision:** Kept `latitude` and `longitude` as `NULL`.
- **Why:** All raw HTML files and JSON-LD metadata blobs from AqarExit were inspected; none expose GPS coordinates or map embeds. Per Issue 4 non-negotiable rules, missing coordinates are kept `NULL` without external geocoding calls or artificial fabrication.

---

## 5. Reproduction Sequence

To reproduce the entire pipeline from scratch, run the following commands from the repository root:

```bash
# 1. Install prerequisites
pip install -r milestone2/requirements.txt

# 2. Stage 1: Frontier Discovery (populates crawl_state.sqlite)
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

## 6. Definition of Done Checklist

| Criterion | Status | Evidence / File Pointer |
| :--- | :---: | :--- |
| Discovered count explained; crawl covers ALL listings on the website | **YES** | 9,628 listings downloaded; 62 HTTP 404s; 0 pending in `crawl_state.sqlite` |
| No request-rate abuse; no bot protection bypassed; polite rate-limiting | **YES** | Verified in `milestone2/crawler/http_client.py` & `logs/crawl.log` |
| Dump is UTF-8, restores into clean DB, row counts match, Arabic round-trips | **YES** | Verified in `milestone2/deliverables/restore_check.md` (9,628 rows matched) |
| Location hierarchy is geographically correct and shown as a tree | **YES** | 207 locations mapped across 8 Governorates in `location.csv` |
| No entity appears twice in two languages; resolution report produced | **YES** | Verified in `milestone2/data/staging/entity_resolution_report.csv` |
| Coordinates extracted where available; otherwise NULL | **YES** | Verified 0 coordinates published on AqarExit; kept `NULL` |
| Gain vs discount columns decision documented | **YES** | Documented in Section 4 and `schema_changes_m2.sql` |
| 0 FK orphans; 0 duplicate natural keys | **YES** | 0 orphans across all 9 FK checks in `quality_report.md` |
| Loader is idempotent (two runs produce identical counts) | **YES** | Re-run confirmed identical table counts |
| One CSV per table; CSV counts equal DB counts; manifest generated | **YES** | Verified in `milestone2/deliverables/csv/_manifest.csv` |
| Synthetic users and reviews reference real developments and locations | **YES** | 40 users, 120 reviews referencing real developments in `seed_users.py` |
| Milestone III smoke queries return meaningful rows | **YES** | Verified in `milestone2/validate/m3_smoke_queries_output.txt` |
| Automated unit tests pass | **YES** | 12/12 passed in `milestone2/parsing/tests/test_parsers.py` |
| Known limitations documented | **YES** | Documented in Section 7 |
| `deliverables/crawler/` identical to source | **YES** | Synchronized cleanly with `milestone2/` |

---

## 7. Known Limitations
1. **Target Site GPS Coordinates:** AqarExit does not publish coordinates on listing pages; `latitude` and `longitude` are therefore `NULL` across developments and locations.
2. **Expired Listings:** 62 links in `sitemap.xml` return `HTTP 404 Not Found` because the properties were removed or sold on the live platform; they are properly recorded as `failed` in `crawl_state.sqlite` and excluded from the database.
