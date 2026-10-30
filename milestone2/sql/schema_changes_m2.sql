-- =============================================================================
-- CSCE 2501 – Fundamentals of Database Systems – Milestone 2
-- Migration / Schema Adjustments File: schema_changes_m2.sql
-- =============================================================================

-- Status: NO BREAKING MIGRATIONS REQUIRED.
-- The Milestone 1 schema was designed forward-compatible with the real AqarExit
-- data structure, accommodating:
-- 1. All financial fields (price, market_price, down_payment, installment_amount, remaining_balance, gain/discount).
-- 2. Physical unit fields (area_sqm, bedrooms, bathrooms, delivery_year, contract_year).
-- 3. Lookup entity structures for property_type, payment_method, amenity, developer, and location hierarchy.
-- 4. Crawler idempotency via uq_property_source_listing_id.
--
-- All crawled attributes from AqarExit map directly to existing columns in milestone1/schema.sql.

