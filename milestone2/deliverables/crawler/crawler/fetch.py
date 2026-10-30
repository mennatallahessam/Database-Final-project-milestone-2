import os
import sys
import argparse
from pathlib import Path
from milestone2.config import RAW_DIR, CRAWL_DEFAULT_LIMIT
from milestone2.crawler.http_client import PoliteHttpClient, logger
from milestone2.crawler.state import (
    init_state,
    get_pending_listings,
    mark_done,
    mark_failed,
    get_stats
)

def fetch_listings(limit: int = 50, only_id: str = None, resume: bool = True):
    """Stage 2: Fetches pending property detail pages and saves them raw."""
    init_state()
    client = PoliteHttpClient()

    pending = get_pending_listings(limit=limit)
    if only_id:
        pending = [{"listing_id": only_id, "url": f"https://aqarexit.com/en/buy/opportunity/{only_id}", "attempts": 0}]

    logger.info(f"Starting fetch cycle for {len(pending)} listings (Limit: {limit})...")

    fetched_count = 0
    skipped_count = 0

    for idx, item in enumerate(pending, 1):
        listing_id = item["listing_id"]
        url = item["url"]
        target_path = RAW_DIR / f"{listing_id}.html"

        # Check if already fetched and non-empty (resume capability)
        if resume and target_path.exists() and target_path.stat().st_size > 1000:
            logger.info(f"[{idx}/{len(pending)}] Skipping already downloaded: {listing_id}")
            mark_done(listing_id)
            skipped_count += 1
            continue

        logger.info(f"[{idx}/{len(pending)}] Fetching {listing_id} -> {url}")
        resp = client.get(url)

        if resp and resp.status_code == 200:
            # Validate response is not a soft error or challenge
            if len(resp.text) < 500 or "Just a moment..." in resp.text:
                logger.warning(f"Discarding suspicious/empty page for {listing_id}")
                mark_failed(listing_id, "Empty or challenge page")
                continue

            # Atomic file write (temp file -> rename)
            temp_path = RAW_DIR / f"{listing_id}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
            temp_path.replace(target_path)

            mark_done(listing_id)
            fetched_count += 1
        else:
            status = resp.status_code if resp else "ConnectionError"
            logger.error(f"Failed to fetch {listing_id} (Status: {status})")
            mark_failed(listing_id, f"HTTP_{status}")

    stats = get_stats()
    print("\n--- FETCH SUMMARY ---")
    print(f"Cycle Fetched: {fetched_count}")
    print(f"Cycle Skipped (Resumed): {skipped_count}")
    print(f"Total State -> Done: {stats.get('done', 0)} | Pending: {stats.get('pending', 0)} | Failed: {stats.get('failed', 0)}")

def main():
    parser = argparse.ArgumentParser(description="AqarExit Detail Page Crawler")
    parser.add_argument("--limit", type=int, default=CRAWL_DEFAULT_LIMIT, help="Max listings to fetch")
    parser.add_argument("--only-id", type=str, default=None, help="Fetch single listing ID")
    parser.add_argument("--resume", action="store_true", default=True, help="Skip existing files")
    args = parser.parse_args()

    fetch_listings(limit=args.limit, only_id=args.only_id, resume=args.resume)

if __name__ == "__main__":
    main()

