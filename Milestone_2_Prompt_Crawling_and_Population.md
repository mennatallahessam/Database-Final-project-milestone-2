# MILESTONE II MASTER PROMPT: Web Crawling & Database Population
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (F26)

> Paste everything below the line into your AI coding assistant (Claude Code, Cursor, Copilot Chat, etc.).
> **Before you start, attach/paste:** (1) your final Milestone I `schema.sql`, (2) a saved HTML file or screenshot of one **listing page** and of the **listing index page** from AqarExit.
> **Time warning:** Milestone II is worth **50 points** and is due **31 October 2026**. Section 12 is a time-boxed plan; follow it.

---

## 0. ROLE AND CONTEXT

You are a senior data engineer and Python developer helping a computer-engineering student finish **Milestone II** of *CSCE 2501 – Fundamentals of Database Systems* (Prof. Mohamed Alhalaby, AUC, Fall 2026).

**The project:** a database application for **real-estate properties in Egypt offered for resale**, built on the public website **AqarExit**: `https://aqarexit.com/en/opportunities?show=8000`. Milestone I produced the MySQL schema (attached). Milestone III will be an application that connects to this database hosted on a **remote** MySQL server and answers analytics queries, so **data quality in Milestone II directly determines the Milestone III result**.

### Official Milestone II requirements (verbatim intent, this is your source of truth)
- "Write a **web crawler** to crawl the pages from the AqarExit website for **all the properties listed**."
- "**Parse the HTML** you crawled and extract the relevant fields for populating the **non-user tables** in your schema."
- "Note that you may need to **extract some of the fields from the text fields** in the web pages."
- "At the end of this milestone, you should have **all your non-user tables populated** with the extracted data."
- "For the **user tables**, use **sample test information** to populate the relevant tables."
- "Make sure to **rate-limit requests** (**Cloudflare is present**; aggressive scraping risks IP blocks)."
- **Tools suggested:** Scrapy, PyCharm, BeautifulSoup, Selenium, Python (or any other crawler library/language).
- **Note:** slide 6 of the deck says "property finder website". That is a leftover from a template; the target site is **AqarExit**.

### Official deliverables (exactly three, do not skip any)
1. **Crawling script**
2. **Populated MySQL database dump**
3. **CSV files for the values in each table**

---

## 1. NON-NEGOTIABLE RULES

1. **Be polite and stay within the rules (this is both an ethics and a survival issue).**
   - Check `https://aqarexit.com/robots.txt` and the site's terms first; summarize what they say in the README and obey disallowed paths.
   - **Do NOT** bypass or defeat Cloudflare or any bot protection: no stealth plugins, no fingerprint spoofing, no CAPTCHA solving, no proxy/IP rotation to evade blocks. If you hit a challenge page, **stop, back off, and tell me**. The supported fallbacks are: slow down, use a real browser session via Selenium at human-like pace, or reduce the scope.
   - Use an honest `User-Agent` that identifies the project (e.g. `CSCE2501-AUC-StudentProject/1.0 (student; contact: <my email>)`).
   - Only crawl **public** pages. No login. **Never collect or store personal data of sellers/agents** (phone numbers, personal emails, names of individuals). The schema does not need them.
2. **Never fabricate data.** If a field is not on the page and cannot be reliably parsed from text, store `NULL`, never a guess or default. Never hardcode counts like "8000 listings". Reconcile against what the site itself reports.
3. **Use my Milestone I schema exactly.** If you discover the real data requires a schema change (e.g. a column that is too narrow, a missing field), do **not** silently alter it. Produce `schema_changes_m2.sql` (migration), explain each change, and apply it only after listing it for me.
4. **Never lose crawled pages.** Every fetched page is saved raw to disk first. Parsing must be re-runnable offline without re-fetching (this is also your main rate-limit protection).
5. **Idempotent and resumable.** Running any stage twice must not duplicate rows. Killing the crawler and restarting must resume where it stopped.
6. **No secrets in code.** DB credentials come from `.env` (provide `.env.example`).
7. **Real execution, real output.** Run the code, show real counts and real logs. If something cannot be run in your environment, say so and give me the exact command to run.

---

## 2. TECH STACK (decide in Phase 1, then commit)

- **Language:** Python 3.11+.
- **Fetching:** prefer, in this order:
  1. A **JSON/XHR endpoint** the site's own frontend uses (discover it in Phase 1 via the browser DevTools Network tab, or by inspecting how `?show=8000` and pagination load data). Calling the same data the page itself loads, at a slow rate, is far lighter on the server than rendering thousands of pages.
  2. **Scrapy** (or `requests` + `BeautifulSoup4` with `lxml`) if the pages are server-rendered HTML.
  3. **Selenium/Playwright** only if the content is rendered by JavaScript and no usable endpoint exists. Use it headless but slowly, reuse one browser session, and never run parallel browsers.
- **DB access:** `SQLAlchemy` or `mysql-connector-python` / `PyMySQL`.
- **Data handling:** `pandas` for CSV export and validation; `python-dotenv`; `tenacity` (or manual) for retries; `Faker` for user test data.
- **Justify your choice** in the README with the evidence you found in Phase 1.

---

## 3. REPOSITORY LAYOUT (create exactly this)

```
milestone2/
├── README.md                    # how to run, decisions, robots/ToS summary, limitations
├── requirements.txt
├── .env.example                 # DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, CRAWL_* settings
├── config.py                    # all tunables in one place
├── sql/
│   ├── schema.sql               # Milestone I schema (unchanged)
│   └── schema_changes_m2.sql    # only if truly needed
├── crawler/
│   ├── discover.py              # Stage 1: collect all listing URLs/IDs
│   ├── fetch.py                 # Stage 2: download listing pages to data/raw/
│   ├── http_client.py           # polite session: delays, retries, backoff, UA
│   └── state.py                 # crawl state (SQLite or JSONL): pending/done/failed
├── parsing/
│   ├── parse_listing.py         # raw HTML/JSON -> dict of fields
│   ├── text_extractors.py       # regex/NLP helpers for fields hidden in free text
│   ├── normalize.py             # names, numbers, currency, Arabic digits, units
│   └── tests/                   # unit tests with saved sample pages
├── load/
│   ├── load_db.py               # staging -> MySQL, FK-safe order, upserts
│   ├── seed_users.py            # sample user data (users, focus areas, reviews)
│   └── export_csv.py            # one CSV per table
├── validate/
│   ├── quality_report.py        # row counts, null rates, duplicates, orphans, ranges
│   └── m3_smoke_queries.sql     # the 10 Milestone III queries to prove usability
├── data/
│   ├── raw/                     # saved HTML/JSON, one file per listing (git-ignored)
│   ├── staging/                 # parsed records (JSONL or SQLite)
│   └── exports/                 # CSVs + dump
├── logs/
└── deliverables/
    ├── crawler/                 # copy of crawling script for submission
    ├── resale_properties_dump.sql
    └── csv/<table>.csv
```

---

## 4. PHASE 1: RECONNAISSANCE (do this BEFORE writing the crawler; report findings to me)

Fetch **at most ~10 pages total** during recon, slowly, and save them.

1. Fetch and summarize `robots.txt`. Note any `Crawl-delay`, disallowed paths, sitemap links.
2. Check for a **sitemap** (`/sitemap.xml`, referenced in robots) that lists listing URLs. That is the cleanest enumeration method.
3. Open the index page `https://aqarexit.com/en/opportunities?show=8000` and determine:
   - Does `show=8000` mean "show up to 8000 items per page", a page-size parameter, or something else? Test with a *small* number first (e.g. `show=20`) to see how the parameter behaves, then decide.
   - How are listings enumerated: pagination (`page=`), infinite scroll, "load more" XHR, or all at once?
   - What is the **total number of listings** the site reports? Record it as the reconciliation target.
   - Is the listing data embedded as JSON in the HTML (e.g. `__NEXT_DATA__`, `application/ld+json`, a `<script>` state blob)? That is far more reliable to parse than CSS selectors.
4. Open 3 to 5 **different** listing pages (different property types, one with a development and one without, one with many amenities) and write a **field inventory table**:

   | Field on page | Where (CSS selector / JSON path / free text) | Example raw value | Target table.column | Parsing rule |
   |---|---|---|---|---|

5. Detect whether Cloudflare presents a challenge (HTTP 403/429/503, "Just a moment...", JS challenge). Report the exact behaviour and the request rate at which it appears. **Do not try to defeat it.**
6. Estimate **crawl time**: `listings × delay`. (Example: 8000 listings × 3 s ≈ 6.7 hours.) Propose the chosen delay and concurrency, and whether the index endpoint provides enough data to avoid fetching every detail page.
7. **STOP and present the Phase 1 report** (stack decision, enumeration method, field inventory, risks, time estimate) before building. Wait for my "go" unless I said to proceed automatically.

---

## 5. PHASE 2: THE CRAWLER

### 5.1 Stage 1: Discovery (`discover.py`)
- Enumerate **every** listing (via sitemap, index pagination, or the JSON endpoint). Store each as a row `(source_listing_id, url, discovered_at, status='pending')` in the crawl-state store.
- Deduplicate by `source_listing_id` / canonical URL.
- Record the **total discovered** and compare with the site's reported total. Flag mismatches.

### 5.2 Stage 2: Fetching (`fetch.py`, `http_client.py`)
**Rate-limiting and politeness (mandatory, configurable in `config.py`):**
- **Concurrency: 1** (maximum 2). No parallel hammering.
- **Delay between requests:** randomized **uniform 2.5 to 6 seconds** (jitter, never a fixed interval). If robots.txt gives a larger `Crawl-delay`, obey it.
- If using Scrapy: `ROBOTSTXT_OBEY=True`, `CONCURRENT_REQUESTS=1`, `DOWNLOAD_DELAY≥3`, `RANDOMIZE_DOWNLOAD_DELAY=True`, `AUTOTHROTTLE_ENABLED=True` with a conservative `AUTOTHROTTLE_TARGET_CONCURRENCY≈1.0`, `RETRY_TIMES=3`, `HTTPCACHE_ENABLED=True`.
- **Backoff:** on HTTP **429/503/403** or a challenge page, exponential backoff (e.g. 30 s → 60 s → 120 s → 300 s …) and honour `Retry-After`. After **3 consecutive** blocks, **pause the whole crawl for 15+ minutes**; after repeated failure, **stop cleanly** and print a clear message instead of retrying forever.
- **Circuit breaker:** if the block rate in the last 20 requests exceeds ~30%, halt.
- Reuse a single HTTP session (keep-alive), send `Accept-Language: en`, send the honest UA.
- Timeouts on every request (connect 10 s, read 30 s).
- **Never** retry the same URL in a tight loop.

**Persistence & resume:**
- Save each response **untouched** to `data/raw/<source_listing_id>.html` (or `.json`) **before** parsing; write atomically (temp file → rename).
- Update the state store after every request: `done`, `failed(reason, attempts)`, or `blocked`.
- On restart, skip everything already `done` and whose raw file exists and is non-empty.
- Support CLI flags: `--limit N` (crawl only N listings, for testing), `--resume`, `--retry-failed`, `--only-id <id>`, `--dry-run`.
- Detect and discard **soft-404 / challenge pages** saved by mistake (e.g. tiny pages, "Just a moment", missing expected markers) and mark them `failed`, never `done`.

**Observability:** structured log (`logs/crawl.log`) with timestamp, URL, status code, elapsed ms, bytes, attempt. Print a progress line every 25 requests: done / pending / failed / ETA.

### 5.3 Test the crawler incrementally
1. `--limit 5` → inspect raw files by eye.
2. `--limit 50` → run the parser (Phase 3) on them and confirm field coverage.
3. Only then start the full crawl **in the background** (see Section 12 for the schedule) while you build parsing/loading on the cached pages.

---

## 6. PHASE 3: PARSING & EXTRACTION

### 6.1 General rules
- Prefer **structured data** (embedded JSON / JSON-LD / API JSON) over CSS selectors; use selectors only as fallback. Wrap each field extractor in its own function with a docstring that states the source location and fallback.
- Parsing is a **pure function** of raw file → `dict`. It performs no network or DB access.
- Parsing must never crash on one bad page: catch per-field errors, record `parse_warnings` for that listing, continue.
- Output goes to `data/staging/listings.jsonl` (one JSON object per listing) including `source_listing_id`, `source_url`, `scraped_at` and a `parse_warnings` list.
- Write **unit tests** (`pytest`) using 5+ saved pages, including edge cases (no development, no bathrooms, Arabic text, missing price).

### 6.2 Fields to extract (map every one to the Milestone I schema; use the exact column names from my `schema.sql`)
For **each property** (include everything the page offers, the requirement says "including but not limited to"):
- Source id and URL
- Title; **description** (full text, cleaned of HTML but otherwise untouched)
- **Property type** (apartment, villa, townhouse, duplex, ...)
- **Area** in sqm
- **Bedrooms**, **bathrooms**
- **Location**: governorate / city / area (the full hierarchy as the page presents it) and coordinates if present
- **Development / project** name, and its **developer**, location, coordinates (if present)
- **Amenities** list
- **Payment method**
- **Asking price**, **market price / current market value**, **gain over current value** (amount and/or %), **discount over market price**
- **Down payment**, **installment amount** and terms (years, frequency) if shown
- **Contract year** (or contract date)
- Any other attribute the schema has a column for

### 6.3 "Extract fields from the text" (explicitly required by the assignment)
Some values are embedded in free text (title/description) instead of labelled fields. Build `text_extractors.py` with **well-tested, documented regex/heuristic extractors**, each returning `(value, confidence, matched_snippet)`:
- Bedrooms/bathrooms from phrases like `3 BR`, `3 bedrooms`, `3 غرف`, `2 bath`.
- Area from `150 sqm`, `150 m²`, `150 م²`.
- Money from `EGP 1,500,000`, `1.5M`, `1.5 million`, `1,500,000 جنيه`, `ج.م`.
- Percentages from `25% down payment`, `gain 12%`.
- Year from `contract 2021`, `contracted in 2020`.
- Installment terms from `8 years`, `quarterly`.
- Amenity keywords from the description when the structured amenity list is absent (keep a controlled vocabulary in a dict; log unmatched candidates).
- Use structured fields **first**; use text extraction **only to fill gaps**, and record the source of each value (`structured` / `text`) in staging for auditability.

### 6.4 Normalization (`normalize.py`)
- Convert **Arabic-Indic digits** (`٠١٢٣٤٥٦٧٨٩`) and Arabic decimal/thousand separators to ASCII before numeric parsing.
- Strip currency symbols and thousand separators; store numbers as `Decimal`, never `float`. Default currency `EGP`; if another currency appears, record it, don't silently convert.
- Normalize units to **sqm**.
- Trim and collapse whitespace; Unicode-normalize (NFC); case-fold for matching **but keep the original display casing** for storage.
- **Entity resolution:** the same developer/development/area often appears with spelling variants (`Palm Hills`, `PALM HILLS Developments`, `Palm Hills Development`). Build a normalization key per entity and a small, **reviewable alias map**; emit `data/staging/entity_resolution_report.csv` listing merges and near-duplicates so a human can check them. Do not blindly fuzzy-merge distinct entities (e.g. "Sodic West" vs "Sodic East").
- Validate ranges and **quarantine** (do not load) records that fail hard rules, writing them to `data/staging/rejected.jsonl` with the reason: negative/zero area or price, `down_payment > price`, bedrooms > 20, contract year outside 1990..current year+1, etc. Soft anomalies (e.g. price/sqm outliers) are loaded but flagged in the quality report.

---

## 7. PHASE 4: LOADING THE DATABASE (`load_db.py`)

1. Connect using `.env`. Create the schema from `sql/schema.sql` (fresh DB) when `--init` is passed.
2. **Load in dependency order** (parents first), inside transactions, in batches (e.g. 500 rows):
   1. lookup/reference tables: `property_type`, `payment_method`, `amenity`
   2. `location` hierarchy (top-down: governorate → city → area)
   3. `developer`
   4. `development`
   5. `property`
   6. `property_amenity`
   (Use the actual table names from my schema.)
3. **Upsert logic:** `INSERT ... ON DUPLICATE KEY UPDATE` keyed on each table's natural unique key (`source_listing_id` for property; unique name constraints for lookups). Re-running the loader must produce **identical row counts**.
4. Look up FK IDs through in-memory dictionaries built from the DB (`name_key → id`) instead of one SELECT per row.
5. If a property has no development, store `development_id = NULL`; never invent a placeholder development like "Unknown".
6. Use `utf8mb4` on the connection (`charset='utf8mb4'`), verify Arabic round-trips correctly (`SELECT` a known Arabic string and compare).
7. Log inserted / updated / skipped / rejected counts per table.
8. **Do not touch the user tables in this step.** They are seeded separately (Section 8).

---

## 8. PHASE 5: USER TABLES WITH SAMPLE DATA (`seed_users.py`)

The assignment says: "For the user tables, use **sample test information**."
- Use `Faker` with a fixed seed (e.g. `Faker.seed(2501)`) for **reproducible** output.
- Create **~30 to 50 users**: realistic unique usernames; **unique emails on the reserved domain `example.com`** (never real people's emails); genders drawn from the allowed values in my schema; **birthdates** giving ages roughly 18 to 65 with a believable distribution (and consistent with the derived `age` if my schema exposes it); `registered_at` timestamps within the last 12 months.
- **Focus areas:** each user gets 1 to 4 areas **chosen from locations that actually exist** in the populated `location` table (weight toward popular areas, e.g. New Cairo, North Coast, 6th of October, if present).
- **Reviews:** ~100 to 200 reviews, each referencing an **existing user** and an **existing development** from the crawled data. Rating is an integer 1..10, with a realistic skewed distribution (not uniform); review text is plausible, varied English sentences (a template pool combined with development-specific details is fine); `created_at` after the user's `registered_at`. Weight reviews toward developments with more listings. If my schema allows only one review per user per development, respect that.
- **Everything must be clearly marked as synthetic** in the README. These users are fake.
- Idempotent: re-running wipes and re-seeds the user tables only (inside a transaction), without touching crawled data.

---

## 9. PHASE 6: VALIDATION (`validate/`)

### 9.1 `quality_report.py` → `data/exports/quality_report.md`
- **Reconciliation:** site-reported total vs discovered vs fetched vs parsed vs loaded vs rejected (a funnel table).
- **Row counts per table.**
- **Null/missing rate per column** (table), highlighting key analytic fields: price, area, down payment, market price, contract year, location, type.
- **Duplicate checks:** duplicate `source_listing_id`, duplicate normalized names in lookups.
- **FK orphan checks** for every FK (must be 0).
- **Range checks:** min/median/max for price, area, price/sqm, down payment %, bedrooms; list the top 20 outliers for human review.
- **Text-extraction coverage:** for each field, % from structured data vs % from text vs % missing.
- **Charset check** on Arabic strings.

### 9.2 `m3_smoke_queries.sql`
Run one query per Milestone III functionality against the **real populated data** and show the first rows of each, to prove the data supports the final app:
1. Top 10 projects by resale inventory / resale amount / gain over market value, by property type
2. A development's location, avg price per sqm, and listing counts per unit type
3. All properties in an area with avg price per sqm per unit type
4. Properties in an area within a price range having a given set of amenities
5. Top 5 developers by number of resale listings with avg price/sqm, avg down payment, gain over market value
6. Properties by area, property type, and contract year
7. By area and development: avg installment price, avg down payment, number of properties, avg discount over market price, avg age of contract year, avg market price
8. View reviews of a project (join users and reviews)

If any query returns empty or nonsense because a column is mostly NULL, **report it as a data problem** and propose a fix (better extraction, a schema tweak) before I submit.

---

## 10. PHASE 7: DELIVERABLES

### 10.1 Deliverable 1: Crawling script
- A clean, commented, runnable crawler (all code in `crawler/`, `parsing/`, `load/`), copied into `deliverables/crawler/`.
- `README.md` with: prerequisites, `pip install -r requirements.txt`, `.env` setup, and the **exact command sequence**:
  ```
  python -m crawler.discover
  python -m crawler.fetch --resume
  python -m parsing.parse_listing --all
  python -m load.load_db --init
  python -m load.seed_users
  python -m load.export_csv
  python -m validate.quality_report
  ```
- A section "Rate-limiting and ethics" describing the delays, backoff, robots.txt compliance, and the fact that no protection was bypassed.

### 10.2 Deliverable 2: Populated MySQL database dump
- Command: `mysqldump --single-transaction --routines --triggers --default-character-set=utf8mb4 --set-gtid-purged=OFF -u <user> -p resale_properties > deliverables/resale_properties_dump.sql`
- Verify the dump by **restoring it into a fresh empty database** and re-running the row counts; show that the counts match. The dump must contain schema + data and must run without manual edits.

### 10.3 Deliverable 3: CSV files for the values in each table
- **One CSV per table**, **all tables including user tables and join tables**, named `<table>.csv`, in `deliverables/csv/`.
- UTF-8 **with BOM** (`utf-8-sig`) so Excel shows Arabic correctly; header row = exact column names; `NULL` exported as an empty field; decimals as plain numbers (no thousand separators, no scientific notation); dates ISO-8601; embedded commas/quotes/newlines properly quoted (use `csv.QUOTE_MINIMAL` via pandas/csv module).
- A `csv/_manifest.csv` listing table name, row count, and file size, and a check that **CSV row counts equal DB row counts** for every table.

---

## 11. DEFINITION OF DONE (answer each YES/NO in the README; fix every NO)

- [ ] robots.txt and ToS reviewed; no bot protection bypassed; honest UA used.
- [ ] Crawl is rate-limited (2.5 to 6 s jittered, concurrency 1), with backoff, circuit breaker and resume.
- [ ] Every fetched page saved raw; parsing re-runs offline.
- [ ] Listings crawled reconcile with the site's reported total (gaps explained).
- [ ] All non-user tables populated (property, development, developer, location, property_type, payment_method, amenity, property_amenity, ...).
- [ ] Fields hidden in text are extracted by documented, unit-tested extractors.
- [ ] No fabricated values; unknowns are NULL; rejected rows quarantined with reasons.
- [ ] Entity-resolution report produced and spot-checked.
- [ ] User tables populated with clearly synthetic, reproducible sample data referencing real developments/areas.
- [ ] 0 FK orphans; 0 duplicate natural keys; ranges sane.
- [ ] Arabic text round-trips correctly through MySQL, dump, and CSV.
- [ ] Loader is idempotent (second run = same counts).
- [ ] Dump restores cleanly into a fresh DB; counts match.
- [ ] One CSV per table; CSV counts = DB counts.
- [ ] All Milestone III smoke queries return meaningful rows.
- [ ] README lists every assumption, known limitation, and exact reproduction steps.

---

## 12. TIME-BOXED PLAN (the deadline is tight, so work in this order)

| Block | Goal |
|---|---|
| 1 | Phase 1 recon + field inventory (report to me). |
| 2 | Discovery + fetch working on `--limit 50`. **Start the full crawl in the background as early as possible**, because polite crawling takes hours. |
| 3 | While the crawl runs: build parsers and tests on cached pages; build loader; seed users. |
| 4 | Load whatever has been crawled so far; run validation; fix extractors; re-parse offline (no re-fetching). |
| 5 | When the crawl finishes (or at a cut-off I set): final parse → load → seed → CSV → dump → restore test → README. |

**If the full crawl cannot finish before the deadline:** do not raise the request rate. Submit what has been crawled, make the README state the exact coverage (`N of M listings, X%`), and keep the script resumable so the remainder can be completed afterwards. Prioritize a **representative** sample (spread across areas, developments, and property types) over an arbitrary first-N.

---

## 13. STYLE OF YOUR RESPONSE

- Work phase by phase. After each phase show: files created, commands run, real output/counts, problems found.
- State every important decision as **Decision / Alternatives / Why**. The student must be able to defend each in the demo and README.
- Never use `TODO`/placeholder code in delivered files.
- If the real site contradicts anything in this prompt, **the real site and the official project text win**; tell me about the conflict.
- If you are blocked (Cloudflare challenge, endpoint missing, schema mismatch), stop and explain the options rather than improvising around the protection.
- Finish with a "What to hand in" list mapped to the three official deliverables.
