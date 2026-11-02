import os
import sys
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def run_step(step_name, cmd):
    print("\n" + "=" * 80)
    print(f"STEP: {step_name}")
    print("=" * 80)
    t0 = time.time()
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"FAILED: {step_name} exited with code {res.returncode}")
        return False
    print(f"SUCCESS: {step_name} completed in {time.time() - t0:.2f}s")
    return True

def main():
    print("================================================================================")
    print("           AQAREXIT END-TO-END PIPELINE: FULL RE-INGESTION & SUBMISSION        ")
    print("================================================================================\n")

    # Step 1: Parse all downloaded listings
    if not run_step("Offline Parsing of All Raw Listings", [sys.executable, "-m", "milestone2.parsing.parse_listing", "--all"]):
        return

    # Step 2: Database Schema & Ingestion
    if not run_step("MySQL Database Ingestion (Topological Load)", [sys.executable, "-m", "milestone2.load.load_db", "--init"]):
        return

    # Step 3: Seed Synthetic Users & Reviews
    if not run_step("Seed Synthetic Users & Reviews (Seed 2501)", [sys.executable, "-m", "milestone2.load.seed_users"]):
        return

    # Step 4: Export CSVs & Manifest
    if not run_step("Export UTF-8 BOM CSVs & Manifest", [sys.executable, "-m", "milestone2.load.export_csv"]):
        return

    # Step 5: Export UTF-8 mysqldump
    mysqldump_bin = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"
    dump_out = str(BASE_DIR / "deliverables" / "resale_properties_dump.sql")
    dump_cmd = f'"{mysqldump_bin}" --single-transaction --routines --triggers --default-character-set=utf8mb4 --set-gtid-purged=OFF --result-file="{dump_out}" -h 127.0.0.1 -P 3306 -u root -ppassword resale_properties'
    if not run_step("Export Pure UTF-8 MySQL Dump", dump_cmd):
        return

    # Step 6: Mandatory Restore Test
    if not run_step("Mandatory Restore Verification Test", [sys.executable, "milestone2/deliverables/restore_test.py"]):
        return

    # Step 7: Quality Report & Smoke Queries
    if not run_step("Generate Quality Report", [sys.executable, "-m", "milestone2.validate.quality_report"]):
        return
    if not run_step("Run Analytical Smoke Queries", [sys.executable, "-m", "milestone2.validate.run_smoke_queries"]):
        return

    # Step 8: Unit Tests
    if not run_step("Run Automated Unit Tests", [sys.executable, "-m", "unittest", "milestone2/parsing/tests/test_parsers.py"]):
        return

    print("\n" + "=" * 80)
    print("ALL PIPELINE STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()

