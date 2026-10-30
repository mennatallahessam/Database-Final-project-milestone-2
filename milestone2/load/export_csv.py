import csv
import os
from decimal import Decimal
from datetime import datetime, date
from pathlib import Path
import pymysql

from milestone2.config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    CSV_DIR
)

TABLES = [
    "property_type",
    "payment_method",
    "amenity",
    "location",
    "developer",
    "development",
    "property",
    "property_amenity",
    "app_user",
    "user_focus_area",
    "review"
]

def format_cell_value(val):
    """Formats cell values according to strict assignment specifications."""
    if val is None:
        return ""
    if isinstance(val, Decimal):
        # Plain number string, strip trailing zeros if appropriate or format as decimal
        return f"{val:f}"
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    return str(val)

def export_all_tables_to_csv():
    """Exports every MySQL table to deliverables/csv/<table>.csv with UTF-8 BOM."""
    CSV_DIR.mkdir(parents=True, exist_ok=True)

    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    manifest_rows = []
    print(f"Exporting tables from {DB_NAME} to {CSV_DIR} (UTF-8 BOM)...")

    for tbl in TABLES:
        csv_file = CSV_DIR / f"{tbl}.csv"
        
        # Get row count from DB
        cursor.execute(f"SELECT COUNT(*) as cnt FROM `{tbl}`")
        db_count = cursor.fetchone()["cnt"]

        # Fetch all rows
        cursor.execute(f"SELECT * FROM `{tbl}`")
        rows = cursor.fetchall()

        fieldnames = []
        if cursor.description:
            fieldnames = [d[0] for d in cursor.description]

        # Write with utf-8-sig (UTF-8 with BOM)
        with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(fieldnames)
            for row in rows:
                formatted_row = [format_cell_value(row[col]) for col in fieldnames]
                writer.writerow(formatted_row)

        file_size = csv_file.stat().st_size
        csv_row_count = len(rows)
        match_status = "MATCH" if csv_row_count == db_count else "MISMATCH"

        manifest_rows.append({
            "table_name": tbl,
            "db_row_count": db_count,
            "csv_row_count": csv_row_count,
            "file_size_bytes": file_size,
            "status": match_status
        })

        print(f" -> {tbl}.csv: {csv_row_count} rows ({file_size} bytes) [{match_status}]")

    # Write _manifest.csv
    manifest_file = CSV_DIR / "_manifest.csv"
    with open(manifest_file, "w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["table_name", "db_row_count", "csv_row_count", "file_size_bytes", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_rows)

    conn.close()
    print(f"\nManifest written to {manifest_file}")

if __name__ == "__main__":
    export_all_tables_to_csv()

