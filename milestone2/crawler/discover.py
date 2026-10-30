import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from milestone2.crawler.http_client import PoliteHttpClient, logger
from milestone2.crawler.state import init_state, add_discovered, get_stats

SITEMAP_URL = "https://aqarexit.com/sitemap.xml"
INDEX_URL = "https://aqarexit.com/en/opportunities"

def extract_listing_id(url: str) -> str:
    """Extracts the unique opportunity identifier or UUID from an AqarExit URL."""
    # Pattern: /opportunity/b0a04b39-bc4f-4629-bcde-5a58fbc712ea
    match = re.search(r"/opportunity/([a-zA-Z0-9\-]+)", url)
    if match:
        return match.group(1).split("?")[0]
    # Fallback to normalized path
    return urlparse(url).path.strip("/").replace("/", "_")

def discover_listings():
    """Stage 1: Discovers all property listings from sitemap and index."""
    logger.info("Initializing crawler state database...")
    init_state()

    client = PoliteHttpClient()
    discovered_count = 0

    # 1. Discover via sitemap.xml
    logger.info(f"Fetching sitemap from {SITEMAP_URL}...")
    resp = client.get(SITEMAP_URL)
    if resp and resp.status_code == 200:
        try:
            root = ET.fromstring(resp.content)
            urls = [e.text for e in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc") if e.text]
            logger.info(f"Parsed {len(urls)} total URLs from sitemap.xml")
            for u in urls:
                if "/opportunity/" in u or "/buy/opportunity/" in u:
                    listing_id = extract_listing_id(u)
                    canonical_url = f"https://aqarexit.com/en/buy/opportunity/{listing_id}"
                    if add_discovered(listing_id, canonical_url):
                        discovered_count += 1
        except Exception as e:
            logger.error(f"Error parsing sitemap.xml: {e}")

    # 2. Discover via Opportunities index page
    logger.info(f"Fetching opportunities index from {INDEX_URL}...")
    resp_idx = client.get(INDEX_URL)
    if resp_idx and resp_idx.status_code == 200:
        soup = BeautifulSoup(resp_idx.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/opportunity/" in href:
                full_url = href if href.startswith("http") else f"https://aqarexit.com{href}"
                listing_id = extract_listing_id(full_url)
                canonical_url = f"https://aqarexit.com/en/buy/opportunity/{listing_id}"
                if add_discovered(listing_id, canonical_url):
                    discovered_count += 1

    stats = get_stats()
    logger.info(f"Discovery complete! Total unique listings in state: {stats.get('total', 0)} (New: {discovered_count})")
    print(f"\n--- DISCOVERY SUMMARY ---")
    print(f"Total Listings Discovered: {stats.get('total', 0)}")
    print(f"Pending: {stats.get('pending', 0)}")
    print(f"Done: {stats.get('done', 0)}")
    print(f"Failed: {stats.get('failed', 0)}")

if __name__ == "__main__":
    discover_listings()

