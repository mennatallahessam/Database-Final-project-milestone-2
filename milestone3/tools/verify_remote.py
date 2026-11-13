"""
Milestone III: Remote Database Connectivity & Latency Audit Tool
CSCE 2501 – Fundamentals of Database Systems – Prof. Mohamed Alhalaby (AUC)

Connects to the remote MySQL server specified in milestone3/.env,
measures real network ping & query roundtrip latencies,
and verifies table row counts to prove remote hosting compliance.
"""
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import pymysql
from tabulate import tabulate

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

def verify_remote_database(allow_local: bool = False):
    host = os.getenv("DB_HOST", "").strip()
    port = int(os.getenv("DB_PORT", "3306"))
    user = os.getenv("DB_USER", "").strip()
    password = os.getenv("DB_PASSWORD", "").strip()
    database = os.getenv("DB_NAME", "").strip()
    ssl_enabled = os.getenv("DB_SSL", "false").lower() in ("true", "1", "yes")

    print("\n" + "=" * 70)
    print("🌐 MILESTONE III: REMOTE MYSQL DATABASE AUDIT & COMPLIANCE CHECK")
    print(f"Target Server Host: {host}:{port}")
    print(f"Remote Database:    {database}")
    print(f"Database User:      {user}")
    print("=" * 70)

    if not host or not database:
        print("\n❌ CONFIGURATION ERROR: DB_HOST or DB_NAME is missing in milestone3/.env!")
        print("Please configure milestone3/.env with your remote MySQL credentials.")
        sys.exit(1)

    # Check for localhost / local loopback
    is_local = host.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0", "host.docker.internal")
    if is_local:
        if allow_local or "--allow-local" in sys.argv:
            print("\n⚠️  [OFFLINE DEV MODE]: Connected to localhost because --allow-local is active.")
            print("⚠️  REMINDER: The final course evaluation and demo must run against a remote host!")
        else:
            print(f"\n❌ AUDIT FAILED: DB_HOST is set to '{host}'.")
            print("Per Milestone III Rule 1, you must connect to an actual remote host (e.g. db4free.net, TiDB Cloud, Aiven).")
            print("To run this audit against a local database for offline testing only, pass --allow-local.")
            sys.exit(1)
    else:
        print(f"✓ Remote Host Validated: '{host}' is an external remote server (Not localhost).")

    # Connect to MySQL with latency measurement
    ssl_config = {}
    if ssl_enabled:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ssl_config = {"ssl": ctx}

    print("\n[1/3] Establishing connection to remote database...")
    t0 = time.perf_counter()
    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password, database=database,
            charset="utf8mb4", connect_timeout=15, read_timeout=30, write_timeout=30,
            **ssl_config
        )
        t_connect = (time.perf_counter() - t0) * 1000
        print(f"✓ TCP Handshake & Authentication Successful! (Latency: {t_connect:.1f} ms)")
    except Exception as e:
        print(f"\n❌ CONNECTION FAILED: Unable to reach {host}:{port}")
        print(f"Error details: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your remote host, user, and password in milestone3/.env.")
        print("2. Confirm the remote MySQL server is running and port 3306 is open.")
        print("3. Ensure your IP address is whitelisted if your cloud provider has a firewall.")
        sys.exit(1)

    cursor = conn.cursor()

    # Verify Table Row Counts
    print("\n[2/3] Verifying table row counts against assignment specification...")
    expected_tables = [
        ("property", 9628),
        ("development", 6279),
        ("developer", 3056),
        ("location", 207),
        ("property_amenity", 37382),
        ("amenity", 10),
        ("property_type", 11),
        ("payment_method", 2),
        ("review", 120),
        ("app_user", 40),
        ("user_focus_area", 95)
    ]

    results_table = []
    all_matched = True

    for table, expected in expected_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`;")
            count = cursor.fetchone()[0]
            # Users and focus areas can be >= initial count due to registrations
            is_valid = (count >= expected) if table in ("app_user", "user_focus_area", "review") else (count == expected)
            status = "✓ MATCH" if is_valid else f"MISMATCH ({count})"
            if not is_valid:
                all_matched = False
            results_table.append([table, expected, count, status])
        except Exception as e:
            results_table.append([table, expected, "ERROR", str(e)])
            all_matched = False

    print(tabulate(results_table, headers=["Table", "Expected", "Remote Count", "Status"], tablefmt="github"))

    # Test an analytical query and measure remote execution latency
    print("\n[3/3] Testing analytical query latency across network...")
    sample_queries = [
        ("Simple Ping Query (SELECT 1)", "SELECT 1;"),
        ("Top 5 Developers (F08)", """
            SELECT dev.name, COUNT(p.property_id) AS cnt 
            FROM property p 
            JOIN development d ON p.development_id = d.development_id 
            JOIN developer dev ON d.developer_id = dev.developer_id 
            GROUP BY dev.developer_id, dev.name 
            ORDER BY cnt DESC LIMIT 5;
        """),
        ("Location Tree Recursive CTE (F06)", """
            WITH RECURSIVE AreaHierarchy AS (
                SELECT location_id FROM location WHERE location_id = 20
                UNION ALL
                SELECT l.location_id FROM location l
                INNER JOIN AreaHierarchy ah ON l.parent_location_id = ah.location_id
            )
            SELECT COUNT(*) FROM property WHERE location_id IN (SELECT location_id FROM AreaHierarchy);
        """)
    ]

    perf_table = []
    for q_name, q_sql in sample_queries:
        t_start = time.perf_counter()
        cursor.execute(q_sql)
        _ = cursor.fetchall()
        t_exec = (time.perf_counter() - t_start) * 1000
        perf_table.append([q_name, f"{t_exec:.1f} ms"])

    print(tabulate(perf_table, headers=["Query Name", "Measured Remote Latency"], tablefmt="github"))

    cursor.close()
    conn.close()

    print("\n" + "=" * 70)
    if all_matched:
        print("🎉 AUDIT PASSED: Remote database is fully populated and ready for demo!")
    else:
        print("⚠️ AUDIT WARNING: Some table counts did not match expected values.")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    allow_local_flag = "--allow-local" in sys.argv
    verify_remote_database(allow_local=allow_local_flag)
