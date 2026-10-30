import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
EXPORTS_DIR = DATA_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"
DELIVERABLES_DIR = BASE_DIR / "deliverables"
CSV_DIR = DELIVERABLES_DIR / "csv"

# Ensure runtime directories exist
for p in [RAW_DIR, STAGING_DIR, EXPORTS_DIR, LOGS_DIR, CSV_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Helper to load .env manually if python-dotenv is not installed
env_file = BASE_DIR / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

# Database configuration
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "resale_properties")

# Crawler politeness and network settings
CRAWL_MIN_DELAY = float(os.getenv("CRAWL_MIN_DELAY", "2.5"))
CRAWL_MAX_DELAY = float(os.getenv("CRAWL_MAX_DELAY", "5.0"))
CRAWL_TIMEOUT_CONNECT = int(os.getenv("CRAWL_TIMEOUT_CONNECT", "10"))
CRAWL_TIMEOUT_READ = int(os.getenv("CRAWL_TIMEOUT_READ", "30"))
CRAWL_MAX_RETRIES = int(os.getenv("CRAWL_MAX_RETRIES", "3"))
CRAWL_BACKOFF_FACTOR = float(os.getenv("CRAWL_BACKOFF_FACTOR", "2.0"))
CRAWL_MAX_CONSECUTIVE_BLOCKS = int(os.getenv("CRAWL_MAX_CONSECUTIVE_BLOCKS", "3"))
CRAWL_USER_AGENT = os.getenv(
    "CRAWL_USER_AGENT",
    "CSCE2501-AUC-StudentProject/1.0 (academic research; contact: student@aucegypt.edu)"
)

# Crawl Scope Tunables
CRAWL_DEFAULT_LIMIT = int(os.getenv("CRAWL_DEFAULT_LIMIT", "60"))

