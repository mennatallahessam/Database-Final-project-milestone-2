# Milestone III: Live Demo Script & Walkthrough (5–8 Minutes)
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties
**Author:** Mennatallah Essam Zaher  
**Instructor:** Prof. Mohamed Alhalaby — The American University in Cairo (AUC)  

---

## 1. Recorded Video Demo Walkthrough

A complete, high-definition recording of the live application demonstrating all 10 project functionalities is included in this directory:

* **Video File:** [`aqarexit_milestone3_demo.mp4`](aqarexit_milestone3_demo.mp4) (H.264 / AAC, 1440x900 HD, 6.09 MB)
* **Automated Recorder Script:** [`milestone3/tools/record_demo.py`](../../tools/record_demo.py)

### Video Recording Timeline & Functionalities Shown:
| Timestamp | Scene / Feature | What Is Demonstrated |
| :---: | :--- | :--- |
| **0:00–0:10** | **Executive Dashboard** | Live database counters (9,628 properties, 6,279 developments, 3,056 developers, 207 areas), luminous UI, and quick feature CTA shortcuts. |
| **0:10–0:16** | **Navigation Dropdowns** | Interactive hover & click navigation menus for *Market Analytics* and *Account & Reviews*. |
| **0:16–0:24** | **F01: User Registration** | Completing registration with multi-select focus areas; atomic transaction confirmation showing dynamic derived age (`Derived Age: 28`). |
| **0:24–0:33** | **F02 & F03: Project Reviews** | Community reviews for *Patio Vida*, submitting 9/10 score, updated project statistics and rating display. |
| **0:33–0:42** | **F04: Top 10 Projects** | 3-way ranking tabs (*Resale Inventory*, *Resale Capital*, *Gain Over Market Value*) and interactive Chart.js bar graphs. |
| **0:42–0:48** | **F05: Development Deep Dive** | Full location breadcrumb (*Giza -> 6th of October -> Badya*), developer name, coordinates status, and unit type breakdown table with total row. |
| **0:48–0:55** | **F06: Area Hierarchy (Recursive CTE)** | Recursive Common Table Expression traversing New Cairo hierarchy with sortable properties table. |
| **0:55–1:02** | **F07: Amenities Multi-Filter** | Relational division query enforcing `ALL` selected amenities with toggle for `ANY`. |
| **1:02–1:07** | **F08: Top 5 Developers** | Market leader rankings by listing inventory, price/sqm, required down payment %, and capital. |
| **1:07–1:12** | **F09: Area × Type × Year Matrix** | Multi-dimensional matrix slicing resale opportunities across geographic areas, property types, and contract vintage years. |
| **1:12–1:15** | **F10: Benchmark Averages & CSV Export** | Benchmark averages with sample contribution counts (`(12/15)`) and single-click UTF-8 BOM CSV export. |
| **1:15–1:18** | **Wrap-Up & Remote Proof** | Return to dashboard, scrolling down to the footer displaying the remote database host verification badge. |

---

## 2. Live Demo Script & Walkthrough (For Live Presentation)

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

## 3. Fallback Plan (If Remote Free Host Has Connectivity Outage During Demo)
Free MySQL hosts (like `db4free.net`) occasionally experience transient downtime or maintenance. If the remote host is unreachable during a live evaluation:
1. Show the friendly "Remote Database Unreachable" error page in the app, demonstrating that the application is genuinely connecting to the remote host over the network.
2. Run `python -m milestone3.app.main --allow-local` to show the exact same database restored locally from `resale_properties_dump_final.sql`. Clearly state that this is the approved offline demonstration fallback.

---

## 4. Demo Evidence Screenshots Catalog
The following high-resolution verification screenshots of the live application are available in [`milestone3/deliverables/demo/screenshots/`](screenshots/):

* `00_dashboard.png`: Executive Dashboard with live metrics counters (9,628 properties, 6,279 developments, 3,056 developers).
* `01_f01_registration.png`: User registration form with dynamic focus area selection and age derivation.
* `02_f02_f03_reviews.png`: Project review submission and paginated community reviews list.
* `03_f04_top_projects.png`: Top 10 development projects ranked by resale inventory, capital, and market gain.
* `04_f05_dev_deep_dive.png`: Development deep-dive showing full geographic path, developer, and property type breakdown.
* `05_f06_area_properties.png`: Area hierarchy property listings with Recursive Common Table Expression traversal.
* `06_f07_amenities_filter.png`: Multi-amenity filtering with relational division toggle (`ALL` vs `ANY`).
* `07_f08_top_developers.png`: Market leader rankings by resale listing inventory and financial averages.
* `07_f08_top_developers.png`: Top 5 developers by inventory and average price per sqm.
* `08_f09_matrix_slicing.png`: Multi-dimensional Area × Property Type × Contract Signing Year analytical matrix.
* `09_f10_benchmark_averages.png`: Area & development benchmark averages with non-NULL sample verification and single-click CSV export.
