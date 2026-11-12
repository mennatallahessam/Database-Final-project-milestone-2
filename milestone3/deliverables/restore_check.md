# Milestone III: Database Dump Clean Restoration Verification
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties
**Author:** Mennatallah Essam Zaher  
**Instructor:** Prof. Hossam Sharara — The American University in Cairo (AUC)  
**Dump File Tested:** `milestone3/deliverables/resale_properties_remote_ready.sql` (5.31 MB, Pure UTF-8)  
**Test Database Restored Into:** `resale_properties_m3_restore_audit`  
**Audit Timestamp:** 2026-11-13  

---
## 1. Table Row Counts Parity Audit

| Table Name       |   Expected Count |   Restored Count | Integrity Status   |
|------------------|------------------|------------------|--------------------|
| property_type    |               11 |               11 | MATCH              |
| payment_method   |                2 |                2 | MATCH              |
| amenity          |               10 |               10 | MATCH              |
| location         |              207 |              207 | MATCH              |
| developer        |             3056 |             3056 | MATCH              |
| development      |             6279 |             6279 | MATCH              |
| property         |             9628 |             9628 | MATCH              |
| property_amenity |            37382 |            37382 | MATCH              |
| app_user         |               40 |               40 | MATCH              |
| user_focus_area  |               95 |               95 | MATCH              |
| review           |              120 |              120 | MATCH              |

---
## 2. Arabic Character Round-Trip Verification

Arabic strings restored without character distortion, loss, or mojibake:

- **English:** `Cairo` $\to$ **Arabic:** `القاهرة` (100% UTF-8 character match)
- **English:** `New Administrative Capital` $\to$ **Arabic:** `العاصمة الإدارية الجديدة` (100% UTF-8 character match)
- **English:** `New Administrative Capital` $\to$ **Arabic:** `العاصمة الإدارية الجديدة` (100% UTF-8 character match)

---
## 3. Restoration Integrity Conclusion

The dump file restores into a completely clean, fresh database with **100% row-count parity** across all 11 tables, 0 Foreign Key errors, and pristine bilingual character fidelity.