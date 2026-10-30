# Textual ERD Specification for Hand-Drawing / Draw.io / Lucidchart
## CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (Fall 2026)

This document provides the formal textual representation of the Entity-Relationship Diagram (ERD). Students can directly use this specification to draw the ERD in **Crow's Foot** notation or **Chen** notation using tools such as Draw.io, Lucidchart, or by hand.

---

## 1. Entities & Attributes

Notation guidelines:
- **[PK]**: Primary Key
- **[FK]**: Foreign Key
- **[UQ]**: Unique constraint
- **[NN]**: Not Null constraint
- **[DERIVED]**: Computed attribute (view)

### 1. `DEVELOPER`
- **developer_id** [PK, NN]: Auto-increment integer surrogate key.
- **name** [UQ, NN]: Official company name.
- **slug** [UQ]: URL slug.
- **created_at** [NN]: Audit creation timestamp.

### 2. `LOCATION` (Hierarchical Geographic Entity)
- **location_id** [PK, NN]: Auto-increment integer surrogate key.
- **parent_location_id** [FK]: References `LOCATION.location_id` (NULL for top-level governorates).
- **name** [NN]: Geographic name (e.g., Cairo, New Cairo, 5th Settlement).
- **location_type** [NN]: Hierarchy level ('governorate', 'city', 'area').
- **latitude**: Coordinate latitude (Decimal 9,6).
- **longitude**: Coordinate longitude (Decimal 9,6).
- *Composite Key*: `(parent_location_id, name)` is unique.

### 3. `DEVELOPMENT` (Real-Estate Compound / Project)
- **development_id** [PK, NN]: Auto-increment integer surrogate key.
- **developer_id** [FK]: References `DEVELOPER.developer_id` (Nullable).
- **location_id** [FK]: References `LOCATION.location_id` (Nullable).
- **name** [NN]: Compound or project name (e.g. Patio Vida, Badya, Mivida).
- **latitude**: Geographic coordinate latitude.
- **longitude**: Geographic coordinate longitude.
- **source_url**: AqarExit project page URL.
- **created_at** [NN]: Audit timestamp.
- *Composite Key*: `(developer_id, name)` is unique.

### 4. `PROPERTY_TYPE` (Lookup Table)
- **property_type_id** [PK, NN]: Auto-increment integer.
- **name** [UQ, NN]: Unit classification (Apartment, Villa, Townhouse, Duplex, Penthouse, Chalet, Studio).

### 5. `PAYMENT_METHOD` (Lookup Table)
- **payment_method_id** [PK, NN]: Auto-increment integer.
- **name** [UQ, NN]: Method of payment (Cash, Installments, Cash & Installments).

### 6. `PROPERTY` (Resale Listing)
- **property_id** [PK, NN]: Auto-increment 64-bit integer (`BIGINT`).
- **source_listing_id** [UQ, NN]: Natural crawler key / UUID from AqarExit.
- **source_url** [NN]: URL of the crawled listing.
- **title**: Listing title headline.
- **description**: Detailed free-text description.
- **development_id** [FK]: References `DEVELOPMENT.development_id` (Nullable; standalone properties have NULL).
- **location_id** [FK, NN]: References `LOCATION.location_id` (Mandatory).
- **property_type_id** [FK, NN]: References `PROPERTY_TYPE.property_type_id` (Mandatory).
- **payment_method_id** [FK]: References `PAYMENT_METHOD.payment_method_id` (Nullable).
- **area_sqm** [NN]: Built-up area in square meters.
- **bedrooms**: Number of bedrooms (0 for studios, positive integer).
- **bathrooms**: Number of bathrooms.
- **price** [NN]: Asking resale price (Decimal 15,2).
- **market_price**: Current market valuation by developer / owner.
- **down_payment**: Cash required up front (<= price).
- **installment_amount**: Periodic installment payment.
- **installment_frequency**: Frequency of installment (Quarterly, Monthly, etc.).
- **installment_years**: Number of installment years remaining.
- **remaining_balance**: Total remaining balance payable to developer.
- **gain_over_market_value**: Reported gain over market valuation.
- **gain_percentage**: Percentage gain over current value.
- **discount_over_market_price**: Discount relative to market price.
- **contract_year**: Year the original sales contract was signed (e.g. 2021).
- **delivery_year**: Handover year (e.g. 2029).
- **currency** [NN]: Default 'EGP'.
- **scraped_at** [NN]: Audit timestamp when data was scraped.
- *[DERIVED]* **price_per_sqm**: `price / area_sqm` (provided through View).

### 7. `AMENITY` (Lookup Table)
- **amenity_id** [PK, NN]: Auto-increment integer.
- **name** [UQ, NN]: Name of amenity (e.g., Swimming Pool, Elevator, Private Garden, 24/7 Security, Garage).

### 8. `PROPERTY_AMENITY` (M:N Associative Entity)
- **property_id** [PK, FK, NN]: References `PROPERTY.property_id`.
- **amenity_id** [PK, FK, NN]: References `AMENITY.amenity_id`.

### 9. `APP_USER` (System Registered User)
- **user_id** [PK, NN]: Auto-increment integer.
- **username** [UQ, NN]: Unique handle.
- **email** [UQ, NN]: Unique valid email address.
- **gender**: 'male', 'female', 'other', 'prefer_not_to_say'.
- **birthdate** [NN]: Date of birth (DATE).
- **registered_at** [NN]: Account creation timestamp.
- *[DERIVED]* **age**: `TIMESTAMPDIFF(YEAR, birthdate, CURDATE())` (provided through View).

### 10. `USER_FOCUS_AREA` (M:N Associative Entity for Multi-Valued Focus Areas)
- **user_id** [PK, FK, NN]: References `APP_USER.user_id`.
- **location_id** [PK, FK, NN]: References `LOCATION.location_id`.

### 11. `REVIEW` (Evaluative Feedback on Development)
- **review_id** [PK, NN]: Auto-increment integer.
- **user_id** [FK, NN]: References `APP_USER.user_id`.
- **development_id** [FK, NN]: References `DEVELOPMENT.development_id`.
- **rating** [NN]: Rating integer constrained to `1 <= rating <= 10`.
- **review_text**: Textual review commentary.
- **created_at** [NN]: Timestamp when review was submitted.

---

## 2. Relationships, Cardinality & Participation Matrix

| Relationship Name | Entity 1 | Cardinality & Participation (Side 1) | Entity 2 | Cardinality & Participation (Side 2) | Foreign Key Holder | Business Rule |
|---|---|---|---|---|---|---|
| **Builds** | `DEVELOPER` | Zero-or-Many (Partial) | `DEVELOPMENT` | Zero-or-One (Partial) | `DEVELOPMENT.developer_id` | A developer can build many developments. A development may optionally have an associated developer. |
| **Contains** | `LOCATION` (Parent) | Zero-or-Many (Partial) | `LOCATION` (Child) | Zero-or-One (Partial) | `LOCATION.parent_location_id` | A location can contain multiple sub-locations. Top-level locations have no parent. |
| **Development Location** | `LOCATION` | Zero-or-Many (Partial) | `DEVELOPMENT` | Zero-or-One (Partial) | `DEVELOPMENT.location_id` | A development belongs to one geographic location. A location contains zero or many developments. |
| **Property Location** | `LOCATION` | Zero-or-Many (Partial) | `PROPERTY` | Exactly-One (Total) | `PROPERTY.location_id` | Every property must belong to an area/location. |
| **Project Membership**| `DEVELOPMENT` | Zero-or-Many (Partial) | `PROPERTY` | Zero-or-One (Partial) | `PROPERTY.development_id` | A property may or may not belong to a development project (standalone allowed). |
| **Unit Categorization**| `PROPERTY_TYPE`| Zero-or-Many (Partial) | `PROPERTY` | Exactly-One (Total) | `PROPERTY.property_type_id` | Every property must have a property type classification. |
| **Payment Terms** | `PAYMENT_METHOD`| Zero-or-Many (Partial) | `PROPERTY` | Zero-or-One (Partial) | `PROPERTY.payment_method_id`| A property listing optionally specifies its payment terms. |
| **Property Features** | `PROPERTY` | One-or-Many (Total) | `PROPERTY_AMENITY`| Exactly-One (Total) | `PROPERTY_AMENITY.property_id`| Resolves M:N Property ↔ Amenity. |
| **Amenity Inclusion** | `AMENITY` | Zero-or-Many (Partial) | `PROPERTY_AMENITY`| Exactly-One (Total) | `PROPERTY_AMENITY.amenity_id` | Resolves M:N Property ↔ Amenity. |
| **User Interest** | `APP_USER` | Zero-or-Many (Partial) | `USER_FOCUS_AREA` | Exactly-One (Total) | `USER_FOCUS_AREA.user_id` | Resolves M:N User ↔ Location. |
| **Location Interest** | `LOCATION` | Zero-or-Many (Partial) | `USER_FOCUS_AREA` | Exactly-One (Total) | `USER_FOCUS_AREA.location_id`| Resolves M:N User ↔ Location. |
| **User Authorship** | `APP_USER` | Zero-or-Many (Partial) | `REVIEW` | Exactly-One (Total) | `REVIEW.user_id` | A user can write zero or multiple reviews. Each review belongs to exactly one user. |
| **Project Review** | `DEVELOPMENT` | Zero-or-Many (Partial) | `REVIEW` | Exactly-One (Total) | `REVIEW.development_id` | A development receives zero or multiple reviews. Each review targets exactly one development. |

