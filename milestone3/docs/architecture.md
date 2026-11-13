# Milestone III: System Architecture & Data Flow
### CSCE 2501 – Fundamentals of Database Systems – Project: Resale Properties
**Author:** Mennatallah Essam Zaher  
**Instructor:** Prof. Mohamed Alhalaby — The American University in Cairo (AUC)  

---

## 1. High-Level Architecture Overview

The Milestone III application layer is a full-stack, decoupled, database-first web system built in **Python 3.11+ / Flask**, serving a high-performance responsive UI styled with **Tailwind CSS** and dynamic charts via **Chart.js**.

```mermaid
flowchart TD
    Client["Client Browser (Responsive GUI)"] -- HTTP / HTML / REST --> AppServer["Flask Application Layer (Python 3.11+)"]
    
    subgraph AppServer["Flask Application Layer"]
        Guard["Remote Host Security Guard\n(Rejects localhost / 127.0.0.1)"]
        Router["Route Controllers (main.py)"]
        Services["Service Layer (F01 - F10 Services)"]
        SQL["Parameterized SQL Queries (queries.py)\nWhitelist Sort Validation"]
        Pool["PyMySQL Connection Pool & Reconnect Retry"]
    end
    
    AppServer -- "TCP Port 3306 (utf8mb4, Remote Network)" --> RemoteMySQL[("Remote MySQL 8.0+ Database Server\n(db4free.net / Aiven / Remote Host)")]
    
    subgraph RemoteMySQL["Remote MySQL Database"]
        Tables["11 Relational 3NF Tables\n(9,628 Properties, 6,279 Developments)"]
        Indexes["M3 Composite Indexes (m3_changes.sql)"]
        Views["v_property_metrics, v_user_profile"]
    end
```

---

## 2. Request / Response Lifecycle

1. **Startup Host Enforcement:**
   When the Flask application starts, `verify_remote_host()` in `milestone3/app/db.py` inspects `DB_HOST`. If it resolves to `localhost`, `127.0.0.1`, `::1`, or Docker internal hostnames, the application **immediately halts with a fatal exception**, ensuring absolute compliance with course requirements.
2. **Client Request:**
   The user navigates the web application or submits an analytical query (e.g., F06 Area Hierarchy or F07 Multi-Amenity Search).
3. **Dual Validation & Whitelist Sanitization:**
   - User inputs (dates, ratings, IDs) are validated server-side.
   - Dynamic parameters (e.g. `ORDER BY price DESC`) are checked against strict hardcoded whitelists in `ALLOWED_SORT_COLUMNS` to prevent SQL injection.
4. **Parameterized Query Execution:**
   The query is executed over the remote network connection via `PyMySQL` with `autocommit=False`, parameterized arguments (`%s`), and automatic retry on network drops.
5. **View Rendering:**
   Data is transformed into Jinja2 templates, numbers formatted with thousand separators, and rendered with RTL Arabic font support.

---

## 3. Transaction Flow: F01 User Registration

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant App as Flask Controller (main.py)
    participant Svc as UserService (user_service.py)
    participant DB as Remote MySQL Server

    User->>App: POST /f01-register (username, email, birthdate, [focus_areas])
    App->>Svc: register_user(...)
    Svc->>Svc: Validate email regex, age consistency, past date
    Svc->>DB: BEGIN TRANSACTION
    Svc->>DB: SELECT user_id FROM app_user WHERE email=? OR username=?
    alt Already Exists
        DB-->>Svc: Found duplicate
        Svc-->>App: Return user-friendly error
        App-->>User: Display "Username/Email already taken"
    else Available
        Svc->>DB: INSERT INTO app_user (username, email, gender, birthdate)
        DB-->>Svc: user_id = LAST_INSERT_ID()
        loop For Each Selected Focus Area
            Svc->>DB: INSERT INTO user_focus_area (user_id, location_id)
        end
        Svc->>DB: COMMIT TRANSACTION
        Svc->>DB: SELECT * FROM v_user_profile WHERE user_id = ?
        DB-->>Svc: Profile with dynamically computed age
        Svc-->>App: Registration Success
        App-->>User: 200 OK + Confirmation Badge
    end
```
