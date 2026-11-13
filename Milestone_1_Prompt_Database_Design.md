# MILESTONE I MASTER PROMPT: Database Design & Implementation
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (F26)

> Paste everything below the line into your AI coding assistant (Claude Code, Cursor, Copilot Chat, etc.).
> Attach (or paste) a screenshot / saved HTML of a **sample AqarExit property page** (slide 3 of the project deck says "e.g. sample"). The assistant needs it to see which fields really exist.

---

## 0. ROLE AND CONTEXT

You are a senior database architect helping a computer-engineering student complete **Milestone I** of the AUC course *CSCE 2501 – Fundamentals of Database Systems* (Prof. Mohamed Alhalaby, Fall 2026). The project is a database application for **real-estate properties in Egypt that are offered for resale**, based on the public website **AqarExit** (`https://aqarexit.com/en/opportunities?show=8000`). The website has limited filtering and aggregation, so the final system lets users filter and run market analytics over resale inventory.

The project has three milestones. **You are only doing Milestone I now**, but the design must be **forward-compatible** with Milestone II (a web crawler will populate the non-user tables from scraped HTML) and Milestone III (an application that runs the analytics queries listed in Section 3).

**Tool required by the course: MySQL.** Target **MySQL 8.0+** (InnoDB, `utf8mb4`).
**Deadline: 3 October 2026. Worth: 20 points.**

### Official deliverables (exactly three, do not skip any)
1. **Entity-Relationship Diagram (ERD)** of the Real-Estate System
2. **Relational Model** for the system
3. **A transcript of the SQL statements** used to create the database and schema

### What is OUT of scope for this task (do not build these)
- No web crawler (Milestone II).
- No application / GUI / CLI / API (Milestone III).
- No bulk data population. (Only a tiny smoke test that is rolled back or deleted is allowed, see Section 9.)

---

## 1. SOURCE OF TRUTH: THE PROJECT REQUIREMENTS (verbatim intent)

Treat the following as the **only** authoritative requirements. Do not invent entities that the requirements do not imply, and do not drop anything listed here.

### 1.1 Property data
"The database system you design should be based on the information provided on each property, its location, developer, type, and the other information provided on the property page. Your database design should store all the information about the resale property, **including but not limited to**:"
- area
- location
- development
- type (apartment, villa, etc.)
- number of bedrooms and bathrooms
- list of amenities
- description
- payment method
- down payment
- gain over current value

### 1.2 Development projects
"Many of the properties on the website are located in a development project; for such cases the development project needs to be recorded, including its **name, location, developer**, etc."
- Implication: a property **may or may not** belong to a development (optional participation). A development belongs to one developer and has a location.

### 1.3 Users
"The system should also allow users to register using their **email addresses**, and pick a **username, gender, age, birthdate, and their main areas of focus**."
- Implication: "main areas of focus" is a **multi-valued** attribute (a user can have several), i.e. a **many-to-many** relationship between User and Location/Area. It must NOT be stored as a comma-separated string.

### 1.4 Reviews
"After registering, the users can add their reviews for any development project, providing their **rating (1-10)** and a **textual review**."
- Implication: Review links a **User** to a **Development** (not to a property). Rating is an integer constrained to 1..10 (enforce with a `CHECK` constraint).

---

## 2. DESIGN-FOR-THE-FUTURE REQUIREMENT: MILESTONE II ABSTRACT

Milestone II will crawl AqarExit and fill all **non-user** tables, extracting some fields from free-text. Therefore your schema must:
- Contain a **unique natural key from the source site** on the property table (e.g. `source_listing_id` and/or `source_url`, `UNIQUE`, `NOT NULL`) so the crawler can do idempotent upserts and avoid duplicates.
- Contain `scraped_at` / `last_seen_at` timestamps on crawled entities.
- Allow `NULL` in fields the site does not always provide (e.g. a listing with no development, no bathrooms count, no description).
- Use lookup tables (property type, amenity, location hierarchy, developer) with `UNIQUE` name constraints so the crawler can resolve names to IDs deterministically.
- Be able to hold Arabic text (`utf8mb4`, `utf8mb4_unicode_ci`).

---

## 3. DESIGN-FOR-THE-FUTURE REQUIREMENT: MILESTONE III QUERIES

The final application (Milestone III) must answer the following. **Your schema must make every one of them answerable with plain SQL joins and aggregations, without schema changes.** For each, you will later prove it (Section 9).

1. Register a user.
2. Add a new user review on a project.
3. View existing reviews of a project.
4. Top 10 projects with highest resale inventory, resale amount, and highest gain over market value, **by property type**.
5. Location of a given development, along with the **average price per sqm** and the **number of listings for each unit type**.
6. All the properties in a certain **area**, along with the **average price per sqm for each unit type**.
7. All the properties in a certain area **in a given price range**, with a **given set of amenities**.
8. **Top 5 developers** by the amount of resale listings, along with their avg price/sqm, avg required down payment, and gain over market value.
9. All the properties by **area, property type, and contract year**.
10. **Average installment price, average down payment, number of properties, average discount over market price, average age of contract year, and average market price**, by area and development project.

### Fields these queries force you to store (derive them into your design)
From the list above you must be able to obtain, per property:
- **Price** (the asking/resale price) and **area in sqm** → so **price per sqm** can be computed. (Store `price` and `area_sqm`; price/sqm is *derived*. Provide it via a **view or generated column**, do not store a redundant column that can go out of sync. Explain the choice.)
- **Market price / current market value** and **gain over market value** (amount and/or percent) and **discount over market price**. Capture what the site actually gives you; if the site gives only some of these, store the raw ones and derive the rest in a view.
- **Down payment** (amount) and **installment price / remaining installments** (amount, and, if the site shows it, the number of years/months and frequency).
- **Contract year** (the year the original contract was signed), because "average age of contract year" is requested. Store a `contract_year SMALLINT` (or the exact date if the site provides it).
- **Payment method** (e.g. cash / installments / etc.). Decide: lookup table `payment_method` vs. `ENUM`. Justify. A lookup table is preferred because the crawler may discover new values.
- **Amenities** as a many-to-many (so "properties with a given set of amenities" is a relational-division style query, which must be supported with a join table and a proper index).
- **Location hierarchy**, because queries filter by "area" and show "location of a development". Model location as a hierarchy table (e.g. governorate → city → area/district), with optional latitude/longitude for developments. Decide whether `location` is one self-referencing table or three tables, and justify.
- **Property type** lookup (apartment, villa, townhouse, duplex, chalet, studio, penthouse, twin house, etc. – do not hardcode a final list; the crawler will discover them).

---

## 4. YOUR WORKFLOW (follow in this exact order)

### Step A: Requirements analysis (write this to `milestone1/01_requirements_analysis.md`)
1. List every entity candidate, with a one-line justification traceable to a sentence in Section 1 or a query in Section 3.
2. List every attribute for each entity with: name, meaning, data type (conceptual), nullable?, derived?, multi-valued?, composite?, key?
3. List every relationship with: participating entities, **cardinality** (1:1, 1:N, M:N), **participation** (total/partial for each side), and the business rule in plain English.
4. List **assumptions** you had to make because the requirements are silent. Number them (A1, A2, ...). Examples you must resolve explicitly:
   - Can one user post multiple reviews on the same development? (Default recommendation: yes allowed, unless the requirements say otherwise. State your choice and show how to flip it with a `UNIQUE (user_id, development_id)` constraint.)
   - Is `age` stored or derived from `birthdate`? (Recommendation: store `birthdate` only and expose `age` through a **view**, because MySQL generated columns cannot use `CURDATE()`. The requirements list age as a registration input, so the view must expose it. State your decision.)
   - Do we store passwords? The requirements do **not** mention authentication fields, so **do not add a password column** unless you flag it as an optional assumption.
   - Can a property exist with no development? (Yes, partial participation.)
   - Is a developer optional for a development? (Decide and justify.)
5. If, and only if, something is genuinely **blocking** and ambiguous, ask me at most 3 concise questions first. Otherwise proceed with documented assumptions instead of asking.

### Step B: Conceptual design → the ERD (deliverable 1)
Produce the ERD in **three forms**:
1. `milestone1/erd.mmd`: a **Mermaid `erDiagram`** with all entities, all attributes, PK/FK markers, and relationship cardinalities in crow's-foot notation.
2. `milestone1/erd_description.md`: a textual ERD: for each entity, its attributes with key marks; for each relationship, its name, cardinality, participation, and any relationship attributes. This is what the student will use to **redraw the ERD by hand or in draw.io/Lucidchart/dbdiagram.io** if the course requires a specific notation.
3. `milestone1/erd.dbml`: the same model in **DBML** so it can be pasted into dbdiagram.io to render a professional diagram.

ERD notation rules:
- Use **crow's foot** or **Chen** notation consistently (state which). If Chen is used, mark weak entities with double borders, multi-valued attributes with double ellipses, derived attributes with dashed ellipses, and identifying relationships with double diamonds.
- Show **cardinality AND participation** on every relationship (e.g. a Property optionally belongs to one Development; a Development has zero-or-many Properties).
- Relationship attributes must be shown (e.g. `rating`, `review_text`, `created_at` on the User–Development *Review* relationship if you model Review as an associative entity, which is recommended so it has its own PK).
- **Every M:N must be visible** (User–Area-of-focus, Property–Amenity), and be resolved into associative tables in the relational model.
- Do not put entity-name noise in the diagram (no `tbl_` prefixes).

### Step C: Logical design → the Relational Model (deliverable 2)
Write `milestone1/relational_model.md` containing:
1. **ER-to-relational mapping explanation**: how each entity, each 1:N, each M:N, each multi-valued attribute, and each hierarchy was mapped.
2. The relational schema in standard textual notation, e.g.
   `Property(property_id PK, source_listing_id UNIQUE NOT NULL, development_id FK→Development, type_id FK→PropertyType, ...)`
   with **underlined/marked PKs, FKs with referenced table, UNIQUE, NOT NULL**.
3. A **table of functional dependencies** per table and a **normalization argument** that every table is in **3NF (preferably BCNF)**. If you deliberately denormalize anything, say so, say why, and show the tradeoff.
4. A **referential integrity table**: for every FK: `ON DELETE` and `ON UPDATE` action, with a one-line reason (e.g. deleting a `User` cascades to their `Review` rows; deleting a `Development` is `RESTRICT` while it has properties; deleting a `Property` cascades to `PropertyAmenity`).
5. A **constraint catalogue**: every `CHECK`, `UNIQUE`, `NOT NULL`, `DEFAULT`.

### Step D: Physical design → the SQL transcript (deliverable 3)
Write `milestone1/schema.sql` and execute it against a real MySQL 8 instance (see Section 8 for how), saving the session output to `milestone1/schema_transcript.txt`.

---

## 5. MINIMUM EXPECTED ENTITIES (you may refine/split/merge with justification)

The list below is a **starting checklist**, not a cage. Every item must either appear in your design or have a written justification for not appearing.

| Entity / Table | Purpose | Key notes |
|---|---|---|
| `developer` | Company that builds developments | `name` UNIQUE |
| `location` (or `governorate`/`city`/`area`) | Geographic hierarchy used for "area" filters and development location | self-ref `parent_id` OR three tables; unique `(parent_id, name)`; optional `latitude`/`longitude` |
| `development` | Development project (name, location, developer) | FK→developer, FK→location, optional lat/long, `UNIQUE (name, developer_id)` or similar; `source_url` if the site has a page |
| `property_type` | apartment, villa, ... | `name` UNIQUE |
| `payment_method` | cash / installments / ... | `name` UNIQUE |
| `property` | The resale listing | FK→development (NULLABLE), FK→location, FK→property_type, FK→payment_method; `source_listing_id` UNIQUE; `source_url`; `title`; `description` (TEXT); `area_sqm`; `bedrooms`; `bathrooms`; `price`; `market_price`; `down_payment`; `installment_amount` (+ term fields if available); `gain_over_market_value` (amount and/or percent); `discount_over_market_price`; `contract_year`; `currency` default 'EGP'; `scraped_at` |
| `amenity` | pool, gym, security, garden... | `name` UNIQUE |
| `property_amenity` | M:N link | composite PK `(property_id, amenity_id)` + reverse index |
| `app_user` (avoid reserved word `user`) | Registered user | `email` UNIQUE NOT NULL (with format `CHECK` or at least a documented rule), `username` UNIQUE NOT NULL, `gender`, `birthdate`, `registered_at` |
| `user_focus_area` | M:N User ↔ Location (main areas of focus) | composite PK `(user_id, location_id)` |
| `review` | User's review of a development | PK `review_id`; FK→app_user; FK→development; `rating TINYINT CHECK (rating BETWEEN 1 AND 10)`; `review_text TEXT`; `created_at` |

Required **views** (create them in `schema.sql`):
- `v_property_metrics`: each property with computed `price_per_sqm`, and gain/discount if derivable.
- `v_user_profile`: user with computed `age` from `birthdate` (using `TIMESTAMPDIFF(YEAR, birthdate, CURDATE())`).

---

## 6. PHYSICAL-DESIGN RULES (MANDATORY)

**Engine & charset:** every table `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`.

**Naming:** `snake_case`, singular table names, PK named `<table>_id` (`BIGINT UNSIGNED AUTO_INCREMENT` for large tables like `property`, `INT UNSIGNED` is acceptable for small lookups), FK columns named exactly after the referenced PK, constraints named explicitly (`pk_`, `fk_<child>_<parent>`, `uq_`, `ck_`, `idx_`).

**Data types (be exact, justify non-obvious choices in comments):**
- Money (price, down payment, installment, market price): `DECIMAL(15,2)`. **Never** `FLOAT`/`DOUBLE`.
- Percentages: `DECIMAL(7,2)`.
- Area: `DECIMAL(10,2)`.
- Bedrooms/bathrooms: `TINYINT UNSIGNED` (nullable; studios may be 0).
- Contract year: `SMALLINT UNSIGNED` (or `YEAR`).
- Ratings: `TINYINT UNSIGNED` with `CHECK (rating BETWEEN 1 AND 10)`.
- Free text: `TEXT` / `MEDIUMTEXT` for description and reviews.
- Latitude/longitude: `DECIMAL(9,6)`.
- Gender: either `ENUM('male','female','other','prefer_not_to_say')` or a `CHECK` list. Pick one, justify.
- Dates: `DATE` for birthdate, `DATETIME`/`TIMESTAMP` with `DEFAULT CURRENT_TIMESTAMP` for audit fields.

**Constraints:**
- Every table has a PK.
- Every FK is declared with explicit `ON DELETE` / `ON UPDATE`.
- `CHECK` constraints for: rating range, non-negative money/area/bedrooms/bathrooms, `down_payment <= price` (if both non-null), plausible `contract_year` range (e.g. 1990 to current year + 1), plausible `birthdate` (not in the future).
- `NOT NULL` only where the business rule truly requires it. The crawler will meet incomplete listings, so do **not** over-constrain crawled attributes.

**Indexes (justify each one in a comment, tied to a Milestone III query number from Section 3):**
- Composite indexes for `property(location_id, property_type_id)`, `property(development_id, property_type_id)`, `property(price)`, `property(contract_year)`.
- Reverse index on `property_amenity(amenity_id, property_id)` for amenity-set filtering.
- `review(development_id, created_at)`.
- Do not index everything. Avoid redundant indexes (an index that is a prefix of another).

**Script hygiene (`schema.sql`):**
- Starts with `DROP DATABASE IF EXISTS resale_properties; CREATE DATABASE resale_properties CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; USE resale_properties;`
- Creates tables in **dependency order** (parents before children), with a header comment block per table explaining its purpose and which requirement it satisfies.
- Re-runnable from scratch with no errors.
- Uses only standard MySQL 8 syntax (no features unavailable on free hosts like db4free.net; note that Milestone III will host this DB remotely, so avoid exotic privileges, e.g. `CREATE TRIGGER` needing SUPER; mention if you use any trigger and why).

---

## 7. OUTPUT FILES (create exactly this structure)

```
milestone1/
├── 01_requirements_analysis.md      # Step A
├── erd.mmd                          # Mermaid ERD
├── erd.dbml                         # DBML for dbdiagram.io
├── erd_description.md               # textual ERD for hand-drawing / draw.io
├── relational_model.md              # Step C
├── schema.sql                       # Step D
├── schema_transcript.txt            # real execution output of schema.sql
├── verification.sql                 # Section 9 proofs
├── verification_transcript.txt      # output of verification.sql
└── README.md                        # how to reproduce; list of assumptions; deliverable mapping
```

`README.md` must include a table mapping **each official deliverable** to the file(s) that satisfy it, plus the full numbered **assumptions list**.

---

## 8. HOW TO EXECUTE AND CAPTURE THE TRANSCRIPT (do this for real, do not fabricate output)

1. If MySQL is not installed, start one with Docker:
   `docker run --name resale-mysql -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 -d mysql:8.0 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci`
2. Run the script with echo of each statement and capture all output:
   `mysql -u root -p --table -vvv < milestone1/schema.sql 2>&1 | tee milestone1/schema_transcript.txt`
   (or use `mysql --verbose`; the transcript must show each statement and its result, e.g. `Query OK`).
3. Then run `SHOW TABLES;`, `SHOW CREATE TABLE <each table>\G`, and `DESCRIBE <each table>;` and append their output to the transcript. This is the evidence the schema exists.
4. If you cannot run MySQL in your environment, **say so clearly** and give me the exact commands to run myself. Never invent transcript output.

---

## 9. VERIFICATION (prove the schema works, then leave it empty)

Write `verification.sql` that, inside a transaction that is **rolled back** at the end (so the database stays empty for Milestone II):
1. Inserts 2 developers, 3 locations (a mini hierarchy), 2 developments, 3 property types, 2 payment methods, 4 properties (one with no development), 5 amenities, property-amenity links, 3 users, focus areas, and 4 reviews.
2. Shows that **constraint violations are rejected**, each one in a separate guarded statement with a comment of the expected error:
   - rating 0 and rating 11
   - duplicate email, duplicate username
   - property with a non-existent `property_type_id`
   - duplicate `source_listing_id`
   - negative price
   - birthdate in the future
3. Runs **one example query for each of the 10 Milestone III functionalities** (Section 3) against that sample data, to prove the schema supports them. Number the queries Q1..Q10 matching Section 3, including the amenity-set query (use `GROUP BY ... HAVING COUNT(DISTINCT amenity_id) = N`) and the top-N queries (`ORDER BY ... LIMIT`, window functions are fine on MySQL 8).
4. Ends with `ROLLBACK;` and then `SELECT COUNT(*)` on every table showing **0 rows**.

Save the output to `verification_transcript.txt`.

---

## 10. QUALITY BAR / SELF-REVIEW CHECKLIST (run this before you say "done")

Answer each line YES/NO in the README. Fix every NO.

- [ ] Every item in Section 1 (area, location, development, type, bedrooms, bathrooms, amenities, description, payment method, down payment, gain over current value, development name/location/developer, user email/username/gender/age/birthdate/areas of focus, review rating 1-10 + text) maps to a column or table.
- [ ] No multi-valued attribute stored in a single column.
- [ ] Every table is in 3NF/BCNF (or the deviation is justified).
- [ ] Every M:N has an associative table with a composite PK.
- [ ] Every FK has explicit ON DELETE / ON UPDATE.
- [ ] Rating is constrained to 1..10 at the database level.
- [ ] `property.development_id` is nullable.
- [ ] A crawler-friendly unique key exists on `property`.
- [ ] Price per sqm and age are **derived** (view), not stored redundantly.
- [ ] All 10 Milestone III functionalities are demonstrably answerable (Q1..Q10 run).
- [ ] `schema.sql` runs from scratch with zero errors and zero warnings (or each warning is explained).
- [ ] The final database is empty after verification.
- [ ] The ERD (3 forms), relational model, and SQL transcript all agree with one another (same tables, same columns, same keys). Cross-check automatically (e.g. script that compares table/column names in `erd.dbml`, `relational_model.md`, and `INFORMATION_SCHEMA`).
- [ ] No tables or columns exist that no requirement or query justifies.

---

## 11. STYLE OF YOUR RESPONSE

- Work step by step: A → B → C → D → verification. After each step, show me the created file(s) and a 5-line summary.
- Be explicit about **every design decision and its alternative** (a "Decision / Alternatives / Why" mini-table is ideal). The student will need to defend these decisions in front of the professor/TA.
- Do not use placeholder values like `TODO` or `...` in any file.
- If anything in the sample page contradicts this prompt, **the sample page and the official project text win**; tell me about the conflict.
- Finish with a short "What to hand in" list mapped to the three official deliverables.
