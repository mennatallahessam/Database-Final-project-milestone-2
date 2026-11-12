@echo off
setlocal enabledelayedexpansion

echo ==============================================================================
echo  AqarExit Resale Analytics - Milestone III Application Launcher
echo ==============================================================================

:: Check for .env file
if not exist ".env" (
    if exist ".env.example" (
        echo [!] .env not found. Copying .env.example to .env...
        copy ".env.example" ".env" >nul
        echo [!] Please update milestone3/.env with your real remote MySQL database credentials.
    )
)

:: Create virtual environment if missing
if not exist "venv" (
    echo [+] Creating Python virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install dependencies
echo [+] Checking and installing requirements...
pip install -r requirements.txt --quiet

:: Launch web browser in 3 seconds
start "" cmd /c "timeout /t 3 >nul && start http://127.0.0.1:5000"

:: Start Flask server (Pass any CLI arguments e.g. --allow-local)
echo [+] Starting application server...
python -m milestone3.app.main %*

pause
