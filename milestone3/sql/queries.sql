-- =============================================================================
-- CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties
-- Milestone III: Application Layer Queries (F01 to F10)
-- Character Set: utf8mb4, Engine: InnoDB
-- Tested on MySQL 8.0+
-- =============================================================================

-- -----------------------------------------------------------------------------
-- F01: Register a user
-- Step 1: Check existing username/email to present user-friendly error
-- -----------------------------------------------------------------------------
-- [F01_CHECK_EXISTING]
SELECT user_id, username, email 
FROM app_user 
WHERE email = %s OR username = %s 
LIMIT 1;

-- Step 2: Insert new app_user (age is derived dynamically from birthdate in v_user_profile)
-- [F01_INSERT_USER]
INSERT INTO app_user (username, email, gender, birthdate, registered_at)
VALUES (%s, %s, %s, %s, NOW());

-- Step 3: Insert user focus areas (executed in the same transaction)
-- [F01_INSERT_FOCUS_AREA]
INSERT INTO user_focus_area (user_id, location_id)
VALUES (%s, %s);

-- Step 4: Verify registration and fetch user profile with derived age
-- [F01_GET_PROFILE]
SELECT user_id, username, email, gender, birthdate, age, registered_at
FROM v_user_profile
WHERE user_id = %s;


-- -----------------------------------------------------------------------------
-- F02: Add a new user review on a project (development)
-- Step 1: Check for existing review by this user on this development
-- -----------------------------------------------------------------------------
-- [F02_CHECK_EXISTING]
SELECT review_id, rating, review_text 
FROM review 
WHERE user_id = %s AND development_id = %s;

-- Step 2: Insert the review (rating checked between 1 and 10 by table constraint)
-- [F02_INSERT_REVIEW]
INSERT INTO review (user_id, development_id, rating, review_text, created_at)
VALUES (%s, %s, %s, %s, NOW());


-- -----------------------------------------------------------------------------
-- F03: View existing reviews of a project
-- Summary header query
-- -----------------------------------------------------------------------------
-- [F03_GET_DEV_SUMMARY]
SELECT 
    d.development_id,
    d.name AS development_name,
    dev.developer_id,
    dev.name AS developer_name,
    loc.location_id,
    loc.name AS location_name,
    loc.name_en AS location_name_en,
    loc.name_ar AS location_name_ar,
    COUNT(r.review_id) AS total_reviews,
    ROUND(AVG(r.rating), 1) AS avg_rating
FROM development d
LEFT JOIN developer dev ON d.developer_id = dev.developer_id
LEFT JOIN location loc ON d.location_id = loc.location_id
LEFT JOIN review r ON d.development_id = r.development_id
WHERE d.development_id = %s
GROUP BY d.development_id, dev.developer_id, dev.name, loc.location_id, loc.name, loc.name_en, loc.name_ar;

-- Paginated list of reviews for the development
-- [F03_GET_REVIEWS_LIST]
SELECT 
    r.review_id,
    r.rating,
    r.review_text,
    r.created_at,
    u.user_id,
    u.username
FROM review r
JOIN app_user u ON r.user_id = u.user_id
WHERE r.development_id = %s
ORDER BY r.created_at DESC
LIMIT %s OFFSET %s;


-- -----------------------------------------------------------------------------
-- F04: Top 10 projects by resale inventory, resale amount, and gain over market value
-- Ranked for a chosen property type
-- -----------------------------------------------------------------------------

-- Tab 1: Order by resale inventory (listing count)
-- [F04_TOP_INVENTORY]
SELECT 
    d.development_id,
    d.name AS development_name,
    dev.developer_id,
    dev.name AS developer_name,
    COUNT(p.property_id) AS resale_inventory,
    SUM(p.price) AS total_resale_amount,
    ROUND(AVG(p.price / p.area_sqm), 2) AS avg_price_sqm,
    SUM(p.gain_over_market_value) AS total_gain,
    ROUND(AVG(p.gain_over_market_value), 2) AS avg_gain
FROM property p
JOIN development d ON p.development_id = d.development_id
LEFT JOIN developer dev ON d.developer_id = dev.developer_id
WHERE p.property_type_id = %s
  AND p.price > 0 AND p.area_sqm > 0
GROUP BY d.development_id, d.name, dev.developer_id, dev.name
ORDER BY resale_inventory DESC, total_resale_amount DESC, d.name ASC
LIMIT 10;

-- Tab 2: Order by resale amount (total price)
-- [F04_TOP_AMOUNT]
SELECT 
    d.development_id,
    d.name AS development_name,
    dev.developer_id,
    dev.name AS developer_name,
    COUNT(p.property_id) AS resale_inventory,
    SUM(p.price) AS total_resale_amount,
    ROUND(AVG(p.price / p.area_sqm), 2) AS avg_price_sqm,
    SUM(p.gain_over_market_value) AS total_gain,
    ROUND(AVG(p.gain_over_market_value), 2) AS avg_gain
FROM property p
JOIN development d ON p.development_id = d.development_id
LEFT JOIN developer dev ON d.developer_id = dev.developer_id
WHERE p.property_type_id = %s
  AND p.price > 0 AND p.area_sqm > 0
GROUP BY d.development_id, d.name, dev.developer_id, dev.name
ORDER BY total_resale_amount DESC, resale_inventory DESC, d.name ASC
LIMIT 10;

-- Tab 3: Order by average gain over market value with minimum-listings threshold
-- [F04_TOP_GAIN]
SELECT 
    d.development_id,
    d.name AS development_name,
    dev.developer_id,
    dev.name AS developer_name,
    COUNT(p.property_id) AS resale_inventory,
    SUM(p.price) AS total_resale_amount,
    ROUND(AVG(p.price / p.area_sqm), 2) AS avg_price_sqm,
    SUM(p.gain_over_market_value) AS total_gain,
    ROUND(AVG(p.gain_over_market_value), 2) AS avg_gain
FROM property p
JOIN development d ON p.development_id = d.development_id
LEFT JOIN developer dev ON d.developer_id = dev.developer_id
WHERE p.property_type_id = %s
  AND p.price > 0 AND p.area_sqm > 0
GROUP BY d.development_id, d.name, dev.developer_id, dev.name
HAVING COUNT(p.property_id) >= %s
ORDER BY avg_gain DESC, total_gain DESC, d.name ASC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- F05: Location of a given development + avg price per sqm + listings per unit type
-- -----------------------------------------------------------------------------
-- [F05_GET_DEV_DETAILS]
SELECT 
    d.development_id,
    d.name AS development_name,
    d.latitude,
    d.longitude,
    d.source_url,
    dev.developer_id,
    dev.name AS developer_name,
    loc.location_id,
    loc.name AS location_name,
    loc.name_en AS location_name_en,
    loc.name_ar AS location_name_ar,
    loc.location_type,
    loc.latitude AS loc_latitude,
    loc.longitude AS loc_longitude
FROM development d
LEFT JOIN developer dev ON d.developer_id = dev.developer_id
LEFT JOIN location loc ON d.location_id = loc.location_id
WHERE d.development_id = %s;

-- Breakdown by property type + summary total row
-- [F05_GET_TYPE_BREAKDOWN]
SELECT 
    pt.property_type_id,
    pt.name AS property_type_name,
    pt.name_en AS property_type_en,
    pt.name_ar AS property_type_ar,
    COUNT(p.property_id) AS listing_count,
    ROUND(AVG(p.price / p.area_sqm), 2) AS avg_price_sqm,
    MIN(p.price) AS min_price,
    MAX(p.price) AS max_price,
    ROUND(AVG(p.price), 2) AS avg_price
FROM property p
JOIN property_type pt ON p.property_type_id = pt.property_type_id
WHERE p.development_id = %s
  AND p.price > 0 AND p.area_sqm > 0
GROUP BY pt.property_type_id, pt.name, pt.name_en, pt.name_ar
ORDER BY listing_count DESC;


-- -----------------------------------------------------------------------------
-- F06: All properties in a certain area (and descendants), with average price/sqm by unit type
-- Uses Recursive CTE to gather all sub-areas, cities, and governorates
-- -----------------------------------------------------------------------------
-- [F06_GET_SUMMARY]
WITH RECURSIVE area_tree AS (
    SELECT location_id FROM location WHERE location_id = %s
    UNION ALL
    SELECT l.location_id FROM location l INNER JOIN area_tree t ON l.parent_location_id = t.location_id
)
SELECT 
    pt.property_type_id,
    pt.name AS property_type_name,
    pt.name_en AS property_type_en,
    pt.name_ar AS property_type_ar,
    COUNT(p.property_id) AS listing_count,
    ROUND(AVG(p.price / p.area_sqm), 2) AS avg_price_sqm,
    ROUND(AVG(p.price), 2) AS avg_price
FROM property p
JOIN area_tree a ON p.location_id = a.location_id
JOIN property_type pt ON p.property_type_id = pt.property_type_id
WHERE p.price > 0 AND p.area_sqm > 0
GROUP BY pt.property_type_id, pt.name, pt.name_en, pt.name_ar
ORDER BY listing_count DESC;

-- Paginated properties list in the selected area tree
-- [F06_GET_PROPERTIES_PAGINATED]
WITH RECURSIVE area_tree AS (
    SELECT location_id FROM location WHERE location_id = %s
    UNION ALL
    SELECT l.location_id FROM location l INNER JOIN area_tree t ON l.parent_location_id = t.location_id
)
SELECT 
    p.property_id,
    p.source_listing_id,
    p.title,
    p.source_url,
    pt.name AS property_type_name,
    dev.name AS development_name,
    loc.name AS location_name,
    p.area_sqm,
    p.bedrooms,
    p.bathrooms,
    p.price,
    ROUND(p.price / p.area_sqm, 2) AS price_per_sqm
FROM property p
JOIN area_tree a ON p.location_id = a.location_id
JOIN property_type pt ON p.property_type_id = pt.property_type_id
LEFT JOIN development dev ON p.development_id = dev.development_id
JOIN location loc ON p.location_id = loc.location_id
WHERE p.price > 0 AND p.area_sqm > 0
ORDER BY p.price ASC
LIMIT %s OFFSET %s;


-- -----------------------------------------------------------------------------
-- F07: Properties in a certain area, price range, with given set of amenities
-- Relational division: HAVING COUNT(DISTINCT pa.amenity_id) = N for ALL amenities
-- -----------------------------------------------------------------------------
-- [F07_FILTER_PROPERTIES_ALL]
WITH RECURSIVE area_tree AS (
    SELECT location_id FROM location WHERE location_id = %s
    UNION ALL
    SELECT l.location_id FROM location l INNER JOIN area_tree t ON l.parent_location_id = t.location_id
),
matching_amenities AS (
    SELECT pa.property_id
    FROM property_amenity pa
    WHERE pa.amenity_id IN (/* AMENITY_IDS_PLACEHOLDER */)
    GROUP BY pa.property_id
    HAVING COUNT(DISTINCT pa.amenity_id) = %s
)
SELECT 
    p.property_id,
    p.source_listing_id,
    p.title,
    p.source_url,
    pt.name AS property_type_name,
    dev.name AS development_name,
    loc.name AS location_name,
    p.area_sqm,
    p.bedrooms,
    p.bathrooms,
    p.price,
    ROUND(p.price / p.area_sqm, 2) AS price_per_sqm,
    GROUP_CONCAT(am.name ORDER BY am.name SEPARATOR ', ') AS amenities_list
FROM property p
JOIN area_tree a ON p.location_id = a.location_id
JOIN matching_amenities ma ON p.property_id = ma.property_id
JOIN property_type pt ON p.property_type_id = pt.property_type_id
LEFT JOIN development dev ON p.development_id = dev.development_id
JOIN location loc ON p.location_id = loc.location_id
LEFT JOIN property_amenity pa ON p.property_id = pa.property_id
LEFT JOIN amenity am ON pa.amenity_id = am.amenity_id
WHERE (%s IS NULL OR p.price >= %s)
  AND (%s IS NULL OR p.price <= %s)
  AND p.price > 0 AND p.area_sqm > 0
GROUP BY p.property_id, p.source_listing_id, p.title, p.source_url, pt.name, dev.name, loc.name, p.area_sqm, p.bedrooms, p.bathrooms, p.price
ORDER BY p.price ASC
LIMIT %s OFFSET %s;


-- -----------------------------------------------------------------------------
-- F08: Top 5 developers by number of resale listings
-- -----------------------------------------------------------------------------
-- [F08_TOP_DEVELOPERS]
SELECT 
    dev.developer_id,
    dev.name AS developer_name,
    COUNT(p.property_id) AS total_listings,
    ROUND(AVG(p.price / p.area_sqm), 2) AS avg_price_sqm,
    ROUND(AVG(p.down_payment), 2) AS avg_down_payment,
    ROUND(AVG(CASE WHEN p.price > 0 AND p.down_payment IS NOT NULL 
                   THEN (p.down_payment / p.price) * 100 ELSE NULL END), 2) AS avg_down_payment_pct,
    ROUND(AVG(p.gain_over_market_value), 2) AS avg_gain,
    SUM(p.gain_over_market_value) AS total_gain
FROM property p
JOIN development d ON p.development_id = d.development_id
JOIN developer dev ON d.developer_id = dev.developer_id
WHERE (%s IS NULL OR p.property_type_id = %s)
  AND p.price > 0 AND p.area_sqm > 0
GROUP BY dev.developer_id, dev.name
ORDER BY total_listings DESC, dev.name ASC
LIMIT 5;


-- -----------------------------------------------------------------------------
-- F09: All properties by area, property type, and contract year
-- -----------------------------------------------------------------------------
-- [F09_GROUPED_SUMMARY]
WITH RECURSIVE area_tree AS (
    SELECT location_id FROM location WHERE location_id = %s
    UNION ALL
    SELECT l.location_id FROM location l INNER JOIN area_tree t ON l.parent_location_id = t.location_id
)
SELECT 
    loc.location_id,
    loc.name AS area_name,
    loc.name_en AS area_name_en,
    loc.name_ar AS area_name_ar,
    pt.property_type_id,
    pt.name AS property_type_name,
    p.contract_year,
    COUNT(p.property_id) AS property_count,
    ROUND(AVG(p.price), 2) AS avg_price,
    ROUND(AVG(p.price / p.area_sqm), 2) AS avg_price_sqm
FROM property p
JOIN area_tree a ON p.location_id = a.location_id
JOIN location loc ON p.location_id = loc.location_id
JOIN property_type pt ON p.property_type_id = pt.property_type_id
WHERE (%s IS NULL OR p.property_type_id = %s)
  AND (%s IS NULL OR p.contract_year = %s)
  AND p.contract_year IS NOT NULL
GROUP BY loc.location_id, loc.name, loc.name_en, loc.name_ar, pt.property_type_id, pt.name, p.contract_year
ORDER BY property_count DESC;


-- -----------------------------------------------------------------------------
-- F10: Averages by area and development project
-- (installment, down payment, property count, discount, age of contract, market price)
-- -----------------------------------------------------------------------------
-- [F10_AREA_DEV_AVERAGES]
SELECT 
    loc.location_id,
    loc.name AS area_name,
    loc.name_en AS area_name_en,
    loc.name_ar AS area_name_ar,
    d.development_id,
    d.name AS development_name,
    COUNT(p.property_id) AS property_count,
    ROUND(AVG(p.installment_amount), 2) AS avg_installment,
    COUNT(p.installment_amount) AS installment_count,
    ROUND(AVG(p.down_payment), 2) AS avg_down_payment,
    COUNT(p.down_payment) AS down_payment_count,
    ROUND(AVG(p.discount_over_market_price), 2) AS avg_discount,
    COUNT(p.discount_over_market_price) AS discount_count,
    ROUND(AVG(YEAR(CURDATE()) - p.contract_year), 1) AS avg_contract_age,
    COUNT(p.contract_year) AS contract_year_count,
    ROUND(AVG(p.market_price), 2) AS avg_market_price,
    COUNT(p.market_price) AS market_price_count
FROM property p
JOIN development d ON p.development_id = d.development_id
JOIN location loc ON p.location_id = loc.location_id
WHERE (%s IS NULL OR loc.location_id = %s)
GROUP BY loc.location_id, loc.name, loc.name_en, loc.name_ar, d.development_id, d.name
HAVING COUNT(p.property_id) >= %s
ORDER BY property_count DESC
LIMIT %s OFFSET %s;
