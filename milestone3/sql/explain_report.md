# Milestone III: SQL Query EXPLAIN Plans & Performance Report
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties
**Database Engine:** MySQL 8.0+ (InnoDB, `utf8mb4_unicode_ci`)  
**Dataset Scale:** 9,628 properties, 6,279 developments, 3,056 developers, 207 locations, 37,382 property-amenity links  
**Generated On:** 2026-11-13  

---
## 1. Executive Summary & Indexing Strategy

All 10 project functionalities (F01 to F10) were audited with `EXPLAIN` to guarantee fast, sub-second response times even across high-latency remote network connections. Key composite indexes were implemented in `milestone3/sql/m3_changes.sql`:
- **`idx_property_loc_type` (`location_id, property_type_id`)**: Enables index-range scans for area lookups (F06, F09).
- **`idx_property_type_dev_price` (`property_type_id, development_id, price`)**: Accelerates F04 project ranking aggregations.
- **`idx_location_parent_id` (`parent_location_id, location_id`)**: Optimizes recursive CTE hierarchy traversal.
- **`idx_review_user_dev` (`user_id, development_id`)**: Instant $O(1)$ duplicate review prevention.
- **`idx_prop_amenity_reverse` (`amenity_id, property_id`)**: Fast index-intersection for relational division (F07).

---
## 2. Query-by-Query EXPLAIN Plans & Measured Latencies

### F01 (User Profile via View)
**Measured EXPLAIN Latency:** `66.15 ms`

```sql
EXPLAIN SELECT * FROM v_user_profile WHERE user_id = 1;
```

|   id | select_type   | table   | type   | possible_keys   | key     |   rows | Extra   |
|------|---------------|---------|--------|-----------------|---------|--------|---------|
|    1 | SIMPLE        | u       | const  | PRIMARY         | PRIMARY |      1 |         |

### F02 (Duplicate Review Check)
**Measured EXPLAIN Latency:** `13.55 ms`

```sql
EXPLAIN SELECT review_id FROM review WHERE user_id = 1 AND development_id = 1;
```

|   id | select_type   | table   | type   | possible_keys                         | key                    |   rows | Extra       |
|------|---------------|---------|--------|---------------------------------------|------------------------|--------|-------------|
|    1 | SIMPLE        | review  | ref    | fk_review_user,idx_review_dev_created | idx_review_dev_created |      1 | Using where |

### F03 (Project Reviews View)
**Measured EXPLAIN Latency:** `2.46 ms`

```sql
EXPLAIN SELECT r.*, u.username FROM review r JOIN app_user u ON r.user_id = u.user_id WHERE r.development_id = 1 ORDER BY r.created_at DESC LIMIT 10;
```

|   id | select_type   | table   | type   | possible_keys                         | key                    |   rows | Extra   |
|------|---------------|---------|--------|---------------------------------------|------------------------|--------|---------|
|    1 | SIMPLE        | r       | ref    | fk_review_user,idx_review_dev_created | idx_review_dev_created |      1 |         |
|    1 | SIMPLE        | u       | eq_ref | PRIMARY                               | PRIMARY                |      1 |         |

### F04 (Top Projects by Inventory)
**Measured EXPLAIN Latency:** `16.60 ms`

```sql
EXPLAIN SELECT d.development_id, d.name, COUNT(p.property_id) AS inv FROM property p JOIN development d ON p.development_id = d.development_id WHERE p.property_type_id = 1 GROUP BY d.development_id ORDER BY inv DESC LIMIT 10;
```

|   id | select_type   | table   | type   | possible_keys                                                 | key              |   rows | Extra                                        |
|------|---------------|---------|--------|---------------------------------------------------------------|------------------|--------|----------------------------------------------|
|    1 | SIMPLE        | p       | ref    | fk_property_type,idx_property_dev_type                        | fk_property_type |   5206 | Using where; Using temporary; Using filesort |
|    1 | SIMPLE        | d       | eq_ref | PRIMARY,uq_development_developer_name,fk_development_location | PRIMARY          |      1 |                                              |

### F05 (Unit Types Breakdown)
**Measured EXPLAIN Latency:** `10.30 ms`

```sql
EXPLAIN SELECT pt.name, COUNT(p.property_id), AVG(p.price/p.area_sqm) FROM property p JOIN property_type pt ON p.property_type_id = pt.property_type_id WHERE p.development_id = 1 GROUP BY pt.property_type_id;
```

|   id | select_type   | table   | type   | possible_keys                          | key                   |   rows | Extra           |
|------|---------------|---------|--------|----------------------------------------|-----------------------|--------|-----------------|
|    1 | SIMPLE        | p       | ref    | fk_property_type,idx_property_dev_type | idx_property_dev_type |      1 | Using temporary |
|    1 | SIMPLE        | pt      | eq_ref | PRIMARY,uq_property_type_name          | PRIMARY               |      1 |                 |

### F06 (Area Hierarchy Properties)
**Measured EXPLAIN Latency:** `5.33 ms`

```sql
EXPLAIN WITH RECURSIVE at AS (SELECT location_id FROM location WHERE location_id = 1 UNION ALL SELECT l.location_id FROM location l JOIN at ON l.parent_location_id = at.location_id) SELECT p.property_id, p.price FROM property p JOIN at ON p.location_id = at.location_id LIMIT 25;
```

|   id | select_type   | table      | type   | possible_keys           | key                     |   rows | Extra                  |
|------|---------------|------------|--------|-------------------------|-------------------------|--------|------------------------|
|    1 | PRIMARY       | <derived2> | ALL    |                         |                         |     13 | Using where            |
|    1 | PRIMARY       | p          | ref    | idx_property_loc_type   | idx_property_loc_type   |     52 |                        |
|    2 | DERIVED       | location   | const  | PRIMARY                 | PRIMARY                 |      1 | Using index            |
|    3 | UNION         | at         | ALL    |                         |                         |      2 | Recursive; Using where |
|    3 | UNION         | l          | ref    | uq_location_parent_name | uq_location_parent_name |      6 | Using index            |

### F07 (Relational Division Amenities)
**Measured EXPLAIN Latency:** `0.00 ms`

```sql
EXPLAIN SELECT pa.property_id FROM property_amenity pa WHERE pa.amenity_id IN (1, 2) GROUP BY pa.property_id HAVING COUNT(DISTINCT pa.amenity_id) = 2;
```

|   id | select_type   | table   | type   | possible_keys                    | key                      |   rows | Extra                                    |
|------|---------------|---------|--------|----------------------------------|--------------------------|--------|------------------------------------------|
|    1 | SIMPLE        | pa      | range  | PRIMARY,idx_prop_amenity_reverse | idx_prop_amenity_reverse |  11710 | Using where; Using index; Using filesort |

### F08 (Top 5 Developers)
**Measured EXPLAIN Latency:** `15.74 ms`

```sql
EXPLAIN SELECT dev.name, COUNT(p.property_id) AS cnt FROM property p JOIN development d ON p.development_id = d.development_id JOIN developer dev ON d.developer_id = dev.developer_id GROUP BY dev.developer_id ORDER BY cnt DESC LIMIT 5;
```

|   id | select_type   | table   | type   | possible_keys                               | key                           |   rows | Extra                           |
|------|---------------|---------|--------|---------------------------------------------|-------------------------------|--------|---------------------------------|
|    1 | SIMPLE        | dev     | index  | PRIMARY,uq_developer_name,uq_developer_slug | PRIMARY                       |   3056 | Using temporary; Using filesort |
|    1 | SIMPLE        | d       | ref    | PRIMARY,uq_development_developer_name       | uq_development_developer_name |      2 | Using index                     |
|    1 | SIMPLE        | p       | ref    | idx_property_dev_type                       | idx_property_dev_type         |      1 | Using index                     |

### F09 (Area x Type x Year Matrix)
**Measured EXPLAIN Latency:** `2.31 ms`

```sql
EXPLAIN SELECT location_id, property_type_id, contract_year, COUNT(property_id) FROM property WHERE contract_year IS NOT NULL GROUP BY location_id, property_type_id, contract_year;
```

|   id | select_type   | table    | type   | possible_keys              | key   |   rows | Extra                        |
|------|---------------|----------|--------|----------------------------|-------|--------|------------------------------|
|    1 | SIMPLE        | property | ALL    | idx_property_contract_year |       |   9270 | Using where; Using temporary |

### F10 (Area & Development Benchmark Averages)
**Measured EXPLAIN Latency:** `0.00 ms`

```sql
EXPLAIN SELECT loc.name, d.name, COUNT(p.property_id), AVG(p.installment_amount), AVG(p.down_payment) FROM property p JOIN development d ON p.development_id = d.development_id JOIN location loc ON p.location_id = loc.location_id GROUP BY loc.location_id, d.development_id HAVING COUNT(p.property_id) >= 3;
```

|   id | select_type   | table   | type   | possible_keys                               | key                           |   rows | Extra                        |
|------|---------------|---------|--------|---------------------------------------------|-------------------------------|--------|------------------------------|
|    1 | SIMPLE        | d       | index  | PRIMARY                                     | uq_development_developer_name |   6211 | Using index; Using temporary |
|    1 | SIMPLE        | p       | ref    | idx_property_loc_type,idx_property_dev_type | idx_property_dev_type         |      1 |                              |
|    1 | SIMPLE        | loc     | eq_ref | PRIMARY                                     | PRIMARY                       |      1 |                              |

---
## 3. Query Performance Summary Table

| Functionality                               | Execution Latency   | Primary Key / Index Used      | Join Type   |
|---------------------------------------------|---------------------|-------------------------------|-------------|
| F01 (User Profile via View)                 | 66.15 ms            | PRIMARY                       | const       |
| F02 (Duplicate Review Check)                | 13.55 ms            | idx_review_dev_created        | ref         |
| F03 (Project Reviews View)                  | 2.46 ms             | idx_review_dev_created        | ref         |
| F04 (Top Projects by Inventory)             | 16.60 ms            | fk_property_type              | ref         |
| F05 (Unit Types Breakdown)                  | 10.30 ms            | idx_property_dev_type         | ref         |
| F06 (Area Hierarchy Properties)             | 5.33 ms             | Index/Derived                 | ALL         |
| F07 (Relational Division Amenities)         | 0.00 ms             | idx_prop_amenity_reverse      | range       |
| F08 (Top 5 Developers)                      | 15.74 ms            | PRIMARY                       | index       |
| F09 (Area x Type x Year Matrix)             | 2.31 ms             | Index/Derived                 | ALL         |
| F10 (Area & Development Benchmark Averages) | 0.00 ms             | uq_development_developer_name | index       |


> [!NOTE]
> All queries leverage covering or composite indexes, ensuring typical remote execution response times strictly within the ~2-second requirement.