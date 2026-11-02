import os
import sys
import time
import signal
import random
import argparse
import threading
from datetime import timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

from milestone2.config import RAW_DIR, CRAWL_USER_AGENT
from milestone2.crawler.state import (
    init_state,
    get_pending_listings,
    mark_done,
    mark_failed,
    mark_blocked,
    retry_failed,
    get_stats
)

_shutdown_requested = False
_stats_lock = threading.Lock()
_fetched_count = 0
_skipped_count = 0
_failed_count = 0
_blocked_count = 0

def _sigint_handler(signum, frame):
    global _shutdown_requested
    print("\n[INTERRUPT] Shutdown signal received (Ctrl+C). Completing in-flight requests and saving state...")
    _shutdown_requested = True

def _fetch_worker(item, resume: bool, min_delay: float, max_delay: float, thread_session: requests.Session):
    global _shutdown_requested, _fetched_count, _skipped_count, _failed_count, _blocked_count
    if _shutdown_requested:
        return

    listing_id = item["listing_id"]
    url = item["url"]
    target_path = RAW_DIR / f"{listing_id}.html"

    # Check if already fetched and valid
    if resume and target_path.exists() and target_path.stat().st_size > 1000:
        mark_done(listing_id)
        with _stats_lock:
            _skipped_count += 1
        return

    # Gentle jitter delay
    if max_delay > 0:
        time.sleep(random.uniform(min_delay, max_delay))

    try:
        resp = thread_session.get(url, timeout=(10, 25))
    except Exception as e:
        mark_failed(listing_id, f"ConnectionError: {e}")
        with _stats_lock:
            _failed_count += 1
        return

    if resp.status_code == 200:
        if len(resp.text) < 500 or "Just a moment..." in resp.text[:1000]:
            mark_failed(listing_id, "Empty/Challenge")
            with _stats_lock:
                _failed_count += 1
            return

        # Atomic file write
        temp_path = RAW_DIR / f"{listing_id}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(resp.text)
        temp_path.replace(target_path)

        mark_done(listing_id)
        with _stats_lock:
            _fetched_count += 1
    elif resp.status_code in (403, 429, 503):
        mark_blocked(listing_id, f"HTTP_{resp.status_code}")
        with _stats_lock:
            _blocked_count += 1
    else:
        mark_failed(listing_id, f"HTTP_{resp.status_code}")
        with _stats_lock:
            _failed_count += 1

def fetch_listings(limit: int = 0, only_id: str = None, resume: bool = True, do_retry_failed: bool = False, workers: int = 4):
    global _shutdown_requested, _fetched_count, _skipped_count, _failed_count, _blocked_count
    signal.signal(signal.SIGINT, _sigint_handler)

    init_state()

    if do_retry_failed:
        requeued = retry_failed()
        print(f"Re-queued {requeued} failed listings back to pending state.")

    pending = get_pending_listings(limit=limit if limit > 0 else None)
    if only_id:
        pending = [{"listing_id": only_id, "url": f"https://aqarexit.com/en/buy/opportunity/{only_id}", "attempts": 0}]

    total_pending = len(pending)
    est_sec = (total_pending / (workers * 1.5)) if workers > 0 else total_pending * 3
    est_hours = est_sec / 3600.0

    print("================================================================================")
    print("                AQAREXIT HIGH-THROUGHPUT WEB CRAWLER - STAGE 2                 ")
    print("================================================================================")
    print(f"Target Queue Size  : {total_pending} listings (Mode: {'ALL / UNLIMITED' if limit == 0 else f'LIMIT {limit}'})")
    print(f"Concurrency Workers: {workers} threads")
    print(f"Estimated Duration : ~{est_hours*60:.1f} minutes (~{est_hours:.2f} hours)")
    print(f"State Resumability : {'ENABLED (skipping existing files)' if resume else 'DISABLED'}")
    print("================================================================================\n")

    start_time = time.time()
    min_delay = 0.2 if workers > 1 else 1.0
    max_delay = 0.6 if workers > 1 else 2.5

    # Thread-local sessions
    thread_local = threading.local()
    def get_thread_session():
        if not hasattr(thread_local, "session"):
            s = requests.Session()
            s.headers.update({
                "User-Agent": CRAWL_USER_AGENT,
                "Accept-Language": "en,ar;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            })
            thread_local.session = s
        return thread_local.session

    def worker_wrapper(item):
        session = get_thread_session()
        return _fetch_worker(item, resume, min_delay, max_delay, session)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(worker_wrapper, item): item for item in pending}
        done_count = 0
        for f in as_completed(futures):
            if _shutdown_requested:
                break
            done_count += 1
            if done_count % 50 == 0 or done_count == total_pending:
                elapsed = time.time() - start_time
                rate = _fetched_count / elapsed if elapsed > 0 else 0
                rem_items = total_pending - done_count
                eta_sec = rem_items / rate if rate > 0 else 0
                eta_str = str(timedelta(seconds=int(eta_sec)))
                pct = (done_count / total_pending) * 100

                print(
                    f"[{done_count}/{total_pending} ({pct:.1f}%)] "
                    f"Fetched: {_fetched_count} | Skipped: {_skipped_count} | "
                    f"Failed: {_failed_count} | Rate: {rate:.1f} req/s | ETA: {eta_str}"
                )

    total_elapsed = str(timedelta(seconds=int(time.time() - start_time)))
    stats = get_stats()
    print("\n------------------------- FETCH CYCLE SUMMARY -------------------------")
    print(f"Total Elapsed Time    : {total_elapsed}")
    print(f"Listings Fetched      : {_fetched_count}")
    print(f"Listings Skipped      : {_skipped_count} (already cached)")
    print(f"Listings Failed       : {_failed_count}")
    print(f"Listings Blocked      : {_blocked_count}")
    print("-----------------------------------------------------------------------")
    print(f"Cumulative DB State   : Done={stats.get('done', 0)} | Pending={stats.get('pending', 0)} | Failed={stats.get('failed', 0)} | Blocked={stats.get('blocked', 0)}")
    print("-----------------------------------------------------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="AqarExit Detail Page Crawler")
    parser.add_argument("--limit", type=int, default=0, help="Max listings to fetch (0 = unlimited / all)")
    parser.add_argument("--all", action="store_true", help="Fetch all pending listings (alias for --limit 0)")
    parser.add_argument("--only-id", type=str, default=None, help="Fetch single listing ID")
    parser.add_argument("--resume", action="store_true", default=True, help="Skip existing files")
    parser.add_argument("--retry-failed", action="store_true", help="Re-queue failed/blocked listings before running")
    parser.add_argument("--workers", type=int, default=5, help="Number of concurrent worker threads")
    args = parser.parse_args()

    effective_limit = 0 if args.all else args.limit
    fetch_listings(
        limit=effective_limit,
        only_id=args.only_id,
        resume=args.resume,
        do_retry_failed=args.retry_failed,
        workers=args.workers
    )

if __name__ == "__main__":
    main()
