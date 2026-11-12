#!/usr/bin/env bash
set -e

TARGET_DUMP="milestone3/deliverables/resale_properties_dump_final.sql"

echo "[+] Creating clean UTF-8 database dump..."
mysqldump --single-transaction --routines --triggers --default-character-set=utf8mb4 \
    --set-gtid-purged=OFF --result-file="${TARGET_DUMP}" \
    -h "${DB_HOST:-127.0.0.1}" -P "${DB_PORT:-3306}" -u "${DB_USER:-root}" -p "${DB_NAME:-resale_properties}"

echo "[+] Sanitizing dump for remote hosting..."
python3 -m milestone3.tools.prepare_remote_dump

echo "[✓] Final dump generated at ${TARGET_DUMP}"
