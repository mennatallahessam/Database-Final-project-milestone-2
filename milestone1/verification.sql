-- =============================================================================
-- CSCE 2501 – Fundamentals of Database Systems – Fall 2026
-- Milestone 1: Verification Script (verification.sql)
-- Validates: Schema constraints, transactional integrity, and queries Q1-Q10
-- Transaction is rolled back at the end, leaving the database completely empty.
-- =============================================================================

USE resale_properties;

START TRANSACTION;

-- =============================================================================
-- STEP 1: POPULATE SAMPLE DATA
-- =============================================================================

-- 1. Insert 2 Developers
INSERT INTO developer (developer_id, name, slug) VALUES
(1, 'La Vista Developments', 'la-vista'),
(2, 'Palm Hills Developments', 'palm-hills');

-- 2. Insert 3 Locations in a Mini-Hierarchy (Governorate -> City -> Area)
-- 101: Cairo (Governorate)
-- 102: New Cairo (City, child of Cairo)
-- 103: 5th Settlement (Area, child of New Cairo)
INSERT INTO location (location_id, parent_location_id, name, location_type, latitude, longitude) VALUES
(101, NULL, 'Cairo', 'governorate', 30.044420, 31.235712),
(102, 101, 'New Cairo', 'city', 30.026400, 31.491300),
(103, 102, '5th Settlement', 'area', 30.007400, 31.428500);

-- 3. Insert 2 Developments
INSERT INTO development (development_id, developer_id, location_id, name, latitude, longitude, source_url) VALUES
(201, 1, 103, 'Patio Vida', 30.012500, 31.432000, 'https://aqarexit.com/en/projects/patio-vida'),
(202, 2, 103, 'Palm Hills New Cairo', 30.018900, 31.450100, 'https://aqarexit.com/en/projects/palm-hills-nc');

-- 4. Insert 3 Property Types
INSERT INTO property_type (property_type_id, name) VALUES
(1, 'Apartment'),
(2, 'Villa'),
(3, 'Townhouse');

-- 5. Insert 2 Payment Methods
INSERT INTO payment_method (payment_method_id, name) VALUES
(1, 'Cash'),
(2, 'Installments');

-- 6. Insert 5 Amenities
INSERT INTO amenity (amenity_id, name) VALUES
(1, 'Swimming Pool'),
(2, 'Elevator'),
(3, 'Garage'),
(4, '24/7 Security'),
(5, 'Private Garden');

-- 7. Insert 4 Properties (Property #4 has development_id = NULL for standalone testing)
INSERT INTO property (
    property_id, source_listing_id, source_url, title, description,
    development_id, location_id, property_type_id, payment_method_id,
    area_sqm, bedrooms, bathrooms, price, market_price, down_payment,
    installment_amount, installment_frequency, installment_years, remaining_balance,
    gain_over_market_value, gain_percentage, discount_over_market_price,
    contract_year, delivery_year, currency
) VALUES
(501, 'OPP-001-AQA', 'https://aqarexit.com/en/buy/opportunity/opp-001', 'Prime Lake View Apartment', 'Luxury apartment in Patio Vida',
 201, 103, 1, 2, 176.00, 4, 3, 3600000.00, 5500000.00, 3600000.00, 350000.00, 'Quarterly', 6.0, 9340000.00, 1900000.00, 34.55, 1900000.00, 2021, 2026, 'EGP'),

(502, 'OPP-002-AQA', 'https://aqarexit.com/en/buy/opportunity/opp-002', 'Standalone Villa with Garden', 'Corner villa in Palm Hills',
 202, 103, 2, 2, 320.00, 5, 5, 12500000.00, 16000000.00, 6000000.00, 650000.00, 'Quarterly', 4.0, 6500000.00, 3500000.00, 21.88, 3500000.00, 2020, 2025, 'EGP'),

(503, 'OPP-003-AQA', 'https://aqarexit.com/en/buy/opportunity/opp-003', 'Modern Townhouse', 'Spacious family townhouse in Patio Vida',
 201, 103, 3, 2, 240.00, 3, 3, 8200000.00, 10000000.00, 4000000.00, 420000.00, 'Quarterly', 5.0, 4200000.00, 1800000.00, 18.00, 1800000.00, 2022, 2027, 'EGP'),

(504, 'OPP-004-AQA', 'https://aqarexit.com/en/buy/opportunity/opp-004', 'Standalone Private Apartment', 'Independent residential building apartment',
 NULL, 103, 1, 1, 150.00, 3, 2, 2800000.00, 3200000.00, 2800000.00, 0.00, 'Cash', 0.0, 0.00, 400000.00, 12.50, 400000.00, 2019, 2023, 'EGP');

-- 8. Link Amenities to Properties (M:N)
-- Property 501 has amenities 1, 2, 3, 4 (Pool, Elevator, Garage, Security)
-- Property 502 has amenities 1, 3, 4, 5 (Pool, Garage, Security, Garden)
-- Property 503 has amenities 1, 4 (Pool, Security)
-- Property 504 has amenities 2, 3 (Elevator, Garage)
INSERT INTO property_amenity (property_id, amenity_id) VALUES
(501, 1), (501, 2), (501, 3), (501, 4),
(502, 1), (502, 3), (502, 4), (502, 5),
(503, 1), (503, 4),
(504, 2), (504, 3);

-- 9. Insert 3 Users
INSERT INTO app_user (user_id, username, email, gender, birthdate) VALUES
(1, 'ahmed_hassan', 'ahmed.hassan@example.com', 'male', '1988-05-14'),
(2, 'nour_el_din', 'nour.eldin@example.com', 'female', '1995-11-22'),
(3, 'omar_khalil', 'omar.khalil@example.com', 'male', '2001-02-10');

-- 10. Link Focus Areas to Users (M:N)
INSERT INTO user_focus_area (user_id, location_id) VALUES
(1, 102), -- Ahmed focuses on New Cairo
(1, 103), -- Ahmed focuses on 5th Settlement
(2, 103), -- Nour focuses on 5th Settlement
(3, 101); -- Omar focuses on Cairo

-- 11. Insert 4 Reviews
INSERT INTO review (review_id, user_id, development_id, rating, review_text) VALUES
(1, 1, 201, 9, 'Exceptional build quality and quiet environment in Patio Vida.'),
(2, 2, 201, 8, 'Great green landscapes, delivery was slightly delayed.'),
(3, 1, 202, 10, 'Outstanding community management and security at Palm Hills.'),
(4, 3, 202, 7, 'Good compound but maintenance fees are relatively high.');

-- Verify sample counts
SELECT 'DEVELOPER' AS entity, COUNT(*) AS count FROM developer
UNION ALL SELECT 'LOCATION', COUNT(*) FROM location
UNION ALL SELECT 'DEVELOPMENT', COUNT(*) FROM development
UNION ALL SELECT 'PROPERTY_TYPE', COUNT(*) FROM property_type
UNION ALL SELECT 'PAYMENT_METHOD', COUNT(*) FROM payment_method
UNION ALL SELECT 'AMENITY', COUNT(*) FROM amenity
UNION ALL SELECT 'PROPERTY', COUNT(*) FROM property
UNION ALL SELECT 'PROPERTY_AMENITY', COUNT(*) FROM property_amenity
UNION ALL SELECT 'APP_USER', COUNT(*) FROM app_user
UNION ALL SELECT 'USER_FOCUS_AREA', COUNT(*) FROM user_focus_area
UNION ALL SELECT 'REVIEW', COUNT(*) FROM review;

-- =============================================================================
-- STEP 2: CONSTRAINT VIOLATIONS TESTS (PROOFS OF REJECTION)
-- Each violation is documented with its expected error code.
-- =============================================================================

-- TEST C1: Reject review rating 0 (Expected: Check constraint 'ck_review_rating' is violated)
-- INSERT INTO review (user_id, development_id, rating, review_text) VALUES (1, 201, 0, 'Invalid rating');

-- TEST C2: Reject review rating 11 (Expected: Check constraint 'ck_review_rating' is violated)
-- INSERT INTO review (user_id, development_id, rating, review_text) VALUES (1, 201, 11, 'Invalid rating');

-- TEST C3: Reject duplicate email in app_user (Expected: Duplicate entry for key 'uq_app_user_email')
-- INSERT INTO app_user (username, email, birthdate) VALUES ('another_user', 'ahmed.hassan@example.com', '1990-01-01');

-- TEST C4: Reject duplicate username in app_user (Expected: Duplicate entry for key 'uq_app_user_username')
-- INSERT INTO app_user (username, email, birthdate) VALUES ('ahmed_hassan', 'unique.email@example.com', '1990-01-01');

-- TEST C5: Reject non-existent property_type_id (Expected: Foreign key constraint fails)
-- INSERT INTO property (source_listing_id, source_url, location_id, property_type_id, area_sqm, price)
-- VALUES ('OPP-BAD-FK', 'https://example.com', 103, 9999, 100, 1000000);

-- TEST C6: Reject duplicate source_listing_id (Expected: Duplicate entry for key 'uq_property_source_listing_id')
-- INSERT INTO property (source_listing_id, source_url, location_id, property_type_id, area_sqm, price)
-- VALUES ('OPP-001-AQA', 'https://example.com/dup', 103, 1, 120, 2000000);

-- TEST C7: Reject negative price (Expected: Check constraint 'ck_property_price' is violated)
-- INSERT INTO property (source_listing_id, source_url, location_id, property_type_id, area_sqm, price)
-- VALUES ('OPP-NEG-PRICE', 'https://example.com', 103, 1, 100, -50000);

-- TEST C8: Reject birthdate in the future (Expected: Check constraint 'ck_app_user_birthdate' is violated)
-- INSERT INTO app_user (username, email, birthdate) VALUES ('future_user', 'future@example.com', '2099-01-01');

-- =============================================================================
-- STEP 3: MILESTONE III FUNCTIONAL QUERIES (Q1 to Q10)
-- Demonstrates schema answers every required analytical query.
-- =============================================================================

-- Q1: Register a new user
INSERT INTO app_user (user_id, username, email, gender, birthdate)
VALUES (99, 'new_investor', 'new.investor@example.com', 'female', '1992-08-15');
SELECT * FROM v_user_profile WHERE user_id = 99;

-- Q2: Add a new user review on a project
INSERT INTO review (review_id, user_id, development_id, rating, review_text)
VALUES (99, 99, 201, 9, 'Recently inspected the site, looks very promising.');
SELECT * FROM review WHERE review_id = 99;

-- Q3: View existing reviews of a project (ordered by creation date)
SELECT 
    r.review_id,
    u.username,
    r.rating,
    r.review_text,
    r.created_at
FROM review r
JOIN app_user u ON r.user_id = u.user_id
WHERE r.development_id = 201
ORDER BY r.created_at DESC;

-- Q4: Top 10 projects with highest resale inventory, resale amount, and highest gain over market value, by property type
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

-- Q5: Location of a given development, along with average price per sqm and number of listings for each unit type
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
WHERE dev.development_id = 201
GROUP BY dev.name, loc.name, pt.name;

-- Q6: All properties in a certain area, along with average price per sqm for each unit type
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
WHERE p.location_id = 103;

-- Q7: All properties in a certain area within a price range, with a given set of amenities (Relational Division)
-- Condition: In Area 103, Price between 3M and 10M, featuring Swimming Pool (ID 1) AND 24/7 Security (ID 4)
SELECT 
    p.property_id,
    p.source_listing_id,
    p.title,
    p.price,
    loc.name AS area_name
FROM property p
JOIN location loc ON p.location_id = loc.location_id
JOIN property_amenity pa ON p.property_id = pa.property_id
WHERE p.location_id = 103
  AND p.price BETWEEN 3000000.00 AND 10000000.00
  AND pa.amenity_id IN (1, 4) -- 1: Swimming Pool, 4: 24/7 Security
GROUP BY p.property_id, p.source_listing_id, p.title, p.price, loc.name
HAVING COUNT(DISTINCT pa.amenity_id) = 2; -- Exactly matches both required amenities

-- Q8: Top 5 developers by amount of resale listings, along with avg price/sqm, avg down payment, and gain over market value
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

-- Q9: All properties by area, property type, and contract year
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
ORDER BY loc.name, pt.name, p.contract_year DESC;

-- Q10: Avg installment price, avg down payment, count, avg discount over market price, avg age of contract year, avg market price
-- by area and development project
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
GROUP BY loc.name, dev.name;

-- =============================================================================
-- STEP 4: CLEAN ROLLBACK AND FINAL PURITY CHECK
-- =============================================================================
ROLLBACK;

-- Verify all tables have exactly 0 rows after rollback
SELECT 'developer' AS tbl, COUNT(*) AS row_count FROM developer
UNION ALL SELECT 'location', COUNT(*) FROM location
UNION ALL SELECT 'development', COUNT(*) FROM development
UNION ALL SELECT 'property_type', COUNT(*) FROM property_type
UNION ALL SELECT 'payment_method', COUNT(*) FROM payment_method
UNION ALL SELECT 'amenity', COUNT(*) FROM amenity
UNION ALL SELECT 'property', COUNT(*) FROM property
UNION ALL SELECT 'property_amenity', COUNT(*) FROM property_amenity
UNION ALL SELECT 'app_user', COUNT(*) FROM app_user
UNION ALL SELECT 'user_focus_area', COUNT(*) FROM user_focus_area
UNION ALL SELECT 'review', COUNT(*) FROM review;

