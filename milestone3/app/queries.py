"""
Milestone III Parameterized SQL Statements & Query Helpers
Contains all SQL query definitions for F01 to F10.
Every query uses strict parameterization (%s) to prevent SQL injection.
Dynamic identifiers (e.g. ORDER BY columns) are verified against strict hardcoded whitelists.
"""

# Allowed sort columns to prevent SQL injection
ALLOWED_SORT_COLUMNS = {
    "price": "p.price",
    "area_sqm": "p.area_sqm",
    "price_per_sqm": "(p.price / p.area_sqm)",
    "title": "p.title",
    "property_count": "COUNT(p.property_id)",
    "avg_installment": "AVG(p.installment_amount)",
    "avg_down_payment": "AVG(p.down_payment)",
    "avg_discount": "AVG(p.discount_over_market_price)",
    "avg_contract_age": "AVG(YEAR(CURDATE()) - p.contract_year)",
    "avg_market_price": "AVG(p.market_price)",
    "resale_inventory": "COUNT(p.property_id)",
    "total_resale_amount": "SUM(p.price)",
    "avg_gain": "AVG(p.gain_over_market_value)"
}

# -----------------------------------------------------------------------------
# Common Lookups & Cached Reference Queries
# -----------------------------------------------------------------------------
SQL_GET_PROPERTY_TYPES = """
SELECT property_type_id, name, name_en, name_ar 
FROM property_type 
ORDER BY name ASC;
"""

SQL_GET_AMENITIES = """
SELECT amenity_id, name 
FROM amenity 
ORDER BY name ASC;
"""

SQL_GET_LOCATIONS_TREE = """
SELECT location_id, parent_location_id, name, name_en, name_ar, location_type 
FROM location 
ORDER BY location_type, name ASC;
"""

SQL_GET_DISTINCT_CONTRACT_YEARS = """
SELECT DISTINCT contract_year 
FROM property 
WHERE contract_year IS NOT NULL 
ORDER BY contract_year DESC;
"""

SQL_SEARCH_DEVELOPMENTS = """
SELECT d.development_id, d.name, dev.name AS developer_name, loc.name AS location_name
FROM development d
LEFT JOIN developer dev ON d.developer_id = dev.developer_id
LEFT JOIN location loc ON d.location_id = loc.location_id
WHERE d.name LIKE %s OR dev.name LIKE %s
ORDER BY d.name ASC
LIMIT %s;
"""

SQL_SEARCH_AREAS = """
SELECT location_id, name, name_en, name_ar, location_type
FROM location
WHERE name LIKE %s OR name_en LIKE %s OR name_ar LIKE %s
ORDER BY name ASC
LIMIT %s;
"""

# -----------------------------------------------------------------------------
# F01: Register a user
# -----------------------------------------------------------------------------
SQL_F01_CHECK_EXISTING = """
SELECT user_id, username, email 
FROM app_user 
WHERE email = %s OR username = %s 
LIMIT 1;
"""

SQL_F01_INSERT_USER = """
INSERT INTO app_user (username, email, gender, birthdate, registered_at)
VALUES (%s, %s, %s, %s, NOW());
"""

SQL_F01_INSERT_FOCUS_AREA = """
INSERT INTO user_focus_area (user_id, location_id)
VALUES (%s, %s);
"""

SQL_F01_GET_PROFILE = """
SELECT u.user_id, u.username, u.email, u.gender, u.birthdate, u.age, u.registered_at
FROM v_user_profile u
WHERE u.user_id = %s;
"""

SQL_F01_GET_USER_FOCUS_AREAS = """
SELECT l.location_id, l.name, l.name_en, l.name_ar, l.location_type
FROM user_focus_area ufa
JOIN location l ON ufa.location_id = l.location_id
WHERE ufa.user_id = %s;
"""

# -----------------------------------------------------------------------------
# F02: Add a new user review on a project
# -----------------------------------------------------------------------------
SQL_F02_CHECK_EXISTING_REVIEW = """
SELECT review_id, rating, review_text 
FROM review 
WHERE user_id = %s AND development_id = %s;
"""

SQL_F02_INSERT_REVIEW = """
INSERT INTO review (user_id, development_id, rating, review_text, created_at)
VALUES (%s, %s, %s, %s, NOW());
"""

# -----------------------------------------------------------------------------
# F03: View existing reviews of a project
# -----------------------------------------------------------------------------
SQL_F03_GET_DEV_SUMMARY = """
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
GROUP BY d.development_id, d.name, dev.developer_id, dev.name, loc.location_id, loc.name, loc.name_en, loc.name_ar;
"""

SQL_F03_GET_REVIEWS_LIST = """
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
"""

# -----------------------------------------------------------------------------
# F04: Top 10 projects by resale inventory, amount, gain by property type
# -----------------------------------------------------------------------------
SQL_F04_TOP_PROJECTS = """
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
  {outlier_filter}
GROUP BY d.development_id, d.name, dev.developer_id, dev.name
HAVING COUNT(p.property_id) >= %s
ORDER BY {order_by}
LIMIT 10;
"""

SQL_F04_EXCLUDED_COUNT = """
SELECT COUNT(property_id) AS excluded_count
FROM property
WHERE property_type_id = %s AND development_id IS NULL;
"""

# -----------------------------------------------------------------------------
# F05: Location of development + avg price/sqm + listings per unit type
# -----------------------------------------------------------------------------
SQL_F05_DEV_LOCATION = """
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
"""

SQL_F05_LOCATION_PATH = """
WITH RECURSIVE path_tree AS (
    SELECT location_id, parent_location_id, name, name_en, name_ar, location_type, 0 AS lvl
    FROM location
    WHERE location_id = %s
    UNION ALL
    SELECT l.location_id, l.parent_location_id, l.name, l.name_en, l.name_ar, l.location_type, pt.lvl + 1
    FROM location l
    INNER JOIN path_tree pt ON l.location_id = pt.parent_location_id
)
SELECT location_id, name, name_en, name_ar, location_type 
FROM path_tree 
ORDER BY lvl DESC;
"""

SQL_F05_UNIT_TYPES = """
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
"""

# -----------------------------------------------------------------------------
# F06: All properties in a certain area with avg price/sqm by unit type
# -----------------------------------------------------------------------------
SQL_F06_AREA_SUMMARY = """
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
"""

SQL_F06_PROPERTIES_PAGINATED = """
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
ORDER BY {order_by}
LIMIT %s OFFSET %s;
"""

SQL_F06_COUNT = """
WITH RECURSIVE area_tree AS (
    SELECT location_id FROM location WHERE location_id = %s
    UNION ALL
    SELECT l.location_id FROM location l INNER JOIN area_tree t ON l.parent_location_id = t.location_id
)
SELECT COUNT(p.property_id) AS total_count
FROM property p
JOIN area_tree a ON p.location_id = a.location_id
WHERE p.price > 0 AND p.area_sqm > 0;
"""

# -----------------------------------------------------------------------------
# F07: Properties in area, price range, with given amenities (ALL / ANY)
# -----------------------------------------------------------------------------
def build_f07_query(amenity_ids: list, match_mode: str = "ALL"):
    """Builds relational division query for amenities matching."""
    amenities_count = len(amenity_ids)
    if amenities_count == 0:
        cte_amenity = ""
        join_amenity = ""
    elif match_mode.upper() == "ALL":
        placeholders = ", ".join(["%s"] * amenities_count)
        cte_amenity = f""",
        matching_amenities AS (
            SELECT pa.property_id
            FROM property_amenity pa
            WHERE pa.amenity_id IN ({placeholders})
            GROUP BY pa.property_id
            HAVING COUNT(DISTINCT pa.amenity_id) = {amenities_count}
        )"""
        join_amenity = "JOIN matching_amenities ma ON p.property_id = ma.property_id"
    else: # ANY
        placeholders = ", ".join(["%s"] * amenities_count)
        cte_amenity = f""",
        matching_amenities AS (
            SELECT DISTINCT pa.property_id
            FROM property_amenity pa
            WHERE pa.amenity_id IN ({placeholders})
        )"""
        join_amenity = "JOIN matching_amenities ma ON p.property_id = ma.property_id"

    query = f"""
    WITH RECURSIVE area_tree AS (
        SELECT location_id FROM location WHERE location_id = %s
        UNION ALL
        SELECT l.location_id FROM location l INNER JOIN area_tree t ON l.parent_location_id = t.location_id
    ){cte_amenity}
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
        GROUP_CONCAT(DISTINCT am.name ORDER BY am.name SEPARATOR ', ') AS amenities_list
    FROM property p
    JOIN area_tree a ON p.location_id = a.location_id
    {join_amenity}
    JOIN property_type pt ON p.property_type_id = pt.property_type_id
    LEFT JOIN development dev ON p.development_id = dev.development_id
    JOIN location loc ON p.location_id = loc.location_id
    LEFT JOIN property_amenity pa ON p.property_id = pa.property_id
    LEFT JOIN amenity am ON pa.amenity_id = am.amenity_id
    WHERE (%s IS NULL OR p.price >= %s)
      AND (%s IS NULL OR p.price <= %s)
      AND p.price > 0 AND p.area_sqm > 0
    GROUP BY p.property_id, p.source_listing_id, p.title, p.source_url, pt.name, dev.name, loc.name, p.area_sqm, p.bedrooms, p.bathrooms, p.price
    ORDER BY {{order_by}}
    LIMIT %s OFFSET %s;
    """
    return query

# -----------------------------------------------------------------------------
# F08: Top 5 developers by number of resale listings
# -----------------------------------------------------------------------------
SQL_F08_TOP_DEVELOPERS = """
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
"""

# -----------------------------------------------------------------------------
# F09: All properties by area, property type, and contract year
# -----------------------------------------------------------------------------
SQL_F09_GROUPED_SUMMARY = """
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
"""

# -----------------------------------------------------------------------------
# F10: Averages by area and development project
# -----------------------------------------------------------------------------
SQL_F10_AREA_DEV_AVERAGES = """
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
ORDER BY {order_by}
LIMIT %s OFFSET %s;
"""

SQL_F10_COUNT = """
SELECT COUNT(DISTINCT d.development_id) AS total_projects
FROM property p
JOIN development d ON p.development_id = d.development_id
JOIN location loc ON p.location_id = loc.location_id
WHERE (%s IS NULL OR loc.location_id = %s)
GROUP BY loc.location_id, d.development_id
HAVING COUNT(p.property_id) >= %s;
"""
