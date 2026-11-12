#!/usr/bin/env bash
set -e

echo "=============================================================================="
echo " AqarExit Resale Analytics - Milestone III Application Launcher"
echo "=============================================================================="

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "[!] .env not found. Copying .env.example to .env..."
        cp .env.example .env
        echo "[!] Please configure milestone3/.env with your remote MySQL credentials."
    fi
fi

# Create venv if not present
if [ ! -d "venv" ]; then
    echo "[+] Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "[+] Installing requirements..."
pip install -r requirements.txt --quiet

# Open browser in background
if command -v xdg-open > /dev/null; then
    (sleep 3 && xdg-open http://127.0.0.1:5000) &
elif command -v open > /dev/null; then
    (sleep 3 && open http://127.0.0.1:5000) &
fi

# Start app
echo "[+] Starting application server..."
python -m milestone3.app.main "$@"
