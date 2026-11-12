"""
Prepare Remote Dump
Strips DEFINER, DROP/CREATE DATABASE, and USE statements so that the dump
can be safely imported into shared/remote MySQL hosts (e.g. db4free.net, Aiven, Clever Cloud)
without requiring SUPER privileges or specific database creation rights.
"""
import re
from pathlib import Path

SOURCE_DUMP = Path(__file__).resolve().parent.parent.parent / "milestone2" / "deliverables" / "resale_properties_dump.sql"
TARGET_DUMP = Path(__file__).resolve().parent.parent / "deliverables" / "resale_properties_remote_ready.sql"
FINAL_DUMP = Path(__file__).resolve().parent.parent / "deliverables" / "resale_properties_dump_final.sql"

def clean_dump():
    print(f"Reading source dump: {SOURCE_DUMP}")
    if not SOURCE_DUMP.exists():
        raise FileNotFoundError(f"Source dump not found: {SOURCE_DUMP}")

    with open(SOURCE_DUMP, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Strip DEFINER clauses in views and routines cleanly
    # Replace comment-wrapped create view with clean CREATE OR REPLACE VIEW
    content = re.sub(r'/\*!50013 DEFINER=`[^`]+`@`[^`]+`\s+SQL SECURITY DEFINER \*/', '', content)
    content = re.sub(r'DEFINER=`[^`]+`@`[^`]+`', '', content)
    content = re.sub(r'/\*!50001 CREATE ALGORITHM=UNDEFINED \*/\s+/\*!50001 VIEW `', 'CREATE OR REPLACE VIEW `', content)
    content = re.sub(r'/\*!50001 CREATE ALGORITHM=UNDEFINED \*/', '', content)
    content = re.sub(r'/\*!50001 VIEW `', 'CREATE OR REPLACE VIEW `', content)
    content = re.sub(r'\*/\s*;\s*$', ';', content, flags=re.MULTILINE)

    # 2. Strip CREATE DATABASE / DROP DATABASE / USE statements
    content = re.sub(r'(?i)DROP\s+DATABASE\s+IF\s+EXISTS\s+`?[a-zA-Z0-9_]+`?;', '-- [STRIPPED FOR REMOTE HOST] DROP DATABASE', content)
    content = re.sub(r'(?i)CREATE\s+DATABASE\s+.*?;', '-- [STRIPPED FOR REMOTE HOST] CREATE DATABASE', content)
    content = re.sub(r'(?i)USE\s+`?[a-zA-Z0-9_]+`?;', '-- [STRIPPED FOR REMOTE HOST] USE DATABASE', content)

    TARGET_DUMP.parent.mkdir(parents=True, exist_ok=True)
    with open(TARGET_DUMP, "w", encoding="utf-8") as f:
        f.write(content)

    # Also save as final deliverable dump
    with open(FINAL_DUMP, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully generated clean remote-ready dump: {TARGET_DUMP} ({len(content)} bytes)")
    print(f"Successfully generated official final dump deliverable: {FINAL_DUMP} ({len(content)} bytes)")

if __name__ == "__main__":
    clean_dump()
