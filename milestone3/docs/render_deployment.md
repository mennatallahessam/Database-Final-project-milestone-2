# Deploying AqarExit Analytics App on Render (render.com)

This guide provides instructions to deploy the Milestone III Flask application to **[Render](https://render.com)**.

---

## 1. Prerequisites
1. A GitHub account with access to this repository: `Database-Final-project-milestone-2`.
2. A free account on **[Render](https://render.com)**.
3. A remotely hosted MySQL 8.0 database (e.g., [db4free.net](https://www.db4free.net), [TiDB Cloud Serverless Free Tier](https://tidbcloud.com), [Aiven](https://aiven.io), or [Clever Cloud](https://www.clever-cloud.com)) containing the imported dump from:
   `milestone3/deliverables/resale_properties_dump_final.sql`

---

## 2. Option A: Instant Blueprint Deploy (Recommended)
This repository includes a `render.yaml` blueprint file for setup.

1. Go to your **[Render Dashboard](https://dashboard.render.com/)**.
2. Click **New +** in the top navigation bar and select **Blueprint**.
3. Connect your GitHub repository: `Database-Final-project-milestone-2`.
4. Render will detect `render.yaml` and configure the Web Service (`aqarexit-analytics`).
5. Fill in your remote database environment variables when prompted:
   * `DB_HOST`: Hostname of your remote MySQL database (e.g., `db4free.net` or `gateway01.us-east-1.prod.aws.tidbcloud.com`).
   * `DB_PORT`: Database port (default `3306` or `4000` for TiDB).
   * `DB_USER`: Remote database user.
   * `DB_PASSWORD`: Remote database password.
   * `DB_NAME`: Remote database name.
   * `DB_SSL`: `true` if your remote provider requires TLS (e.g., TiDB Cloud/Aiven), `false` for db4free.net.
6. Click **Apply**. Render will automatically build and start the service with Gunicorn!

---

## 3. Option B: Manual Web Service Setup
If you prefer creating the Web Service manually:

1. In Render Dashboard, click **New +** → **Web Service**.
2. Select **Build and deploy from a Git repository** and pick your repo.
3. Configure the following settings:
   * **Name:** `aqarexit-analytics` (or any name you like)
   * **Region:** Frankfurt (EU) or Oregon (US)
   * **Branch:** `main`
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `gunicorn wsgi:app`
   * **Instance Type:** `Free`
4. Under **Environment Variables**, add:
   | Key | Value | Description |
   |---|---|---|
   | `DB_HOST` | `your-remote-host.com` | **Must be remote host** (e.g., `db4free.net`). `localhost` is rejected! |
   | `DB_PORT` | `3306` | MySQL port |
   | `DB_USER` | `your_remote_user` | MySQL username |
   | `DB_PASSWORD` | `your_remote_password`| MySQL password |
   | `DB_NAME` | `your_remote_database`| MySQL database name |
   | `DB_SSL` | `false` (or `true`) | Set to `true` if your provider enforces TLS/SSL |
   | `APP_SECRET` | *(Random string)* | Flask session signing secret |
   | `PYTHON_VERSION`| `3.11.9` | Recommended Python version |
5. Click **Create Web Service**.

---

## 4. Verification & Health Check
* Once Render finishes building, your app will be live at:
  `https://<your-service-name>.onrender.com`
* The startup security guard checks the remote database host and logs:
  ```
  🔒 MILESTONE III: REMOTE DATABASE HOST VERIFICATION
  Target Database Host: your-remote-host.com:3306
  ✓ Remote Host Verified: Non-local host validated successfully
  ```
* You can test all 10 functionalities directly in your browser or during your project presentation.
