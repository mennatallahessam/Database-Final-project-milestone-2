import sqlite3
import threading
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from milestone2.config import STAGING_DIR

DB_PATH = STAGING_DIR / "crawl_state.sqlite"
_lock = threading.Lock()

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=10000;")
    return conn

def init_state():
    """Initializes the crawler state table."""
    with _lock:
        with get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crawl_state (
                    listing_id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'done', 'failed', 'blocked'
                    discovered_at TEXT NOT NULL,
                    fetched_at TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    error_msg TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_crawl_status ON crawl_state(status);")
            conn.commit()

def add_discovered(listing_id: str, url: str) -> bool:
    """Inserts a newly discovered listing if not already present."""
    with _lock:
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR IGNORE INTO crawl_state (listing_id, url, status, discovered_at)
                VALUES (?, ?, 'pending', ?)
            """, (listing_id, url, datetime.utcnow().isoformat()))
            conn.commit()
            return cursor.rowcount > 0

def get_pending_listings(limit: Optional[int] = None) -> List[Dict]:
    """Retrieves pending listings to fetch."""
    query = "SELECT listing_id, url, attempts FROM crawl_state WHERE status = 'pending' ORDER BY rowid ASC"
    if limit and limit > 0:
        query += f" LIMIT {limit}"
    with get_connection() as conn:
        cursor = conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

def mark_done(listing_id: str):
    """Marks a listing as successfully fetched."""
    with _lock:
        with get_connection() as conn:
            conn.execute("""
                UPDATE crawl_state
                SET status = 'done', fetched_at = ?, attempts = attempts + 1, error_msg = NULL
                WHERE listing_id = ?
            """, (datetime.utcnow().isoformat(), listing_id))
            conn.commit()

def mark_failed(listing_id: str, error: str):
    """Marks a listing fetch as failed with reason."""
    with _lock:
        with get_connection() as conn:
            conn.execute("""
                UPDATE crawl_state
                SET status = 'failed', fetched_at = ?, attempts = attempts + 1, error_msg = ?
                WHERE listing_id = ?
            """, (datetime.utcnow().isoformat(), error, listing_id))
            conn.commit()

def mark_blocked(listing_id: str, error: str):
    """Marks a listing fetch as blocked with reason."""
    with _lock:
        with get_connection() as conn:
            conn.execute("""
                UPDATE crawl_state
                SET status = 'blocked', fetched_at = ?, attempts = attempts + 1, error_msg = ?
                WHERE listing_id = ?
            """, (datetime.utcnow().isoformat(), error, listing_id))
            conn.commit()

def retry_failed() -> int:
    """Resets failed listings back to pending status for a retry cycle."""
    with _lock:
        with get_connection() as conn:
            cursor = conn.execute("""
                UPDATE crawl_state
                SET status = 'pending', error_msg = NULL
                WHERE status IN ('failed', 'blocked')
            """)
            conn.commit()
            return cursor.rowcount

def get_stats() -> Dict[str, int]:
    """Returns counts of listings by status."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT status, COUNT(*) as cnt FROM crawl_state GROUP BY status
        """)
        stats = {row["status"]: row["cnt"] for row in cursor.fetchall()}
        cursor_total = conn.execute("SELECT COUNT(*) as total FROM crawl_state")
        stats["total"] = cursor_total.fetchone()["total"]
        return stats
