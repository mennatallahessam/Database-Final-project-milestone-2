# Relational Model & Logical Design
## CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (Fall 2026)

---

## 1. ER-to-Relational Mapping Explanation

The conceptual ER model was mapped to the relational schema using standard formal transformation rules:

1. **Regular Strong Entities**:
   - `DEVELOPER`, `LOCATION`, `PROPERTY_TYPE`, `PAYMENT_METHOD`, `AMENITY`, and `APP_USER` were mapped directly to relation schemas. Surrogate auto-increment keys were chosen as primary keys to facilitate joins and indexing.
2. **1:N Relationships**:
   - `DEVELOPER 1:N DEVELOPMENT`: Mapped by placing `developer_id` as a foreign key in `DEVELOPMENT` (nullable).
   - `LOCATION 1:N DEVELOPMENT`: Mapped by placing `location_id` as a foreign key in `DEVELOPMENT` (nullable).
   - `DEVELOPMENT 1:N PROPERTY`: Mapped by placing `development_id` as a foreign key in `PROPERTY` (nullable, preserving partial participation).
   - `LOCATION 1:N PROPERTY`: Mapped by placing `location_id` as a mandatory foreign key in `PROPERTY` (`NOT NULL`).
   - `PROPERTY_TYPE 1:N PROPERTY`: Mapped by placing `property_type_id` as a mandatory foreign key in `PROPERTY` (`NOT NULL`).
   - `PAYMENT_METHOD 1:N PROPERTY`: Mapped by placing `payment_method_id` as a foreign key in `PROPERTY` (nullable).
3. **Hierarchical Recursive Relationship**:
   - `LOCATION (Parent) 1:N LOCATION (Child)`: Mapped by including a self-referencing foreign key `parent_location_id` in the `LOCATION` relation (`NULL` for roots like Governorates).
4. **M:N Relationships and Multi-Valued Attributes**:
   - `PROPERTY M:N AMENITY`: Mapped to the associative table `property_amenity` with a composite primary key `(property_id, amenity_id)`.
   - Multi-valued attribute `app_user.areas_of_focus`: Normalized into the associative table `user_focus_area` with a composite primary key `(user_id, location_id)`, satisfying 1NF.
   - `APP_USER M:N DEVELOPMENT (Review)`: Mapped to the associative relation `review`, given its own surrogate primary key `review_id` to allow multiple temporal evaluations, carrying relationship attributes `rating`, `review_text`, and `created_at`.
5. **Derived Attributes**:
   - `price_per_sqm` and `age` were excluded from base tables to avoid redundancy and temporal update anomalies. They are exposed dynamically through views (`v_property_metrics` and `v_user_profile`).

---

## 2. Relational Schema Specification

Primary keys are marked with **[PK]**, foreign keys with **[FK → TargetTable]**, unique keys with **[UQ]**, and mandatory attributes with **[NN]**.

- **developer** (
    `developer_id` **[PK]** INT UNSIGNED AUTO_INCREMENT,
    `name` **[NN, UQ]** VARCHAR(150),
    `slug` **[UQ]** VARCHAR(150),
    `created_at` **[NN]** DATETIME DEFAULT CURRENT_TIMESTAMP
  )

- **location** (
    `location_id` **[PK]** INT UNSIGNED AUTO_INCREMENT,
    `parent_location_id` **[FK → location.location_id]** INT UNSIGNED NULL,
    `name` **[NN]** VARCHAR(150),
    `location_type` **[NN]** ENUM('governorate', 'city', 'area'),
    `latitude` DECIMAL(9,6) NULL,
    `longitude` DECIMAL(9,6) NULL,
    **[UQ]** (`parent_location_id`, `name`)
  )

- **development** (
    `development_id` **[PK]** INT UNSIGNED AUTO_INCREMENT,
    `developer_id` **[FK → developer.developer_id]** INT UNSIGNED NULL,
    `location_id` **[FK → location.location_id]** INT UNSIGNED NULL,
    `name` **[NN]** VARCHAR(200),
    `latitude` DECIMAL(9,6) NULL,
    `longitude` DECIMAL(9,6) NULL,
    `source_url` VARCHAR(500) NULL,
    `created_at` **[NN]** DATETIME DEFAULT CURRENT_TIMESTAMP,
    **[UQ]** (`developer_id`, `name`)
  )

- **property_type** (
    `property_type_id` **[PK]** INT UNSIGNED AUTO_INCREMENT,
    `name` **[NN, UQ]** VARCHAR(50)
  )

- **payment_method** (
    `payment_method_id` **[PK]** INT UNSIGNED AUTO_INCREMENT,
    `name` **[NN, UQ]** VARCHAR(50)
  )

- **property** (
    `property_id` **[PK]** BIGINT UNSIGNED AUTO_INCREMENT,
    `source_listing_id` **[NN, UQ]** VARCHAR(100),
    `source_url` **[NN]** VARCHAR(500),
    `title` VARCHAR(300) NULL,
    `description` MEDIUMTEXT NULL,
    `development_id` **[FK → development.development_id]** INT UNSIGNED NULL,
    `location_id` **[FK → location.location_id, NN]** INT UNSIGNED,
    `property_type_id` **[FK → property_type.property_type_id, NN]** INT UNSIGNED,
    `payment_method_id` **[FK → payment_method.payment_method_id]** INT UNSIGNED NULL,
    `area_sqm` **[NN]** DECIMAL(10,2),
    `bedrooms` TINYINT UNSIGNED NULL,
    `bathrooms` TINYINT UNSIGNED NULL,
    `price` **[NN]** DECIMAL(15,2),
    `market_price` DECIMAL(15,2) NULL,
    `down_payment` DECIMAL(15,2) NULL,
    `installment_amount` DECIMAL(15,2) NULL,
    `installment_frequency` VARCHAR(50) NULL,
    `installment_years` DECIMAL(4,1) NULL,
    `remaining_balance` DECIMAL(15,2) NULL,
    `gain_over_market_value` DECIMAL(15,2) NULL,
    `gain_percentage` DECIMAL(7,2) NULL,
    `discount_over_market_price` DECIMAL(15,2) NULL,
    `contract_year` SMALLINT UNSIGNED NULL,
    `delivery_year` SMALLINT UNSIGNED NULL,
    `currency` **[NN]** CHAR(3) DEFAULT 'EGP',
    `scraped_at` **[NN]** DATETIME DEFAULT CURRENT_TIMESTAMP
  )

- **amenity** (
    `amenity_id` **[PK]** INT UNSIGNED AUTO_INCREMENT,
    `name` **[NN, UQ]** VARCHAR(100)
  )

- **property_amenity** (
    `property_id` **[PK, FK → property.property_id, NN]** BIGINT UNSIGNED,
    `amenity_id` **[PK, FK → amenity.amenity_id, NN]** INT UNSIGNED
  )

- **app_user** (
    `user_id` **[PK]** INT UNSIGNED AUTO_INCREMENT,
    `username` **[NN, UQ]** VARCHAR(50),
    `email` **[NN, UQ]** VARCHAR(150),
    `gender` ENUM('male', 'female', 'other', 'prefer_not_to_say') NULL,
    `birthdate` **[NN]** DATE,
    `registered_at` **[NN]** DATETIME DEFAULT CURRENT_TIMESTAMP
  )

- **user_focus_area** (
    `user_id` **[PK, FK → app_user.user_id, NN]** INT UNSIGNED,
    `location_id` **[PK, FK → location.location_id, NN]** INT UNSIGNED
  )

- **review** (
    `review_id` **[PK]** INT UNSIGNED AUTO_INCREMENT,
    `user_id` **[FK → app_user.user_id, NN]** INT UNSIGNED,
    `development_id` **[FK → development.development_id, NN]** INT UNSIGNED,
    `rating` **[NN]** TINYINT UNSIGNED,
    `review_text` TEXT NULL,
    `created_at` **[NN]** DATETIME DEFAULT CURRENT_TIMESTAMP
  )

---

## 3. Functional Dependencies & Normalization Analysis (BCNF / 3NF)

A relation is in **Boyce-Codd Normal Form (BCNF)** if for every non-trivial functional dependency $X \rightarrow Y$, $X$ is a superkey. Every relation in this schema satisfies BCNF.

| Table | Candidate Keys | Functional Dependencies | Normal Form & Proof |
|---|---|---|---|
| **`developer`** | `{developer_id}`, `{name}`, `{slug}` | `developer_id` → `name, slug, created_at`<br>`name` → `developer_id, slug, created_at` | **BCNF**: Every left-hand side is a superkey. |
| **`location`** | `{location_id}`, `{parent_location_id, name}` | `location_id` → `parent_location_id, name, location_type, latitude, longitude`<br>`parent_location_id, name` → `location_id, location_type, latitude, longitude` | **BCNF**: Both determinants are candidate keys. No partial or transitive dependencies. |
| **`development`** | `{development_id}`, `{developer_id, name}` | `development_id` → `developer_id, location_id, name, latitude, longitude, source_url, created_at`<br>`developer_id, name` → `development_id, location_id, latitude, longitude, source_url, created_at` | **BCNF**: Every determinant is a candidate key. |
| **`property_type`** | `{property_type_id}`, `{name}` | `property_type_id` → `name`<br>`name` → `property_type_id` | **BCNF**: Every determinant is a candidate key. |
| **`payment_method`**| `{payment_method_id}`, `{name}`| `payment_method_id` → `name`<br>`name` → `payment_method_id` | **BCNF**: Every determinant is a candidate key. |
| **`property`** | `{property_id}`, `{source_listing_id}` | `property_id` → `source_listing_id, source_url, title, description, development_id, location_id, property_type_id, payment_method_id, area_sqm, bedrooms, bathrooms, price, market_price, down_payment, installment_amount, installment_frequency, installment_years, remaining_balance, gain_over_market_value, gain_percentage, discount_over_market_price, contract_year, delivery_year, currency, scraped_at`<br>`source_listing_id` → all attributes | **BCNF**: Every non-trivial FD originates from a complete candidate key. All non-key attributes are directly and fully dependent only on the keys. Derived attributes like `price_per_sqm` are avoided. |
| **`amenity`** | `{amenity_id}`, `{name}` | `amenity_id` → `name`<br>`name` → `amenity_id` | **BCNF**: Every determinant is a candidate key. |
| **`property_amenity`**| `{property_id, amenity_id}` | `property_id, amenity_id` → ∅ (All attributes form the primary key) | **BCNF**: Trivial FDs only. |
| **`app_user`** | `{user_id}`, `{username}`, `{email}` | `user_id` → `username, email, gender, birthdate, registered_at`<br>`username` → all attributes<br>`email` → all attributes | **BCNF**: Every determinant is a candidate key. Multi-valued focus areas were separated into `user_focus_area`. |
| **`user_focus_area`** | `{user_id, location_id}` | `user_id, location_id` → ∅ | **BCNF**: Trivial FDs only. |
| **`review`** | `{review_id}` | `review_id` → `user_id, development_id, rating, review_text, created_at` | **BCNF**: The single candidate key determines all other attributes. |

---

## 4. Referential Integrity Matrix

| Child Table | Foreign Key Column | Referenced Parent Table | Referenced Column | ON DELETE Action | ON UPDATE Action | Rationale |
|---|---|---|---|---|---|---|
| `location` | `parent_location_id` | `location` | `location_id` | `RESTRICT` | `CASCADE` | Deleting a parent location while sub-locations exist would orphan child areas. Updates to PK cascade. |
| `development` | `developer_id` | `developer` | `developer_id` | `SET NULL` | `CASCADE` | If a developer is removed, the physical development still exists. |
| `development` | `location_id` | `location` | `location_id` | `RESTRICT` | `CASCADE` | Prevents deleting an area if a development is located inside it. |
| `property` | `development_id` | `development` | `development_id` | `SET NULL` | `CASCADE` | Deleting a development should not destroy property listings (they become standalone). |
| `property` | `location_id` | `location` | `location_id` | `RESTRICT` | `CASCADE` | A property must always belong to a valid location. Prevents accidental geographic deletion. |
| `property` | `property_type_id` | `property_type` | `property_type_id` | `RESTRICT` | `CASCADE` | Cannot delete an active property type classification. |
| `property` | `payment_method_id`| `payment_method`| `payment_method_id`| `SET NULL` | `CASCADE` | Deleting a payment method resets listing terms to unspecified. |
| `property_amenity` | `property_id` | `property` | `property_id` | `CASCADE` | `CASCADE` | Deleting a property listing cascades to its amenity associations. |
| `property_amenity` | `amenity_id` | `amenity` | `amenity_id` | `RESTRICT` | `CASCADE` | Prevents deleting an amenity if properties are tagged with it. |
| `user_focus_area` | `user_id` | `app_user` | `user_id` | `CASCADE` | `CASCADE` | Deleting a user deletes their preference tags. |
| `user_focus_area` | `location_id` | `location` | `location_id` | `CASCADE` | `CASCADE` | Deleting an area clears user focus references. |
| `review` | `user_id` | `app_user` | `user_id` | `CASCADE` | `CASCADE` | Deleting a user deletes the user's reviews. |
| `review` | `development_id`| `development` | `development_id`| `CASCADE` | `CASCADE` | Deleting a development removes its attached reviews. |

---

## 5. Constraint Catalogue

### 5.1 Primary Key Constraints
- `pk_developer`: `developer(developer_id)`
- `pk_location`: `location(location_id)`
- `pk_development`: `development(development_id)`
- `pk_property_type`: `property_type(property_type_id)`
- `pk_payment_method`: `payment_method(payment_method_id)`
- `pk_property`: `property(property_id)`
- `pk_amenity`: `amenity(amenity_id)`
- `pk_property_amenity`: `property_amenity(property_id, amenity_id)`
- `pk_app_user`: `app_user(user_id)`
- `pk_user_focus_area`: `user_focus_area(user_id, location_id)`
- `pk_review`: `review(review_id)`

### 5.2 Unique Constraints
- `uq_developer_name`: `developer(name)`
- `uq_developer_slug`: `developer(slug)`
- `uq_location_parent_name`: `location(parent_location_id, name)`
- `uq_development_dev_name`: `development(developer_id, name)`
- `uq_property_type_name`: `property_type(name)`
- `uq_payment_method_name`: `payment_method(name)`
- `uq_property_source_id`: `property(source_listing_id)`
- `uq_amenity_name`: `amenity(name)`
- `uq_user_username`: `app_user(username)`
- `uq_user_email`: `app_user(email)`

### 5.3 Check Constraints
- `ck_location_lat`: `latitude BETWEEN -90.0 AND 90.0`
- `ck_location_lng`: `longitude BETWEEN -180.0 AND 180.0`
- `ck_dev_lat`: `latitude BETWEEN -90.0 AND 90.0`
- `ck_dev_lng`: `longitude BETWEEN -180.0 AND 180.0`
- `ck_prop_area`: `area_sqm > 0`
- `ck_prop_price`: `price > 0`
- `ck_prop_market_price`: `market_price IS NULL OR market_price >= 0`
- `ck_prop_down_payment`: `down_payment IS NULL OR (down_payment >= 0 AND down_payment <= price)`
- `ck_prop_installment`: `installment_amount IS NULL OR installment_amount >= 0`
- `ck_prop_contract_year`: `contract_year IS NULL OR (contract_year BETWEEN 1990 AND 2030)`
- `ck_user_birthdate`: `birthdate BETWEEN '1920-01-01' AND '2030-01-01'`
- `ck_user_email`: `email LIKE '%_@__%.__%'`
- `ck_review_rating`: `rating BETWEEN 1 AND 10`

### 5.4 Performance & Query Indexes
- `idx_prop_loc_type`: `property(location_id, property_type_id)` (Supports Milestone III Q6, Q9)
- `idx_prop_dev_type`: `property(development_id, property_type_id)` (Supports Milestone III Q4, Q5)
- `idx_prop_price`: `property(price)` (Supports Milestone III Q7 price range filters)
- `idx_prop_contract_year`: `property(contract_year)` (Supports Milestone III Q9, Q10 contract year analytics)
- `idx_prop_amenity_rev`: `property_amenity(amenity_id, property_id)` (Supports Milestone III Q7 relational division)
- `idx_review_dev_created`: `review(development_id, created_at)` (Supports Milestone III Q3 view reviews)
