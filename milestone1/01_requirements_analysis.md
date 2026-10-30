# Milestone 1: Requirements Analysis & Conceptual Design
## CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (Fall 2026)

---

## 1. Traceability & Entity Candidates

The following table lists every candidate entity identified from the authoritative Milestone 1 specifications (Section 1) and the Milestone 3 analytical requirements (Section 3), along with its traceable justification.

| Entity Candidate | Requirement Source | Justification & Role in System |
|---|---|---|
| **`developer`** | Section 1.2, Section 3 (Q8) | Real-estate development companies (e.g. Emaar, SODIC, Palm Hills, La Vista) that build projects. Required to analyze developer inventory and average price/sqm. |
| **`location`** | Section 1.1, 1.2, 1.3, Section 3 (Q5, Q6, Q7, Q9, Q10) | Geographic entities modeled hierarchically (Governorate → City → District/Area). Enables spatial filtering and aggregations across properties, developments, and user focus areas. |
| **`development`** | Section 1.2, 1.4, Section 3 (Q4, Q5, Q8, Q10) | Real-estate compound or master-planned project (e.g. Mivida, Badya, Patio Vida). Connects to a developer and a location. Receives user reviews. Properties optionally belong to a development. |
| **`property_type`** | Section 1.1, Section 3 (Q4, Q5, Q6, Q9) | Classification of property unit (e.g. Apartment, Villa, Townhouse, Duplex, Penthouse, Chalet, Studio). Lookup entity for deterministic categorisation. |
| **`payment_method`** | Section 1.1, Section 3 (Q10) | Financial terms accepted for the listing (e.g. Cash, Installments, Cash & Installments). Extensible lookup table. |
| **`property`** | Section 1.1, Section 2, Section 3 (all queries) | The core resale property listing from AqarExit. Stores physical, financial, contract, and crawler metadata. |
| **`amenity`** | Section 1.1, Section 3 (Q7) | Property features and facilities (e.g. Swimming Pool, Elevator, Private Garden, 24/7 Security, Garage, Clubhouse). |
| **`property_amenity`** | Section 1.1, Section 3 (Q7) | Associative entity resolving the many-to-many relationship between `property` and `amenity`. |
| **`app_user`** | Section 1.3, Section 3 (Q1, Q2, Q3) | Registered system users with demographic profile and preferences. |
| **`user_focus_area`** | Section 1.3 | Associative entity resolving the multi-valued attribute "main areas of focus" as a many-to-many relationship between `app_user` and `location`. |
| **`review`** | Section 1.4, Section 3 (Q2, Q3) | Evaluative feedback and 1-10 rating submitted by a user for a development project. |

---

## 2. Attribute Catalog

The table below catalogs every attribute across all entities, detailing conceptual data types, nullability, key nature, and derived/composite status.

| Entity | Attribute | Conceptual Type | Nullable? | Key? | Derived? | Multi-valued? | Composite? | Description & Business Rules |
|---|---|---|---|---|---|---|---|---|
| **`developer`** | `developer_id` | Surrogate INT | No | PK | No | No | No | Auto-increment unique identifier |
| | `name` | String(150) | No | Unique | No | No | No | Canonical developer name in English or Arabic |
| | `slug` | String(150) | Yes | Unique | No | No | No | URL-friendly identifier |
| | `created_at` | Timestamp | No | No | No | No | No | Creation timestamp (default current timestamp) |
| **`location`** | `location_id` | Surrogate INT | No | PK | No | No | No | Auto-increment unique identifier |
| | `parent_location_id`| Surrogate INT | Yes | FK | No | No | No | Self-reference to parent location (e.g. City → Governorate) |
| | `name` | String(150) | No | Part of UQ| No | No | No | Location/Area name (e.g. New Cairo, 5th Settlement) |
| | `location_type` | Enum / String | No | No | No | No | No | 'governorate', 'city', 'area' |
| | `latitude` | Decimal(9,6) | Yes | No | No | No | No | Geographic coordinate latitude (-90 to +90) |
| | `longitude` | Decimal(9,6) | Yes | No | No | No | No | Geographic coordinate longitude (-180 to +180) |
| **`development`**| `development_id`| Surrogate INT | No | PK | No | No | No | Auto-increment unique identifier |
| | `developer_id` | Surrogate INT | Yes | FK | No | No | No | Referenced developer (optional if independent development) |
| | `location_id` | Surrogate INT | Yes | FK | No | No | No | Geographic location of the development |
| | `name` | String(200) | No | Part of UQ| No | No | No | Project / compound name (e.g. Patio Vida) |
| | `latitude` | Decimal(9,6) | Yes | No | No | No | No | Spatial latitude of compound center |
| | `longitude` | Decimal(9,6) | Yes | No | No | No | No | Spatial longitude of compound center |
| | `source_url` | String(500) | Yes | No | No | No | No | Source URL on AqarExit if project page exists |
| | `created_at` | Timestamp | No | No | No | No | No | Row creation timestamp |
| **`property_type`**| `property_type_id`| Surrogate INT| No | PK | No | No | No | Auto-increment unique identifier |
| | `name` | String(50) | No | Unique | No | No | No | Standardized unit type name (e.g. Apartment, Villa) |
| **`payment_method`**| `payment_method_id`| Surrogate INT| No | PK | No | No | No | Auto-increment unique identifier |
| | `name` | String(50) | No | Unique | No | No | No | Payment method name (Cash, Installments) |
| **`property`** | `property_id` | Surrogate BIGINT| No | PK | No | No | No | Auto-increment primary key |
| | `source_listing_id`| String(100)| No | Unique | No | No | No | AqarExit natural ID / UUID |
| | `source_url` | String(500) | No | No | No | No | No | Full URL of the crawled listing |
| | `title` | String(300) | Yes | No | No | No | No | Listing headline/title |
| | `description` | MediumText | Yes | No | No | No | No | Full textual listing description |
| | `development_id`| Surrogate INT | Yes | FK | No | No | No | Optional development link (NULL if standalone) |
| | `location_id` | Surrogate INT | No | FK | No | No | No | Mandatory area/location reference |
| | `property_type_id`| Surrogate INT| No | FK | No | No | No | Mandatory property type classification |
| | `payment_method_id`| Surrogate INT| Yes | FK | No | No | No | Payment arrangement |
| | `area_sqm` | Decimal(10,2) | No | No | No | No | No | Built-up area in square meters (> 0) |
| | `bedrooms` | TinyInt | Yes | No | No | No | No | Bedroom count (>= 0, studios allow 0) |
| | `bathrooms` | TinyInt | Yes | No | No | No | No | Bathroom count (>= 0) |
| | `price` | Decimal(15,2) | No | No | No | No | No | Asking / resale price (> 0) |
| | `market_price` | Decimal(15,2) | Yes | No | No | No | No | Developer/current market valuation |
| | `down_payment` | Decimal(15,2) | Yes | No | No | No | No | Cash required now (<= price) |
| | `installment_amount`| Decimal(15,2)| Yes| No | No | No | No | Periodic installment installment price |
| | `installment_frequency`| String(50)| Yes| No | No | No | No | Quarterly, monthly, semi-annual, annual |
| | `installment_years`| Decimal(4,1)| Yes| No | No | No | No | Remaining duration in years |
| | `remaining_balance`| Decimal(15,2)| Yes| No | No | No | No | Total balance remaining with developer |
| | `gain_over_market_value`| Decimal(15,2)| Yes| No| No | No | No | Reported gain vs market valuation |
| | `gain_percentage`| Decimal(7,2) | Yes | No | No | No | No | Gain percentage |
| | `discount_over_market_price`| Decimal(15,2)| Yes| No| No| No | No | Discount over developer price |
| | `contract_year` | SmallInt | Yes | No | No | No | No | Year original contract was signed (1990..2030) |
| | `delivery_year` | SmallInt | Yes | No | No | No | No | Expected/actual handover year |
| | `currency` | Char(3) | No | No | No | No | No | Currency ISO code, default 'EGP' |
| | `scraped_at` | Timestamp | No | No | No | No | No | Audit timestamp of crawl |
| | *(derived)* `price_per_sqm` | Decimal(15,2)| No | No | Yes | No | No | `price / area_sqm` (exposed via view) |
| **`amenity`** | `amenity_id` | Surrogate INT | No | PK | No | No | No | Auto-increment unique identifier |
| | `name` | String(100) | No | Unique | No | No | No | Name of facility/amenity (e.g. Elevator, Pool) |
| **`property_amenity`**| `property_id`| Surrogate BIGINT| No| Composite PK, FK| No| No| No| References `property.property_id` |
| | `amenity_id` | Surrogate INT | No | Composite PK, FK| No| No| No| References `amenity.amenity_id` |
| **`app_user`** | `user_id` | Surrogate INT | No | PK | No | No | No | Auto-increment unique identifier |
| | `username` | String(50) | No | Unique | No | No | No | Unique username chosen at registration |
| | `email` | String(150) | No | Unique | No | No | No | Valid email address |
| | `gender` | Enum / String | Yes | No | No | No | No | 'male', 'female', 'other', 'prefer_not_to_say' |
| | `birthdate` | Date | No | No | No | No | No | Date of birth (must be in past) |
| | `registered_at` | Timestamp | No | No | No | No | No | Account registration date |
| | *(derived)* `age`| SmallInt | No | No | Yes | No | No | `TIMESTAMPDIFF(YEAR, birthdate, CURDATE())` |
| **`user_focus_area`**| `user_id` | Surrogate INT | No | Composite PK, FK| No| No| No| References `app_user.user_id` |
| | `location_id` | Surrogate INT | No | Composite PK, FK| No| No| No| References `location.location_id` |
| **`review`** | `review_id` | Surrogate INT | No | PK | No | No | No | Auto-increment unique review ID |
| | `user_id` | Surrogate INT | No | FK | No | No | No | Author of review (`app_user`) |
| | `development_id`| Surrogate INT| No | FK | No | No | No | Target project (`development`) |
| | `rating` | TinyInt | No | No | No | No | No | Integer rating constrained between 1 and 10 |
| | `review_text` | Text | Yes | No | No | No | No | Textual review content |
| | `created_at` | Timestamp | No | No | No | No | No | Submission timestamp |

---

## 3. Relationships, Cardinality & Participation

| Relationship | Participating Entities | Cardinality | Participation | Plain English Business Rule |
|---|---|---|---|---|
| **Developer–Development** | `developer` (1) ↔ `development` (N) | 1:N | `developer` Partial; `development` Partial | A developer can build zero, one, or many developments. A development is typically built by one developer, but can exist independently if the developer is unlisted. |
| **Location–Location (Hierarchy)** | `location` (parent, 1) ↔ `location` (child, N) | 1:N | Parent Partial; Child Partial | A location can contain multiple sub-locations (e.g. Cairo contains New Cairo, which contains 5th Settlement). Top-level governorates have no parent. |
| **Location–Development** | `location` (1) ↔ `development` (N) | 1:N | `location` Partial; `development` Partial | A development is situated in one primary area/location. A location can contain zero or multiple developments. |
| **Location–Property** | `location` (1) ↔ `property` (N) | 1:N | `location` Partial; `property` Total | Every property must belong to a known geographic location. A location may have zero or multiple listings. |
| **Development–Property** | `development` (1) ↔ `property` (N) | 1:N | `development` Partial; `property` Partial | A property optionally belongs to a development compound. A development can have zero or many resale properties listed. |
| **PropertyType–Property** | `property_type` (1) ↔ `property` (N) | 1:N | `property_type` Partial; `property` Total | Every property listing must have exactly one property classification (e.g. Apartment, Villa). A property type classifies zero or many properties. |
| **PaymentMethod–Property** | `payment_method` (1) ↔ `property` (N) | 1:N | `payment_method` Partial; `property` Partial | A property listing specifies zero or one primary payment method. A payment method applies to zero or many properties. |
| **Property–Amenity** | `property` (M) ↔ `amenity` (N) | M:N | `property` Partial; `amenity` Partial | A property can feature zero or multiple amenities. An amenity can be present in zero or multiple properties. Resolved via `property_amenity`. |
| **User–FocusArea** | `app_user` (M) ↔ `location` (N) | M:N | `app_user` Partial; `location` Partial | A user can select zero or multiple areas of interest. A location can be followed by zero or many users. Resolved via `user_focus_area`. |
| **User–Development (Review)** | `app_user` (M) ↔ `development` (N) | M:N (Associative) | `app_user` Partial; `development` Partial | A user may submit reviews for development projects. A development receives reviews from users. Modeled as the entity `review` carrying attributes `rating`, `review_text`, `created_at`. |

---

## 4. Design Decisions & Documented Assumptions

| # | Topic | Decision | Alternatives Considered | Justification & Professor Defense |
|---|---|---|---|---|
| **A1** | **User Age Storage** | Store `birthdate DATE` only; derive `age` dynamically via view `v_user_profile` using `TIMESTAMPDIFF(YEAR, birthdate, CURDATE())`. | Store `age INT` statically, or use a generated column. | Storing a static age violates 3NF and causes temporal drift (data becomes stale next year). MySQL generated columns prohibit non-deterministic functions like `CURDATE()`. A view guarantees perfect accuracy at query time. |
| **A2** | **Price per sqm Storage** | Store `price` and `area_sqm`; expose `price_per_sqm` via view `v_property_metrics` and generated column. | Store a redundant column `price_per_sqm` in `property`. | Redundant storage can diverge if either price or area is updated. Deriving it prevents update anomalies and guarantees consistency. |
| **A3** | **Multiple Reviews per User** | Allow a user to submit multiple reviews over time for the same development (e.g. pre-handover and post-delivery feedback), with separate surrogate PK `review_id`. | Impose `UNIQUE(user_id, development_id)`. | Requirements state: "users can add their reviews for any development project". Keeping `review_id` as surrogate PK allows multiple reviews, but an index on `(user_id, development_id)` can optionally be made unique if required. |
| **A4** | **No Passwords in Schema** | Do not include a `password` column in `app_user`. | Add `password_hash VARCHAR(255)`. | Section 1.3 explicitly lists: email, username, gender, age, birthdate, areas of focus. It does not mention authentication credentials. Adding passwords is out of scope per Section 4 Step A. |
| **A5** | **Partial Participation for Development in Property** | `property.development_id` is nullable (`NULL` allowed). | Require every property to have a development, or create a dummy "Standalone" development. | Many Egyptian properties are standalone apartments or private buildings outside gated compounds. Creating artificial developments would corrupt analytics on real projects. |
| **A6** | **Optional Developer for Development** | `development.developer_id` is nullable (`NULL` allowed). | Enforce `NOT NULL` on developer. | Some local developments are municipality-built or unbranded private cooperatives where no corporate developer is named on AqarExit. |
| **A7** | **Single Self-Referencing Location Table vs. Three Tables** | Model geographic hierarchy as a single self-referencing `location` table (`location_id`, `parent_location_id`, `name`, `location_type`). | Three separate tables: `governorate`, `city`, `area`. | A self-referencing table cleanly handles variable administrative depths (e.g. Governorate → City → District → Sub-district/Zone) and enables clean M:N mapping to `user_focus_area` without needing three separate join tables. |
| **A8** | **Lookup Tables vs. ENUM for Types and Payment Methods** | Use dedicated lookup tables (`property_type`, `payment_method`, `amenity`) with surrogate keys and `UNIQUE` name constraints. | Hardcoded MySQL `ENUM(...)`. | Milestone II crawlers encounter unexpected or newly added types (e.g. Twin House, Penthouse, Duplex, Chalet). Modifying `ENUM` columns requires DDL locks (`ALTER TABLE`), whereas lookup tables allow dynamic, safe crawling. |
| **A9** | **User Entity Naming** | Name table `app_user` instead of `user`. | Name table `user` with backticks `` `user` ``. | `USER` is a reserved keyword in standard SQL and MySQL (and a built-in function `USER()`). Naming it `app_user` eliminates escaping errors across ORMs and raw scripts. |
| **A10** | **Natural Crawler Key on Property** | Add `source_listing_id VARCHAR(100) UNIQUE NOT NULL` and `source_url VARCHAR(500) NOT NULL` to `property`. | Rely solely on surrogate `property_id`. | Required for Milestone II crawler idempotency: enables `INSERT ... ON DUPLICATE KEY UPDATE` without generating duplicates upon repeated crawler runs. |

