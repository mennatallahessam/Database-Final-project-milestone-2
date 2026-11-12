-- =============================================================================
-- CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties
-- Milestone III: Performance Optimization & Query Acceleration Indexes
-- =============================================================================

-- Index 1: Location hierarchy recursive CTE acceleration
-- Optimizes recursive joins on parent_location_id across the location tree (F05, F06, F07, F09, F10)
CREATE INDEX IF NOT EXISTS idx_location_parent_id ON location (parent_location_id, location_id);

-- Index 2: Developer & Development joining index
-- Speeds up F04, F05, F08, F10 when aggregating properties by developer and development
CREATE INDEX IF NOT EXISTS idx_development_developer_loc ON development (developer_id, location_id);

-- Index 3: Review fast duplicate check & user reviews lookup
-- Speeds up F02 and user review lookups
CREATE INDEX IF NOT EXISTS idx_review_user_dev ON review (user_id, development_id);

-- Index 4: Property composite index for property_type aggregation
-- Accelerates F04, F08 when filtering by property_type_id and calculating price / area
CREATE INDEX IF NOT EXISTS idx_property_type_dev_price ON property (property_type_id, development_id, price);
