-- =============================================================================
-- CSCE 2501 – Fundamentals of Database Systems – Fall 2026
-- Milestone 2 Validation: Milestone III Analytical Smoke Queries
-- Executed against the populated MySQL database (crawled data + seeded users)
-- =============================================================================

USE resale_properties;

-- -----------------------------------------------------------------------------
-- Query 1: Top 10 projects with highest resale inventory, resale amount, and
-- highest gain over market value, by property type
-- -----------------------------------------------------------------------------
SELECT 
    pt.name AS property_type,
    dev.name AS development_name,
    COUNT(p.property_id) AS resale_inventory,
    SUM(p.price) AS total_resale_amount,
    AVG(p.gain_over_market_value) AS avg_gain_over_market_value
FROM property p
JOIN property_type pt ON p.property_type_id = pt.property_type_id
JOIN development dev ON p.development_id = dev.development_id
GROUP BY pt.name, dev.name
ORDER BY pt.name, resale_inventory DESC, total_resale_amount DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Query 2: Location of a given development, along with average price per sqm
-- and number of listings for each unit type
-- -----------------------------------------------------------------------------
SELECT 
    dev.name AS development_name,
    loc.name AS development_location,
    pt.name AS unit_type,
    COUNT(p.property_id) AS listing_count,
    ROUND(AVG(p.price / p.area_sqm), 2) AS avg_price_per_sqm
FROM development dev
JOIN location loc ON dev.location_id = loc.location_id
LEFT JOIN property p ON dev.development_id = p.development_id
LEFT JOIN property_type pt ON p.property_type_id = pt.property_type_id
GROUP BY dev.name, loc.name, pt.name
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Query 3: All properties in a certain area, along with average price per sqm
-- for each unit type
-- -----------------------------------------------------------------------------
SELECT 
    loc.name AS area_name,
    pt.name AS unit_type,
    p.property_id,
    p.source_listing_id,
    p.price,
    p.area_sqm,
    ROUND(p.price / p.area_sqm, 2) AS property_price_per_sqm,
    ROUND(AVG(p.price / p.area_sqm) OVER(PARTITION BY pt.property_type_id), 2) AS area_avg_price_per_sqm_for_type
FROM property p
JOIN location loc ON p.location_id = loc.location_id
JOIN property_type pt ON p.property_type_id = pt.property_type_id
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Query 4: All properties in a certain area within a price range, with a given set of amenities
-- (Relational Division via GROUP BY ... HAVING COUNT(DISTINCT) = N)
-- -----------------------------------------------------------------------------
SELECT 
    p.property_id,
    p.source_listing_id,
    p.title,
    p.price,
    loc.name AS area_name
FROM property p
JOIN location loc ON p.location_id = loc.location_id
JOIN property_amenity pa ON p.property_id = pa.property_id
JOIN amenity a ON pa.amenity_id = a.amenity_id
WHERE p.price BETWEEN 1000000.00 AND 30000000.00
GROUP BY p.property_id, p.source_listing_id, p.title, p.price, loc.name
HAVING COUNT(DISTINCT pa.amenity_id) >= 2
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Query 5: Top 5 developers by amount of resale listings, along with avg price/sqm,
-- avg down payment, and gain over market value
-- -----------------------------------------------------------------------------
SELECT 
    d.developer_id,
    d.name AS developer_name,
    COUNT(p.property_id) AS resale_listing_count,
    ROUND(AVG(p.price / p.area_sqm), 2) AS avg_price_per_sqm,
    ROUND(AVG(p.down_payment), 2) AS avg_down_payment,
    ROUND(AVG(p.gain_over_market_value), 2) AS avg_gain_over_market_value
FROM developer d
JOIN development dev ON d.developer_id = dev.developer_id
JOIN property p ON dev.development_id = p.development_id
GROUP BY d.developer_id, d.name
ORDER BY resale_listing_count DESC, avg_gain_over_market_value DESC
LIMIT 5;

-- -----------------------------------------------------------------------------
-- Query 6: Properties by area, property type, and contract year
-- -----------------------------------------------------------------------------
SELECT 
    loc.name AS area_name,
    pt.name AS property_type,
    p.contract_year,
    p.property_id,
    p.source_listing_id,
    p.price,
    p.area_sqm
FROM property p
JOIN location loc ON p.location_id = loc.location_id
JOIN property_type pt ON p.property_type_id = pt.property_type_id
ORDER BY loc.name, pt.name, p.contract_year DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Query 7: Average installment price, avg down payment, count, avg discount over market price,
-- avg age of contract year, avg market price by area and development
-- -----------------------------------------------------------------------------
SELECT 
    loc.name AS area_name,
    COALESCE(dev.name, 'Standalone / No Development') AS development_name,
    COUNT(p.property_id) AS property_count,
    ROUND(AVG(p.installment_amount), 2) AS avg_installment_price,
    ROUND(AVG(p.down_payment), 2) AS avg_down_payment,
    ROUND(AVG(COALESCE(p.discount_over_market_price, p.market_price - p.price)), 2) AS avg_discount_over_market_price,
    ROUND(AVG(YEAR(CURDATE()) - p.contract_year), 1) AS avg_age_of_contract_year,
    ROUND(AVG(p.market_price), 2) AS avg_market_price
FROM property p
JOIN location loc ON p.location_id = loc.location_id
LEFT JOIN development dev ON p.development_id = dev.development_id
GROUP BY loc.name, dev.name
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Query 8: View existing reviews of a project (joining users and developments)
-- -----------------------------------------------------------------------------
SELECT 
    r.review_id,
    u.username,
    dev.name AS development_name,
    r.rating,
    r.review_text,
    r.created_at
FROM review r
JOIN app_user u ON r.user_id = u.user_id
JOIN development dev ON r.development_id = dev.development_id
ORDER BY r.created_at DESC
LIMIT 10;

