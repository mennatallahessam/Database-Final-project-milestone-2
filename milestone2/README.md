# Milestone 2: Web Crawling & Database Population
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (Fall 2026)
**Author:** Mennatallah Essam Zaher  
**Instructor:** Prof. Hossam Sharara (The American University in Cairo)

---

## 1. Official Deliverable Mapping

| Deliverable | Description | Corresponding Files / Directory | Status |
|---|---|---|---|
| **Deliverable 1** | **Crawling Script** | [`deliverables/crawler/`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/deliverables/crawler/) containing:<br>• `crawler/` (`discover.py`, `fetch.py`, `http_client.py`, `state.py`)<br>• `parsing/` (`parse_listing.py`, `text_extractors.py`, `normalize.py`, `tests/`)<br>• `load/` (`load_db.py`, `seed_users.py`, `export_csv.py`)<br>• `validate/` (`quality_report.py`, `m3_smoke_queries.sql`)<br>• `config.py`, `requirements.txt`, `.env.example` | Complete & Verified |
| **Deliverable 2** | **Populated MySQL Database Dump** | [`deliverables/resale_properties_dump.sql`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/deliverables/resale_properties_dump.sql)<br>Generated via `mysqldump` (UTF-8, routines, triggers, single-transaction). Verified by test-restoring into a clean database with 100% row-count match. | Generated & Verified |
| **Deliverable 3** | **CSV Files for Each Table** | [`deliverables/csv/`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/deliverables/csv/) containing 11 table CSVs (`utf-8-sig` with BOM for proper Excel Arabic rendering) + [`_manifest.csv`](file:///c:/Users/iRepair/Downloads/db%20final%20version/milestone2/deliverables/csv/_manifest.csv) verifying 100% row count match with the DB. | Exported & Verified |

---

## 2. Rate-Limiting, Politeness & Ethical Crawling

1. **Robots.txt & Sitemap Obedience**:
   - The crawler checks `https://aqarexit.com/robots.txt` upon startup.
   - Crawl paths are restricted strictly to explicitly allowed routes: `Allow: /` and `Allow: /buy/opportunity/`. Disallowed administrative routes (`/ops`, `/app`, `/stop`, `/*_rsc=`) are completely avoided.
   - Sitemap enumeration via `https://aqarexit.com/sitemap.xml` discovered **9,684** canonical opportunity listing URLs.
2. **Honest User-Agent**:
   - The crawler identifies itself transparently as an academic research project:
     `CSCE2501-AUC-StudentProject/1.0 (academic research; contact: student@aucegypt.edu)`.
3. **Zero Bot Protection Bypass**:
   - No stealth plugins, headless browser fingerprint evasion, CAPTCHA bypass, or IP rotators were utilized.
   - Politeness delays with uniform random jitter (**2.5 to 5.0 seconds**) prevent server strain.
4. **Resilience & Circuit Breaker**:
   - Implements exponential backoff on HTTP 429/503/403.
   - Implements a circuit breaker tripping after 3 consecutive challenge responses to prevent IP bans.
5. **Atomic Raw Persistence**:
   - Every downloaded listing is saved untouched as raw HTML in `data/raw/<listing_id>.html` before parsing. All parsing, normalization, and validation execute completely offline without re-fetching.

---

## 3. Architecture & Key Design Decisions

| Topic | Decision | Alternatives Considered | Justification & Professor Defense |
|---|---|---|---|
| **Crawling Engine** | `requests` session + `BeautifulSoup4` + `sitemap.xml` discovery. | Headless Selenium/Playwright browser automation. | AqarExit uses Next.js server-side rendering with embedded JSON-LD schema metadata and static HTML cards. Browser automation is unnecessary, heavyweight, and prone to bot triggers. Direct HTTP requests are 20x faster and polite to the server. |
| **Extraction Strategy** | Hybrid: structured JSON-LD `Product` schema first, HTML label parsing second, and regex text extraction as fallback. | CSS selector scraping only, or regex scraping only. | JSON-LD schema guarantees exact developer, unit type, and location fields. HTML labels capture exact payment splits. Text extractors rescue values embedded in description text. |
| **User Seeding** | Python `Faker` with fixed seed `2501`, generating 40 users and 120 reviews referencing real developments and real locations. | Completely random dummy records, or manual insertions. | Fixed seed provides 100% deterministic, reproducible evaluation for instructors and TAs. Linking to real crawled entities ensures foreign key integrity. |
| **CSV Export Encoding** | `utf-8-sig` (UTF-8 with Byte Order Mark). | Plain ASCII or UTF-8 without BOM. | Arabic location, developer, and property names corrupt in Microsoft Excel unless a UTF-8 BOM is present. |
| **Database Loading** | Foreign-key topological dependency order with in-memory lookup caching. | One SELECT query per record. | In-memory lookup dictionaries reduce database round-trips from thousands to dozens, executing the entire load in seconds. |

---

## 4. Step-by-Step Reproduction Pipeline

To reproduce the crawling, extraction, database population, and verification from scratch:

```bash
# 1. Install prerequisites
pip install -r milestone2/requirements.txt

# 2. Configure environment credentials
cp milestone2/.env.example milestone2/.env

# 3. Discover all listings from AqarExit sitemap and index
python -m milestone2.crawler.discover

# 4. Fetch listing pages with polite rate limiting (limit configurable)
python -m milestone2.crawler.fetch --limit 35 --resume

# 5. Parse all cached raw HTML pages into staging JSONL
python -m milestone2.parsing.parse_listing --all

# 6. Initialize MySQL schema and load crawled data
python -m milestone2.load.load_db --init

# 7. Seed synthetic users, focus areas, and reviews
python -m milestone2.load.seed_users

# 8. Export all tables to UTF-8 BOM CSV files
python -m milestone2.load.export_csv

# 9. Generate comprehensive data quality validation report
python -m milestone2.validate.quality_report

# 10. Run Milestone III analytical smoke queries
mysql -u root -p --default-character-set=utf8mb4 resale_properties < milestone2/validate/m3_smoke_queries.sql
```

---

## 5. Table Inventory & Reconciliation Summary

| Table | DB Rows | CSV Rows | Status | Role |
|---|---|---|---|---|
| `property` | **35** | **35** | MATCH | Core crawled resale listings |
| `developer` | **34** | **34** | MATCH | Crawled development companies |
| `development` | **35** | **35** | MATCH | Crawled projects / compounds |
| `location` | **18** | **18** | MATCH | Crawled geographic hierarchy |
| `property_type` | **6** | **6** | MATCH | Unit types (Apartment, Villa, etc.) |
| `payment_method` | **1** | **1** | MATCH | Payment structure |
| `amenity` | **8** | **8** | MATCH | Amenities (Pool, Security, Garage, etc.) |
| `property_amenity`| **139** | **139** | MATCH | M:N Property ↔ Amenity links |
| `app_user` | **40** | **40** | MATCH | Synthetic registered users |
| `user_focus_area` | **100** | **100** | MATCH | M:N User ↔ Focus Area links |
| `review` | **120** | **120** | MATCH | Synthetic reviews on real projects |

---

## 6. Definition of Done Checklist

- [x] **YES** — `robots.txt` and site terms reviewed; no bot protection bypassed; honest academic User-Agent used.
- [x] **YES** — Crawl is rate-limited (2.5 to 5.0 s jittered delay, concurrency 1), with exponential backoff, circuit breaker, and resume capability.
- [x] **YES** — Every fetched page is saved raw to disk (`data/raw/`); parsing re-runs 100% offline.
- [x] **YES** — Listings crawled reconcile with site sitemap (9,684 discovered listings tracked in state database).
- [x] **YES** — All non-user tables populated (`property`, `development`, `developer`, `location`, `property_type`, `payment_method`, `amenity`, `property_amenity`).
- [x] **YES** — Fields hidden in text are extracted by documented, unit-tested extractors (`test_parsers.py`).
- [x] **YES** — No fabricated values in crawled tables; missing fields stored as `NULL`; out-of-bounds rows quarantined.
- [x] **YES** — Controlled entity resolution maps developer spelling variants to canonical corporate names.
- [x] **YES** — User tables populated with reproducible synthetic sample data referencing real crawled developments and areas.
- [x] **YES** — Zero foreign key orphans; zero duplicate natural keys; metric ranges sane.
- [x] **YES** — Arabic text round-trips correctly through MySQL, dump, and CSV exports (`utf-8-sig`).
- [x] **YES** — Database loader is idempotent (repeated runs produce identical row counts).
- [x] **YES** — Dump restores cleanly into a fresh database with 100% row-count match verified.
- [x] **YES** — One CSV per table; CSV row counts equal DB row counts verified via `_manifest.csv`.
- [x] **YES** — All Milestone III analytical queries return meaningful rows on the populated database.

