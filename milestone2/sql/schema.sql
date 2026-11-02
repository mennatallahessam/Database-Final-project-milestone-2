-- =============================================================================
-- CSCE 2501 – Fundamentals of Database Systems – Fall 2026
-- Project: Resale Properties Database (AqarExit Platform)
-- Milestone 1 Deliverable: Physical Database Schema (MySQL 8.0+)
-- Character Set: utf8mb4, Collation: utf8mb4_unicode_ci, Engine: InnoDB
-- =============================================================================

DROP DATABASE IF EXISTS resale_properties;
CREATE DATABASE resale_properties
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE resale_properties;

-- =============================================================================
-- 1. LOOKUP TABLE: property_type
-- Satisfies: Section 1.1 (Property Type), Milestone III (Q4, Q5, Q6, Q9)
-- Purpose: Dynamic classification of property types (Apartment, Villa, etc.)
-- =============================================================================
CREATE TABLE property_type (
    property_type_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    name_en VARCHAR(100) NULL,
    name_ar VARCHAR(100) NULL,
    CONSTRAINT pk_property_type PRIMARY KEY (property_type_id),
    CONSTRAINT uq_property_type_name UNIQUE (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 2. LOOKUP TABLE: payment_method
-- Satisfies: Section 1.1 (Payment Method), Section 3 (Q10)
-- Purpose: Payment structure options (Cash, Installments, Cash & Installments)
-- =============================================================================
CREATE TABLE payment_method (
    payment_method_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    CONSTRAINT pk_payment_method PRIMARY KEY (payment_method_id),
    CONSTRAINT uq_payment_method_name UNIQUE (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 3. LOOKUP TABLE: amenity
-- Satisfies: Section 1.1 (List of Amenities), Milestone III (Q7)
-- Purpose: Controlled vocabulary of property features (Pool, Gym, Security, etc.)
-- =============================================================================
CREATE TABLE amenity (
    amenity_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    CONSTRAINT pk_amenity PRIMARY KEY (amenity_id),
    CONSTRAINT uq_amenity_name UNIQUE (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 4. GEOGRAPHIC HIERARCHY: location
-- Satisfies: Section 1.1, 1.2, 1.3, Milestone III (Q5, Q6, Q7, Q9, Q10)
-- Purpose: Self-referencing geographic hierarchy (Governorate -> City -> Area)
-- =============================================================================
CREATE TABLE location (
    location_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    parent_location_id INT UNSIGNED NULL,
    name VARCHAR(150) NOT NULL,
    name_en VARCHAR(150) NULL,
    name_ar VARCHAR(150) NULL,
    location_type ENUM('governorate', 'city', 'area') NOT NULL,
    latitude DECIMAL(9,6) NULL,
    longitude DECIMAL(9,6) NULL,
    CONSTRAINT pk_location PRIMARY KEY (location_id),
    CONSTRAINT fk_location_parent FOREIGN KEY (parent_location_id)
        REFERENCES location (location_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_location_parent_name UNIQUE (parent_location_id, name),
    CONSTRAINT ck_location_latitude CHECK (latitude IS NULL OR (latitude BETWEEN -90.000000 AND 90.000000)),
    CONSTRAINT ck_location_longitude CHECK (longitude IS NULL OR (longitude BETWEEN -180.000000 AND 180.000000))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 5. REAL-ESTATE DEVELOPER: developer
-- Satisfies: Section 1.1, 1.2, Milestone III (Q8)
-- Purpose: Corporate entity constructing projects (Emaar, Palm Hills, SODIC)
-- =============================================================================
CREATE TABLE developer (
    developer_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    slug VARCHAR(150) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_developer PRIMARY KEY (developer_id),
    CONSTRAINT uq_developer_name UNIQUE (name),
    CONSTRAINT uq_developer_slug UNIQUE (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 6. DEVELOPMENT PROJECT: development
-- Satisfies: Section 1.2 (Development Projects), Section 1.4, Milestone III (Q4, Q5, Q8, Q10)
-- Purpose: Real-estate compound or master plan (e.g. Patio Vida, Badya)
-- =============================================================================
CREATE TABLE development (
    development_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    developer_id INT UNSIGNED NULL,
    location_id INT UNSIGNED NULL,
    name VARCHAR(200) NOT NULL,
    latitude DECIMAL(9,6) NULL,
    longitude DECIMAL(9,6) NULL,
    source_url VARCHAR(500) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_development PRIMARY KEY (development_id),
    CONSTRAINT fk_development_developer FOREIGN KEY (developer_id)
        REFERENCES developer (developer_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_development_location FOREIGN KEY (location_id)
        REFERENCES location (location_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_development_developer_name UNIQUE (developer_id, name),
    CONSTRAINT ck_dev_latitude CHECK (latitude IS NULL OR (latitude BETWEEN -90.000000 AND 90.000000)),
    CONSTRAINT ck_dev_longitude CHECK (longitude IS NULL OR (longitude BETWEEN -180.000000 AND 180.000000))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 7. RESALE PROPERTY LISTING: property
-- Satisfies: Section 1.1, Section 2 (Crawler Natural Key), Milestone III (all queries)
-- Purpose: Central listing record containing physical, financial, and contract attributes
-- =============================================================================
CREATE TABLE property (
    property_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    source_listing_id VARCHAR(100) NOT NULL,
    source_url VARCHAR(500) NOT NULL,
    title VARCHAR(300) NULL,
    description MEDIUMTEXT NULL,
    development_id INT UNSIGNED NULL,
    location_id INT UNSIGNED NOT NULL,
    property_type_id INT UNSIGNED NOT NULL,
    payment_method_id INT UNSIGNED NULL,
    area_sqm DECIMAL(10,2) NOT NULL,
    bedrooms TINYINT UNSIGNED NULL,
    bathrooms TINYINT UNSIGNED NULL,
    price DECIMAL(15,2) NOT NULL,
    market_price DECIMAL(15,2) NULL,
    down_payment DECIMAL(15,2) NULL,
    installment_amount DECIMAL(15,2) NULL,
    installment_frequency VARCHAR(50) NULL,
    installment_years DECIMAL(4,1) NULL,
    remaining_balance DECIMAL(15,2) NULL,
    gain_over_market_value DECIMAL(15,2) NULL,
    gain_percentage DECIMAL(7,2) NULL,
    discount_over_market_price DECIMAL(15,2) NULL,
    contract_year SMALLINT UNSIGNED NULL,
    delivery_year SMALLINT UNSIGNED NULL,
    currency CHAR(3) NOT NULL DEFAULT 'EGP',
    scraped_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_property PRIMARY KEY (property_id),
    CONSTRAINT uq_property_source_listing_id UNIQUE (source_listing_id),
    CONSTRAINT fk_property_development FOREIGN KEY (development_id)
        REFERENCES development (development_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_property_location FOREIGN KEY (location_id)
        REFERENCES location (location_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_property_type FOREIGN KEY (property_type_id)
        REFERENCES property_type (property_type_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_property_payment_method FOREIGN KEY (payment_method_id)
        REFERENCES payment_method (payment_method_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT ck_property_area CHECK (area_sqm > 0),
    CONSTRAINT ck_property_price CHECK (price > 0),
    CONSTRAINT ck_property_market_price CHECK (market_price IS NULL OR market_price >= 0),
    CONSTRAINT ck_property_down_payment CHECK (down_payment IS NULL OR (down_payment >= 0 AND down_payment <= price)),
    CONSTRAINT ck_property_installment CHECK (installment_amount IS NULL OR installment_amount >= 0),
    CONSTRAINT ck_property_contract_year CHECK (contract_year IS NULL OR (contract_year BETWEEN 1990 AND 2030))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Query optimization indexes for Milestone III
-- Supports Q6, Q9 (Filter properties by location and unit type)
CREATE INDEX idx_property_loc_type ON property (location_id, property_type_id);

-- Supports Q4, Q5 (Filter properties by development and unit type)
CREATE INDEX idx_property_dev_type ON property (development_id, property_type_id);

-- Supports Q7 (Filter properties by price range)
CREATE INDEX idx_property_price ON property (price);

-- Supports Q9, Q10 (Filter/aggregate by contract year)
CREATE INDEX idx_property_contract_year ON property (contract_year);

-- =============================================================================
-- 8. ASSOCIATIVE TABLE: property_amenity
-- Satisfies: Section 1.1 (Amenities list), Milestone III (Q7 relational division)
-- Purpose: Resolves M:N relationship between properties and amenities
-- =============================================================================
CREATE TABLE property_amenity (
    property_id BIGINT UNSIGNED NOT NULL,
    amenity_id INT UNSIGNED NOT NULL,
    CONSTRAINT pk_property_amenity PRIMARY KEY (property_id, amenity_id),
    CONSTRAINT fk_prop_amenity_property FOREIGN KEY (property_id)
        REFERENCES property (property_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_prop_amenity_amenity FOREIGN KEY (amenity_id)
        REFERENCES amenity (amenity_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reverse index to support Q7 (finding properties having a specific amenity set)
CREATE INDEX idx_prop_amenity_reverse ON property_amenity (amenity_id, property_id);

-- =============================================================================
-- 9. USER ACCOUNTS: app_user
-- Satisfies: Section 1.3 (Users registration), Milestone III (Q1, Q2)
-- Purpose: Registered user accounts with demographic profile
-- Note: 'user' is a SQL reserved word, so 'app_user' is used
-- =============================================================================
CREATE TABLE app_user (
    user_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(150) NOT NULL,
    gender ENUM('male', 'female', 'other', 'prefer_not_to_say') NULL,
    birthdate DATE NOT NULL,
    registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_app_user PRIMARY KEY (user_id),
    CONSTRAINT uq_app_user_username UNIQUE (username),
    CONSTRAINT uq_app_user_email UNIQUE (email),
    CONSTRAINT ck_app_user_email_format CHECK (email LIKE '%_@__%.__%'),
    CONSTRAINT ck_app_user_birthdate CHECK (birthdate BETWEEN '1920-01-01' AND '2030-01-01')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 10. ASSOCIATIVE TABLE: user_focus_area
-- Satisfies: Section 1.3 (Main areas of focus - multi-valued attribute)
-- Purpose: Resolves M:N relationship between users and geographic areas
-- =============================================================================
CREATE TABLE user_focus_area (
    user_id INT UNSIGNED NOT NULL,
    location_id INT UNSIGNED NOT NULL,
    CONSTRAINT pk_user_focus_area PRIMARY KEY (user_id, location_id),
    CONSTRAINT fk_user_focus_user FOREIGN KEY (user_id)
        REFERENCES app_user (user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_user_focus_location FOREIGN KEY (location_id)
        REFERENCES location (location_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reverse index to find all users interested in a given area
CREATE INDEX idx_user_focus_area_reverse ON user_focus_area (location_id, user_id);

-- =============================================================================
-- 11. REVIEWS: review
-- Satisfies: Section 1.4 (Reviews), Milestone III (Q2, Q3)
-- Purpose: Evaluative 1-10 rating and textual review of development projects
-- =============================================================================
CREATE TABLE review (
    review_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    development_id INT UNSIGNED NOT NULL,
    rating TINYINT UNSIGNED NOT NULL,
    review_text TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_review PRIMARY KEY (review_id),
    CONSTRAINT fk_review_user FOREIGN KEY (user_id)
        REFERENCES app_user (user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_review_development FOREIGN KEY (development_id)
        REFERENCES development (development_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_review_rating CHECK (rating BETWEEN 1 AND 10)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Supports Q3 (View existing reviews of a project ordered by date)
CREATE INDEX idx_review_dev_created ON review (development_id, created_at DESC);

-- =============================================================================
-- 12. VIEWS: Derived Attributes and Analytical Metrics
-- Satisfies: Section 5 View Requirements, A1 and A2 Design Principles
-- =============================================================================

-- View 1: v_property_metrics
-- Computes price_per_sqm, discount_over_market_price, and effective gain dynamically
CREATE OR REPLACE VIEW v_property_metrics AS
SELECT
    p.property_id,
    p.source_listing_id,
    p.title,
    p.development_id,
    dev.name AS development_name,
    p.location_id,
    loc.name AS location_name,
    p.property_type_id,
    pt.name AS property_type_name,
    p.payment_method_id,
    pm.name AS payment_method_name,
    p.area_sqm,
    p.bedrooms,
    p.bathrooms,
    p.price,
    p.market_price,
    p.down_payment,
    p.installment_amount,
    p.contract_year,
    -- Derived metric: price per square meter
    ROUND(p.price / p.area_sqm, 2) AS price_per_sqm,
    -- Derived or stored gain over market value
    COALESCE(p.gain_over_market_value, 
        CASE WHEN p.market_price IS NOT NULL AND p.market_price > p.price 
             THEN p.market_price - p.price ELSE NULL END) AS effective_gain,
    -- Derived or stored discount over market price
    COALESCE(p.discount_over_market_price,
        CASE WHEN p.market_price IS NOT NULL AND p.market_price > p.price 
             THEN p.market_price - p.price ELSE NULL END) AS effective_discount,
    p.currency,
    p.scraped_at
FROM property p
JOIN location loc ON p.location_id = loc.location_id
JOIN property_type pt ON p.property_type_id = pt.property_type_id
LEFT JOIN development dev ON p.development_id = dev.development_id
LEFT JOIN payment_method pm ON p.payment_method_id = pm.payment_method_id;

-- View 2: v_user_profile
-- Computes user age dynamically based on current date without stale storage
CREATE OR REPLACE VIEW v_user_profile AS
SELECT
    u.user_id,
    u.username,
    u.email,
    u.gender,
    u.birthdate,
    TIMESTAMPDIFF(YEAR, u.birthdate, CURDATE()) AS age,
    u.registered_at
FROM app_user u;
