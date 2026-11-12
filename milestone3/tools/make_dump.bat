@echo off
setlocal

set MYSQLDUMP_PATH="C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"
if not exist %MYSQLDUMP_PATH% (
    set MYSQLDUMP_PATH=mysqldump
)

set TARGET_DUMP=milestone3\deliverables\resale_properties_dump_final.sql

echo [+] Creating clean UTF-8 database dump...
%MYSQLDUMP_PATH% --host=127.0.0.1 --port=3306 --user=root --password=password ^
    --single-transaction --routines --triggers --default-character-set=utf8mb4 ^
    --set-gtid-purged=OFF --result-file=%TARGET_DUMP% resale_properties

echo [+] Sanitizing dump for remote hosting (stripping DEFINER and local DB statements)...
python -m milestone3.tools.prepare_remote_dump

echo [✓] Successfully created final deliverable dump at %TARGET_DUMP%
pause
