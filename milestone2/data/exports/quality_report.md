# Milestone 2: Data Quality & Ingestion Validation Report
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (Fall 2026)

---
## 1. Crawl & Ingestion Reconciliation Funnel

| Funnel Stage | Count | Notes |
|---|---|---|
| **1. Discovered Listings** | 9690 | Extracted from `sitemap.xml` & `/en/opportunities` |
| **2. Fetched Pages (Raw)** | 42 | Untouched HTML pages saved in `data/raw/` |
| **3. Parsed & Staged** | 42 | Structured JSONL records passing validation |
| **4. Quarantined (Rejected)** | 0 | Records failing business rules (quarantine log) |
| **5. Database Loaded** | 42 | Successfully loaded into MySQL `property` table |

## 2. Table Row Counts

| Table Name | Row Count | Classification |
|---|---|---|
| `developer` | **38** | Crawled Reference |
| `location` | **18** | Crawled Hierarchy |
| `development` | **41** | Crawled Projects |
| `property_type` | **6** | Lookup |
| `payment_method` | **1** | Lookup |
| `amenity` | **10** | Lookup |
| `property` | **42** | Core Crawled Listings |
| `property_amenity` | **174** | M:N Associative |
| `app_user` | **40** | Synthetic User Data |
| `user_focus_area` | **100** | M:N Associative |
| `review` | **120** | Synthetic Reviews |

## 3. Attribute Null Rates on `property` Table

| Column | Total Rows | Non-Null Rows | Null Rate (%) | Required by Schema? |
|---|---|---|---|---|
| `property_id` | 42 | 42 | 0.0% | YES (NOT NULL) |
| `source_listing_id` | 42 | 42 | 0.0% | YES (NOT NULL) |
| `source_url` | 42 | 42 | 0.0% | YES (NOT NULL) |
| `title` | 42 | 42 | 0.0% | NO (Nullable) |
| `description` | 42 | 42 | 0.0% | NO (Nullable) |
| `development_id` | 42 | 42 | 0.0% | NO (Nullable) |
| `location_id` | 42 | 42 | 0.0% | YES (NOT NULL) |
| `property_type_id` | 42 | 42 | 0.0% | YES (NOT NULL) |
| `payment_method_id` | 42 | 42 | 0.0% | NO (Nullable) |
| `area_sqm` | 42 | 42 | 0.0% | YES (NOT NULL) |
| `bedrooms` | 42 | 38 | 9.52% | NO (Nullable) |
| `bathrooms` | 42 | 6 | 85.71% | NO (Nullable) |
| `price` | 42 | 42 | 0.0% | YES (NOT NULL) |
| `market_price` | 42 | 42 | 0.0% | NO (Nullable) |
| `down_payment` | 42 | 42 | 0.0% | NO (Nullable) |
| `installment_amount` | 42 | 42 | 0.0% | NO (Nullable) |
| `installment_frequency` | 42 | 42 | 0.0% | NO (Nullable) |
| `installment_years` | 42 | 34 | 19.05% | NO (Nullable) |
| `remaining_balance` | 42 | 42 | 0.0% | NO (Nullable) |
| `gain_over_market_value` | 42 | 42 | 0.0% | NO (Nullable) |
| `gain_percentage` | 42 | 42 | 0.0% | NO (Nullable) |
| `discount_over_market_price` | 42 | 42 | 0.0% | NO (Nullable) |
| `contract_year` | 42 | 42 | 0.0% | NO (Nullable) |
| `delivery_year` | 42 | 36 | 14.29% | NO (Nullable) |
| `currency` | 42 | 42 | 0.0% | YES (NOT NULL) |
| `scraped_at` | 42 | 42 | 0.0% | YES (NOT NULL) |

## 4. Referential Integrity & Foreign Key Orphan Checks

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

## 5. Metric Ranges & Value Distributions

| Metric | Minimum | Average | Maximum |
|---|---|---|---|
| **Price (EGP)** | 2,291,527.00 | 8,742,054.31 | 20,000,000.00 |
| **Area (sqm)** | 12.50 | 114.76 | 260.00 |
| **Price per sqm (EGP)** | 20,460.06 | 104,593.68 | 416,666.67 |
| **Down Payment (EGP)** | 325,345.00 | 2,602,663.10 | 5,693,550.00 |
| **Bedrooms Count** | 1.00 | 2.21 | 4.00 |
| **Contract Year** | 2,023.00 | 2,024.43 | 2,026.00 |

## 6. Character Set & Encoding Verification

- Database Connection Charset: `utf8mb4`
- Sample Arabic string retrieved from DB: `6 أكتوبر`
- Status: **PASSED (Arabic text round-trips with full fidelity)**
