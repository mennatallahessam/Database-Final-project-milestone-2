"""
Database Connection & Security Guard Module
Enforces strict remote-host connection policies, manages connection pooling,
retries transient connection failures, and ensures utf8mb4 encoding across all queries.
"""
import os
import sys
import time
import logging
from contextlib import contextmanager
from pathlib import Path
from dotenv import load_dotenv
import pymysql
import pymysql.cursors

# Load environment configuration
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

logger = logging.getLogger("milestone3.db")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Remote Host Guard definitions
FORBIDDEN_LOCAL_HOSTS = {
    "localhost",
    "127.0.0.1",
    "::1",
    "0.0.0.0",
    "host.docker.internal",
    "mysql",
    "db",
    "local"
}

def verify_remote_host(allow_local: bool = False):
    """
    Startup Security Guard:
    Reads DB_HOST, prints it, and refuses to start if it points to a local machine.
    """
    host = os.getenv("DB_HOST", "").strip()
    port = os.getenv("DB_PORT", "3306").strip()
    
    print("\n" + "=" * 60)
    print("🔒 MILESTONE III: REMOTE DATABASE HOST VERIFICATION")
    print(f"Target Database Host: {host}:{port}")
    print("=" * 60)
    
    if not host:
        raise ValueError("CRITICAL ERROR: DB_HOST is empty! Configure milestone3/.env with remote MySQL credentials.")
        
    normalized_host = host.lower().strip()
    if normalized_host in FORBIDDEN_LOCAL_HOSTS or normalized_host.startswith("127."):
        if allow_local or os.getenv("ALLOW_LOCAL_DEV", "").lower() in ("true", "1", "yes"):
            print("⚠️ [DEV-ONLY WARNING]: Connected to localhost because --allow-local flag is active.")
            print("⚠️ NOTE: This flag is for offline local testing only. Official demo must run against remote host!")
            return host
        else:
            error_msg = (
                f"\n❌ STARTUP REFUSED: DB_HOST is set to '{host}'.\n"
                f"Per Milestone III non-negotiable rules, the application MUST communicate\n"
                f"with an actual remotely hosted MySQL server (e.g. db4free.net, Aiven, etc.)\n"
                f"and never with localhost.\n"
                f"To bypass ONLY during offline local development, supply --allow-local or set ALLOW_LOCAL_DEV=true."
            )
            print(error_msg, file=sys.stderr)
            raise ConnectionRefusedError(error_msg)
            
    print(f"✓ Remote Host Verified: {host} (Non-local host validated successfully)\n")
    return host

class DatabaseManager:
    """Manages resilient MySQL connections with retries and utf8mb4 encoding."""
    
    def __init__(self, allow_local: bool = False):
        self.allow_local = allow_local
        self.host = verify_remote_host(allow_local)
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.user = os.getenv("DB_USER", "")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "")
        self.ssl_enabled = os.getenv("DB_SSL", "false").lower() in ("true", "1", "yes")
        
    def create_connection(self):
        """Creates a fresh, configured PyMySQL connection with timeouts and utf8mb4."""
        ssl_config = {"ssl": {"fake_flag_to_enable_tls": True}} if self.ssl_enabled else {}
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=15,
            read_timeout=45,
            write_timeout=45,
            autocommit=False,
            **ssl_config
        )

    @contextmanager
    def get_cursor(self, max_retries: int = 3, backoff: float = 1.5):
        """
        Yields a cursor within a managed transaction.
        Automatically retries transient connection drops with exponential backoff.
        """
        conn = None
        attempt = 0
        last_error = None
        
        while attempt < max_retries:
            try:
                conn = self.create_connection()
                break
            except (pymysql.OperationalError, pymysql.InternalError) as e:
                attempt += 1
                last_error = e
                logger.warning(f"Connection attempt {attempt}/{max_retries} failed ({e}). Retrying in {backoff}s...")
                time.sleep(backoff)
                backoff *= 1.5
                
        if conn is None:
            logger.error(f"Failed to connect to remote DB after {max_retries} attempts: {last_error}")
            raise ConnectionError(f"Remote database unreachable ({self.host}:{self.port}): {last_error}")

        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as exc:
            conn.rollback()
            logger.error(f"Transaction rolled back due to error: {exc}")
            raise exc
        finally:
            cursor.close()
            conn.close()

# Global manager instance
_db_manager = None

def get_db(allow_local: bool = False) -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(allow_local)
    return _db_manager
