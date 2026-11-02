# Milestone 2: Data Quality & Ingestion Validation Report
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (Fall 2026)

**Generated On:** 2026-11-02  
**Database:** `resale_properties` (MySQL 8.0, InnoDB, `utf8mb4`)

---
## 1. Crawl & Ingestion Reconciliation Funnel

| Funnel Stage | Count | Notes |
|---|---|---|
| **1. Discovered Listings** | 9690 | 9,684 from `sitemap.xml` + 6 active opportunities from `/en/opportunities` |
| **2. Fetched Pages (Raw)** | 9628 | Untouched HTML pages saved in `data/raw/` with polite rate-limiting |
| **3. Parsed & Staged** | 9628 | Clean JSONL records passing normalization and business rules |
| **4. Quarantined (Rejected)** | 0 | Records failing business rules (quarantine log: `rejected.jsonl`) |
| **5. Database Loaded** | 9628 | Successfully upserted into MySQL `property` table |
| **6. Pending Queue** | 0 | Remaining frontier in `crawl_state.sqlite` awaiting future batches |

> **Note on Crawl Scope & Ethics:** In accordance with Section 12 of the Milestone II Master Prompt, downloading all 9,690 listings at the required polite delay (2.5–5.0s jitter) requires ~10.8 hours of continuous fetching. To comply with anti-DDoS guidelines and prevent Cloudflare IP blocks, this submission delivers an initial representative sample of diverse listings across Cairo, Giza, Matrouh, Qalyubia, and South Sinai. The crawler is fully resumable and continues unattended via `python -m milestone2.crawler.fetch --all --resume`.

## 2. Table Row Counts

| Table Name | Row Count | Classification |
|---|---|---|
| `developer` | **3056** | Crawled Reference (Developers) |
| `location` | **207** | Crawled Geographic Hierarchy (Governorate -> City -> Area) |
| `development` | **6279** | Crawled Master Projects & Compounds |
| `property_type` | **11** | Bilingual Lookup (Apartment, Villa, Shop, etc.) |
| `payment_method` | **2** | Payment Term Lookup (Cash, Installments) |
| `amenity` | **10** | Controlled Vocabulary Lookup |
| `property` | **9628** | Core Resale Properties |
| `property_amenity` | **37382** | M:N Associative Bridge |
| `app_user` | **40** | Synthetic User Profiles |
| `user_focus_area` | **95** | M:N Associative (User Interests) |
| `review` | **120** | Synthetic Community Reviews |

## 3. Attribute Null Rates on `property` Table

| Column | Total Rows | Non-Null Rows | Null Rate (%) | Required by Schema? |
|---|---|---|---|---|
| `property_id` | 9628 | 9628 | 0.0% | YES (NOT NULL) |
| `source_listing_id` | 9628 | 9628 | 0.0% | YES (NOT NULL) |
| `source_url` | 9628 | 9628 | 0.0% | YES (NOT NULL) |
| `title` | 9628 | 9628 | 0.0% | NO (Nullable) |
| `description` | 9628 | 9628 | 0.0% | NO (Nullable) |
| `development_id` | 9628 | 9628 | 0.0% | NO (Nullable) |
| `location_id` | 9628 | 9628 | 0.0% | YES (NOT NULL) |
| `property_type_id` | 9628 | 9628 | 0.0% | YES (NOT NULL) |
| `payment_method_id` | 9628 | 9628 | 0.0% | NO (Nullable) |
| `area_sqm` | 9628 | 9628 | 0.0% | YES (NOT NULL) |
| `bedrooms` | 9628 | 9117 | 5.31% | NO (Nullable) |
| `bathrooms` | 9628 | 982 | 89.8% | NO (Nullable) |
| `price` | 9628 | 9628 | 0.0% | YES (NOT NULL) |
| `market_price` | 9628 | 9272 | 3.7% | NO (Nullable) |
| `down_payment` | 9628 | 9628 | 0.0% | NO (Nullable) |
| `installment_amount` | 9628 | 9628 | 0.0% | NO (Nullable) |
| `installment_frequency` | 9628 | 9628 | 0.0% | NO (Nullable) |
| `installment_years` | 9628 | 5397 | 43.94% | NO (Nullable) |
| `remaining_balance` | 9628 | 9571 | 0.59% | NO (Nullable) |
| `gain_over_market_value` | 9628 | 9272 | 3.7% | NO (Nullable) |
| `gain_percentage` | 9628 | 9272 | 3.7% | NO (Nullable) |
| `discount_over_market_price` | 9628 | 9272 | 3.7% | NO (Nullable) |
| `contract_year` | 9628 | 8933 | 7.22% | NO (Nullable) |
| `delivery_year` | 9628 | 8459 | 12.14% | NO (Nullable) |
| `currency` | 9628 | 9628 | 0.0% | YES (NOT NULL) |
| `scraped_at` | 9628 | 9628 | 0.0% | YES (NOT NULL) |

## 4. Geocoding & Coordinates Coverage

- `location` coordinates non-null: 0 / 207 (0.0% - AqarExit public opportunity pages and JSON-LD schemas omit GPS coordinates; coordinates are preserved as `NULL` per Issue 4 instructions).

## 5. Financial Columns Reconciliation (`gain` vs `discount`)

- Evaluated Rows: 9272
- Exact Matches (`gain_over_market_value == discount_over_market_price`): 9272 (100%)
- Mismatches: 0 (0)
- **Rationale:** In resale real-estate contracts, buying below market price represents both the buyer's discount and immediate investor equity gain. Retaining both columns satisfies both Milestone 1 DDL and Milestone 3 analytical query templates without schema divergence.

## 6. Referential Integrity & Foreign Key Orphan Checks

| Child FK | Parent Table | Orphan Count | Verification Status |
|---|---|---|---|
| `property.development_id` | `development.development_id` | **0** | PASSED (0 Orphans) |
| `property.location_id` | `location.location_id` | **0** | PASSED (0 Orphans) |
| `property.property_type_id` | `property_type.property_type_id` | **0** | PASSED (0 Orphans) |
| `property_amenity.property_id` | `property.property_id` | **0** | PASSED (0 Orphans) |
| `property_amenity.amenity_id` | `amenity.amenity_id` | **0** | PASSED (0 Orphans) |
| `user_focus_area.user_id` | `app_user.user_id` | **0** | PASSED (0 Orphans) |
| `user_focus_area.location_id` | `location.location_id` | **0** | PASSED (0 Orphans) |
| `review.user_id` | `app_user.user_id` | **0** | PASSED (0 Orphans) |
| `review.development_id` | `development.development_id` | **0** | PASSED (0 Orphans) |

## 7. Natural Key Uniqueness Checks

- Duplicate `property.source_listing_id`: **0** (PASSED - zero duplicates)
- Duplicate `developer.name`: **0** (PASSED - zero duplicates)

## 8. Metric Ranges & Value Distributions

| Metric | Minimum | Average | Maximum |
|---|---|---|---|
| **Price (EGP)** | 6,700.00 | 11,310,023.42 | 500,000,050.00 |
| **Area (sqm)** | 5.00 | 135.71 | 42,711.80 |
| **Price per sqm (EGP)** | 58.26 | 94,946.13 | 6,493,507.14 |
| **Down Payment (EGP)** | 450.00 | 2,979,643.31 | 55,074,400.00 |
| **Bedrooms Count** | 0.00 | 2.43 | 20.00 |
| **Contract Year** | 2,017.00 | 2,024.44 | 2,026.00 |

## 9. Character Set & Encoding Verification

- Database Connection Charset: `utf8mb4`
- Sample Arabic string retrieved from DB: `القاهرة`
- Status: **PASSED (Arabic text round-trips with full fidelity)**
