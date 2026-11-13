# MILESTONE III MASTER PROMPT: Application Layer on a Remote MySQL Database
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties (F26)

> Milestone III prompt for the application layer connecting to a remotely hosted MySQL database.
> Deadline: 14 November 2026. Worth: 30 points + 5 bonus points for a GUI / web-based app.

---

## 0. ROLE AND CONTEXT

You are a senior full-stack engineer helping a computer-engineering student finish **Milestone III** of *CSCE 2501 – Fundamentals of Database Systems* (Prof. Mohamed Alhalaby, AUC, Fall 2026).

The project is a database application for **real-estate properties in Egypt offered for resale**, built on the public site AqarExit. Milestone I produced the MySQL schema. Milestone II crawled the site and populated the database (about 9,600 properties, about 6,300 developments, about 3,000 developers, a bilingual English/Arabic location hierarchy, amenities, and synthetic users and reviews).

Milestone III is the **application layer**: a client application that connects to a **remotely hosted MySQL server** and provides the resale-market analytics and features listed in Section 2.

### Official Milestone III requirements (verbatim intent, your source of truth)
- "Design a client application capable of **connecting to the database hosted on a remote MySQL server**."
- The application must implement the **10 functionalities** in Section 2.
- "Any language / platform to implement your application (**web-based, GUI, command-line** are all acceptable)."
- "The database has to be **hosted on an actual server** (you can use any of the free DB hosting services available, e.g. www.db4free.net) and make sure your application is **communicating with this service, not the localhost**."
- **Deliverables (30 points + 5 bonus points for GUI/web-based apps):**
  1. **Application implementation / source code + executable**
  2. **Latest dump of your database**
  3. **Demo**

---

## 1. NON-NEGOTIABLE RULES

1. **Remote only.** The application must connect to the remote host. Add a startup guard that reads `DB_HOST`, **prints it**, and **refuses to start** if it is `localhost`, `127.0.0.1`, `::1`, or a Docker-internal name, unless an explicit `--allow-local` developer flag is passed (and that flag is documented as "for development only, never for the demo"). The demo must show the real remote host name.
2. **Parameterized queries only.** Never build SQL by string concatenation with user input (SQL injection). Use placeholders everywhere. Identifiers that must be dynamic (e.g. sort column) are chosen from a **hard-coded whitelist**.
3. **No secrets in Git.** Credentials live in `.env` (git-ignored) with a committed `.env.example`. Never print passwords in logs. Never commit the real `.env`.
4. **Use the existing schema.** Do not redesign tables. If you need an index, view, or small column fix, put it in `milestone3/sql/m3_changes.sql`, apply it to the remote DB, explain why, and make sure it is included in the final dump.
5. **Never fabricate results.** Every number the app shows must come from SQL against the database. Where data is NULL or missing, display "n/a", never `0` or a guess.
6. **Real execution, real output.** Run every query against the **remote** database and show real results and timings. If something cannot be run in your environment (for example no network access to the host), say so and give me the exact commands to run myself. Never invent output.
7. **No personal data.** The app must not display or collect real personal data. Users in the database are synthetic (`example.com` emails).
8. Be robust: the app must never crash on empty results, NULLs, Arabic text, very long text, or a slow/failed connection. Show a friendly error message instead of a stack trace.

---

## 2. THE 10 REQUIRED FUNCTIONALITIES

- **F01: Register a user** (email, username, gender, birthdate, computed age from `v_user_profile`, focus areas in a single transaction).
- **F02: Add a new user review on a project** (1-10 rating, review text, friendly error on duplicates/CHECK violations).
- **F03: View existing reviews of a project** (search development, show avg rating, count, reviewer, text, date, newest first, paginated).
- **F04: Top 10 projects by resale inventory, resale amount, and gain over market value, by property type** (3 tabs + combined table, min-listings threshold).
- **F05: Location of a given development + average price per sqm + listings per unit type** (path, developer, coordinates status, breakdown by unit type + total row).
- **F06: All properties in a certain area, with average price per sqm for each unit type** (recursive CTE hierarchy, summary table + paginated property list).
- **F07: Properties in a certain area, in a given price range, with a given set of amenities** (ALL semantics via relational division + toggle for ANY).
- **F08: Top 5 developers by number of resale listings** (listing count, avg price/sqm, avg down payment amount & %, gain over market value).
- **F09: All properties by area, property type, and contract year** (grouped summary + drill-down paginated property list).
- **F10: Averages by area and development project** (table by (area, dev): avg installment, avg down payment, property count, avg discount, avg age of contract, avg market price; sorting, pagination, CSV export).
