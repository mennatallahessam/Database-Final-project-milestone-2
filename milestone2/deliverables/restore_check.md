# Database Restore & Arabic Round-Trip Verification Check

**Date:** 2026-11-02  
**Source Database:** `resale_properties`  
**Restored Database:** `resale_properties_restore_test`  
**Dump File:** `milestone2/deliverables/resale_properties_dump.sql`  
**File Encoding:** Pure UTF-8 (Header: `-- MySQL dump 10.13`, No UTF-16 LE BOM)

---

## 1. Table Row Count Comparison (Source vs. Restored)

| Table Name | Source DB (`resale_properties`) | Restored DB (`resale_properties_restore_test`) | Verification Status |
| :--- | :---: | :---: | :---: |
| `property_type` | 11 | 11 | **MATCH** |
| `payment_method` | 2 | 2 | **MATCH** |
| `amenity` | 10 | 10 | **MATCH** |
| `location` | 207 | 207 | **MATCH** |
| `developer` | 3056 | 3056 | **MATCH** |
| `development` | 6279 | 6279 | **MATCH** |
| `property` | 9628 | 9628 | **MATCH** |
| `property_amenity` | 37382 | 37382 | **MATCH** |
| `app_user` | 40 | 40 | **MATCH** |
| `user_focus_area` | 95 | 95 | **MATCH** |
| `review` | 120 | 120 | **MATCH** |

**Overall Table Match:** 100% MATCH (11 of 11 tables)

---

## 2. Arabic Character-by-Character Round-Trip Verification

All Arabic strings in the MySQL dump round-trip cleanly without mojibake or character degradation:

| Table | English Identifier | Expected Arabic | Restored Arabic | Codepoint Verification |
| :--- | :--- | :--- | :--- | :--- |
| `location` | New Administrative Capital | العاصمة الإدارية الجديدة | العاصمة الإدارية الجديدة | `MATCH (100%)` |
| `location` | North Coast | الساحل الشمالي | الساحل الشمالي | `MATCH (100%)` |
| `property_type` | Shop | محل | محل | `MATCH (100%)` |
| `property_type` | Office | مكتب | مكتب | `MATCH (100%)` |

---

## 3. Reproduction Commands

To reproduce this exact restore test in MySQL 8.0+:
```bash
# 1. Create clean test database
mysql -u root -p -e "DROP DATABASE IF EXISTS resale_properties_restore_test; CREATE DATABASE resale_properties_restore_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. Restore dump file using native file handling (do NOT use PowerShell `>` redirection)
mysql --default-character-set=utf8mb4 -u root -p resale_properties_restore_test < milestone2/deliverables/resale_properties_dump.sql
```
