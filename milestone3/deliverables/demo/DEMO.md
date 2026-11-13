# Milestone III: Live Demo Script & Walkthrough (5–8 Minutes)
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties
**Author:** Mennatallah Essam Zaher  
**Instructor:** Prof. Mohamed Alhalaby — The American University in Cairo (AUC)  

---

## Demo Script Overview

| Step | Time | Functionality | Exact Demo Inputs | Key Point to Explain to Grader / Instructor |
| :---: | :---: | :--- | :--- | :--- |
| **1** | 0:00–0:45 | **Remote Host Proof** | Application Footer / Startup Log | Point out footer badge displaying `Connected Remote Host: db4free.net`. Explain the startup guard refusing localhost. |
| **2** | 0:45–1:45 | **F01: User Registration** | • Username: `karim_auc`<br>• Email: `karim@example.com`<br>• Birthdate: `1998-05-12`<br>• Areas: *New Cairo*, *Sheikh Zayed* | First submit with duplicate username to show clean error mapping; then register. Highlight atomic transaction and dynamic age derived via view `v_user_profile` (28 yrs). |
| **3** | 1:45–2:30 | **F02 & F03: Project Reviews** | • Search: `Patio Vida` or `Badya`<br>• Rating: `9`<br>• Text: *Great compound location and amenities.* | Submit review; app transitions to F03 showing the newly submitted review at the top with updated project average rating and reviewer username. |
| **4** | 2:30–3:30 | **F04: Top 10 Projects by Type** | • Type: `Apartment` (`شقة`)<br>• Min listings: `3`<br>• Outlier filter: `ON` | Switch between the 3 tabs: (1) Resale Inventory, (2) Resale Capital, (3) Gain Over Market Value. Show Chart.js bar graph. |
| **5** | 3:30–4:15 | **F05: Development Deep Dive** | • Search: `Rivers` or `Zed Towers` | Show full location breadcrumb (*Giza → Sheikh Zayed*), developer name, unit types breakdown table with 'All Types' total row, and explain that coordinates are strictly `NULL` where not published on AqarExit. |
| **6** | 4:15–5:00 | **F06 & F07: Area Hierarchy & Amenities** | • Area: `Cairo` (`القاهرة`)<br>• Price: `2,000,000` to `10,000,000`<br>• Amenities: `Security`, `Pool` | Demonstrate Recursive CTE gathering sub-areas. In F07, show **relational division** toggle: `ALL Selected` vs `ANY Selected`. |
| **7** | 5:00–5:45 | **F08: Top 5 Developers** | • Filter: `All Types` | Show market leaders (e.g. Palm Hills, SODIC), listing counts, average price/sqm, required down payment %, and Chart.js bar chart. |
| **8** | 5:45–6:30 | **F09: Area × Type × Year Matrix** | • Area: `Giza`<br>• Year: `2024` | Grouped multi-dimensional matrix showing property clusters and drill-down links to view individual listings. |
| **9** | 6:30–7:15 | **F10: Area & Development Averages** | • Min Properties: `3`<br>• Sort: `property_count` | Point out non-NULL sample contribution counts (`(12/15)`) preventing misleading averages. Click **⬇ Export CSV** to download `aqarexit_f10_benchmark_averages.csv`. |
| **10** | 7:15–8:00 | **Deliverables & Wrap-Up** | `resale_properties_dump_final.sql`, `restore_check.md` | Close by showing clean SQL dump, unit test suite passing 100%, and architectural design decisions. |

---

## Fallback Plan (If Remote Free Host Has Connectivity Outage During Demo)
Free MySQL hosts (like `db4free.net`) occasionally experience transient downtime or maintenance. If the remote host is unreachable during a live evaluation:
1. Show the friendly "Remote Database Unreachable" error page in the app, demonstrating that the application is genuinely connecting to the remote host over the network.
2. Run `python -m milestone3.app.main --allow-local` to show the exact same database restored locally from `resale_properties_remote_ready.sql`. Clearly state that this is the approved offline demonstration fallback.
