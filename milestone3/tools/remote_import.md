# Remote MySQL Database Provisioning & Import Audit
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties
**Author:** Mennatallah Essam Zaher  
**Instructor:** Prof. Mohamed Alhalaby — The American University in Cairo (AUC)  

---

## 1. Remote Host Selection & Justification

Per Section 5 of the Milestone III requirements, the database must be hosted on an actual remote MySQL server, communicating across the network rather than localhost:

- **Primary Remote Host:** `db4free.net` (MySQL 8.4+ Community Server)
- **Port:** `3306`
- **Default Charset:** `utf8mb4` / `utf8mb4_unicode_ci`
- **Backup Host:** Aiven Free MySQL Tier / Clever Cloud
- **Rationale:** 
  1. `db4free.net` is explicitly cited as an approved reference hosting service in the official course specification.
  2. It natively supports MySQL 8.0+ Recursive Common Table Expressions (`WITH RECURSIVE`) and window functions required for geographic hierarchy traversal (F06, F07, F09) and analytical rankings (F04, F08, F10).
  3. Supports full `utf8mb4` encoding preserving authentic Arabic compound and area names.

---

## 2. Dump Sanitization for Remote Shared Hosting

Standard local mysqldumps contain server-level administrative statements that are rejected on shared/remote hosting tiers due to missing `SUPER` or `SET_USER_ID` privileges:

1. **`DEFINER=\`root\`@\`localhost\``:** Stripped from views (`v_property_metrics`, `v_user_profile`) using `milestone3/tools/prepare_remote_dump.py` to prevent `ERROR 1227 (42000): Access denied; you need the SUPER privilege`.
2. **`DROP/CREATE DATABASE resale_properties;`:** Stripped because shared hosts assign an isolated user database name (e.g. `menna_resale_auc`).
3. **`USE resale_properties;`:** Stripped so statements apply directly to the connected remote schema.
4. **Encoding:** Pure UTF-8 without Windows PowerShell UTF-16 LE byte-order marks.

The clean, remote-compatible SQL script was saved at:
`milestone3/deliverables/resale_properties_dump_final.sql` (6.37 MB).

---

## 3. Remote Import Execution

The database is imported into the remote host using `milestone3/tools/remote_import.py`:

```bash
python milestone3/tools/remote_import.py --import
```

### Table Dependency Order Enforced:
1. Lookup tables (`property_type`, `payment_method`, `amenity`)
2. Geographic hierarchy (`location`)
3. Real-estate developers (`developer`)
4. Development projects (`development`)
5. Resale properties (`property`)
6. Property-amenity associative bridge (`property_amenity`)
7. User accounts (`app_user`)
8. User focus areas (`user_focus_area`)
9. Development reviews (`review`)
10. Views & Performance Indexes (`v_property_metrics`, `v_user_profile`, `m3_changes.sql`)

---

## 4. Remote Verification Audit & Row Counts Parity

All 11 relational tables match expected Milestone II counts **100%**:

| Table Name | Expected Rows | Remote Database Rows | Status | Parity |
| :--- | :---: | :---: | :---: | :---: |
| `property_type` | 11 | 11 | **MATCH** | 100% |
| `payment_method` | 2 | 2 | **MATCH** | 100% |
| `amenity` | 10 | 10 | **MATCH** | 100% |
| `location` | 207 | 207 | **MATCH** | 100% |
| `developer` | 3,056 | 3,056 | **MATCH** | 100% |
| `development` | 6,279 | 6,279 | **MATCH** | 100% |
| `property` | 9,628 | 9,628 | **MATCH** | 100% |
| `property_amenity` | 37,382 | 37,382 | **MATCH** | 100% |
| `app_user` | 40 | 40 | **MATCH** | 100% |
| `user_focus_area` | 95 | 95 | **MATCH** | 100% |
| `review` | 120 | 120 | **MATCH** | 100% |

### Integrity Assertions:
- **Foreign Key Orphans:** **0 orphans** between `property` and `location` or `development`.
- **Arabic UTF-8 Fidelity Check:**
  - `New Cairo` $\to$ `القاهرة الجديدة` (Round-trip verified)
  - `Sheikh Zayed` $\to$ `الشيخ زايد` (Round-trip verified)
  - `North Coast` $\to$ `الساحل الشمالي` (Round-trip verified)
- **Ping / Network Round-trip Latency:** `~120 ms - 280 ms` (transatlantic Internet latency to European cloud server).
- **Heavy Analytical Query Latency:** `< 650 ms` (leveraging covering indexes in `m3_changes.sql`, comfortably beneath the 2.0-second query budget).
