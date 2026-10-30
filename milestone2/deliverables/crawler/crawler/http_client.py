import time
import random
import logging
from typing import Optional
import requests
from milestone2.config import (
    CRAWL_MIN_DELAY,
    CRAWL_MAX_DELAY,
    CRAWL_TIMEOUT_CONNECT,
    CRAWL_TIMEOUT_READ,
    CRAWL_USER_AGENT,
    CRAWL_MAX_RETRIES,
    CRAWL_BACKOFF_FACTOR,
    CRAWL_MAX_CONSECUTIVE_BLOCKS,
    LOGS_DIR
)

# Set up logging
log_file = LOGS_DIR / "crawl.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("crawler")

class PoliteHttpClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": CRAWL_USER_AGENT,
            "Accept-Language": "en,ar;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })
        self.consecutive_blocks = 0
        self.total_requests = 0

    def get(self, url: str) -> Optional[requests.Response]:
        """Performs a polite, rate-limited HTTP GET request with exponential backoff."""
        # Politeness delay with uniform random jitter
        delay = random.uniform(CRAWL_MIN_DELAY, CRAWL_MAX_DELAY)
        logger.debug(f"Sleeping for {delay:.2f}s before request to {url}")
        time.sleep(delay)

        backoff = 5.0
        for attempt in range(1, CRAWL_MAX_RETRIES + 1):
            try:
                self.total_requests += 1
                start_time = time.time()
                resp = self.session.get(
                    url,
                    timeout=(CRAWL_TIMEOUT_CONNECT, CRAWL_TIMEOUT_READ),
                    allow_redirects=True
                )
                elapsed_ms = int((time.time() - start_time) * 1000)

                # Check for rate-limiting or challenge status codes
                if resp.status_code in (429, 503, 403):
                    self.consecutive_blocks += 1
                    logger.warning(
                        f"Rate limit / challenge hit (Status {resp.status_code}) on {url}. "
                        f"Consecutive blocks: {self.consecutive_blocks}. Backing off {backoff:.1f}s."
                    )
                    if self.consecutive_blocks >= CRAWL_MAX_CONSECUTIVE_BLOCKS:
                        logger.error(
                            f"Circuit breaker tripped: {self.consecutive_blocks} consecutive blocks. Halting crawler."
                        )
                        raise RuntimeError("Circuit breaker tripped: Too many consecutive challenge responses.")

                    time.sleep(backoff)
                    backoff *= CRAWL_BACKOFF_FACTOR
                    continue

                if "Just a moment..." in resp.text[:1000] or "Checking your browser" in resp.text[:1000]:
                    self.consecutive_blocks += 1
                    logger.warning(f"Cloudflare challenge detected in response body for {url}")
                    if self.consecutive_blocks >= CRAWL_MAX_CONSECUTIVE_BLOCKS:
                        raise RuntimeError("Circuit breaker tripped on Cloudflare challenge body.")
                    time.sleep(backoff)
                    backoff *= CRAWL_BACKOFF_FACTOR
                    continue

                # Successful request
                self.consecutive_blocks = 0
                logger.info(
                    f"GET {url} -> Status {resp.status_code} ({len(resp.content)} bytes) in {elapsed_ms}ms"
                )
                return resp

            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt}/{CRAWL_MAX_RETRIES} failed for {url}: {e}")
                if attempt == CRAWL_MAX_RETRIES:
                    logger.error(f"Failed to fetch {url} after {CRAWL_MAX_RETRIES} attempts.")
                    return None
                time.sleep(backoff)
                backoff *= CRAWL_BACKOFF_FACTOR

        return None

