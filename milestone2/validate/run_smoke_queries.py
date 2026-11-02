import sys
from pathlib import Path
import pymysql

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from milestone2.config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    BASE_DIR
)

def run_smoke_queries():
    sql_file = BASE_DIR / "validate" / "m3_smoke_queries.sql"
    output_file = BASE_DIR / "validate" / "m3_smoke_queries_output.txt"

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

    with open(sql_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split queries by double dash comments marking query headers
    import re
    queries = re.split(r"-- -{70,}\n-- Query \d+:", content)
    
    out_lines = [
        "================================================================================",
        "CSCE 2501 – Fundamentals of Database Systems – Milestone II Validation",
        "Milestone III Analytical Smoke Queries Execution Transcript",
        "Database: resale_properties (MySQL 8.0, InnoDB, utf8mb4)",
        "Generated on: 2026-11-02",
        "================================================================================\n"
    ]

    for q_idx, q_block in enumerate(queries[1:], 1):
        lines = q_block.strip().split("\n")
        title = lines[0].strip()
        # Find the actual SQL query
        sql_lines = [l for l in lines[1:] if not l.strip().startswith("--")]
        sql = "\n".join(sql_lines).strip()
        if not sql:
            continue

        out_lines.append(f"--------------------------------------------------------------------------------")
        out_lines.append(f"QUERY {q_idx}: {title}")
        out_lines.append(f"--------------------------------------------------------------------------------")
        out_lines.append("SQL Statement:")
        out_lines.append(sql + "\n")
        out_lines.append("Execution Result (First 10 rows):")

        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            if not rows:
                out_lines.append("(No rows returned)\n")
                continue

            headers = list(rows[0].keys())
            # Format as text table
            col_widths = {h: max(len(h), max(len(str(r[h])) for r in rows)) for h in headers}
            header_str = " | ".join(f"{h:<{col_widths[h]}}" for h in headers)
            sep_str = "-+-".join("-" * col_widths[h] for h in headers)
            out_lines.append(header_str)
            out_lines.append(sep_str)
            for r in rows:
                row_str = " | ".join(f"{str(r[h]):<{col_widths[h]}}" for h in headers)
                out_lines.append(row_str)
            out_lines.append(f"\n({len(rows)} row(s) returned)\n")
        except Exception as e:
            out_lines.append(f"ERROR: {e}\n")

    conn.close()

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))

    # Also copy to deliverables/crawler/validate/
    deliv_output = BASE_DIR / "deliverables" / "crawler" / "validate" / "m3_smoke_queries_output.txt"
    deliv_output.parent.mkdir(parents=True, exist_ok=True)
    with open(deliv_output, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))

    print(f"Smoke queries output generated -> {output_file}")

if __name__ == "__main__":
    run_smoke_queries()

