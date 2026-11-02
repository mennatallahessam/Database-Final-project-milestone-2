-- =============================================================================
-- CSCE 2501 – Fundamentals of Database Systems – Milestone 2
-- Migration / Schema Adjustments File: schema_changes_m2.sql
-- =============================================================================
--
-- DECISION DOCUMENTATION:
-- -----------------------------------------------------------------------------
-- 1. Language Policy & Bilingual Entity Normalization (Issue 3):
--    - Decision: Add `name_en` and `name_ar` columns to `location` and `property_type`.
--      The existing `name` column is retained as the canonical English display name
--      to preserve full backward-compatibility with all Milestone 1 schema constraints
--      and Milestone 3 analytical query templates.
--    - Alternatives:
--      (a) Replace `name` with `name_en` and `name_ar` (breaking change for Milestone 1 queries).
--      (b) Store only English names in `name` and drop original Arabic (loses real crawled text).
--    - Why: Keeping `name` (English canonical) alongside `name_en` and `name_ar` ensures:
--      (1) Zero entity duplication between Arabic and English variants (e.g. "محل" and "Shop").
--      (2) Full compatibility with Milestone 1 queries using `WHERE name = '...'`.
--      (3) Complete fidelity to the bilingual Arabic/English data extracted from AqarExit.
--
-- 2. Financial Columns: Gain over Market Value vs. Discount over Market Price (Issue 6):
--    - Decision: Retain both `gain_over_market_value` and `discount_over_market_price`
--      in the `property` table.
--    - Alternatives:
--      (a) Drop one column and create a generated virtual/stored column.
--      (b) Keep only one column and update queries.
--    - Why: In Egyptian real-estate resale economics (and AqarExit data), the numerical
--      difference between market price and asking price represents both the buyer's
--      "discount" and the investor's "equity gain". Milestone 1 schema explicitly includes
--      both columns, and Milestone 3 queries (Q4, Q8, Q10) refer to them interchangeably.
--      Keeping both stored guarantees full compliance without schema divergence.
-- =============================================================================

USE resale_properties;

-- 1. Enhance property_type with bilingual support
ALTER TABLE property_type
    ADD COLUMN name_en VARCHAR(100) NULL AFTER name,
    ADD COLUMN name_ar VARCHAR(100) NULL AFTER name_en;

-- 2. Enhance location with bilingual support
ALTER TABLE location
    ADD COLUMN name_en VARCHAR(150) NULL AFTER name,
    ADD COLUMN name_ar VARCHAR(150) NULL AFTER name_en;
