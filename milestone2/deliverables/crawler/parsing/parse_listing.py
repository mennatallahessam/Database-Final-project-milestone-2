import re
import json
import argparse
import time
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

from milestone2.config import RAW_DIR, STAGING_DIR
from milestone2.parsing.text_extractors import (
    clean_arabic_digits,
    extract_area_from_text,
    extract_bedrooms_from_text,
    extract_bathrooms_from_text,
    extract_money_amount,
    extract_contract_year_from_text,
    extract_installment_terms_from_text,
    extract_amenities_from_text
)
from milestone2.parsing.normalize import (
    resolve_developer,
    resolve_property_type,
    normalize_entity_name,
    parse_decimal_value,
    validate_and_quarantine
)

def parse_listing_html(html_text: str, listing_id: str, url: str) -> Dict[str, Any]:
    """Pure parsing function extracting structured property data from raw listing HTML."""
    soup = BeautifulSoup(html_text, "html.parser")
    record: Dict[str, Any] = {
        "source_listing_id": listing_id,
        "source_url": url,
        "title": None,
        "description": None,
        "developer_name": None,
        "development_name": None,
        "location_name": None,
        "property_type_name": "Apartment",
        "payment_method_name": "Installments",
        "area_sqm": None,
        "bedrooms": None,
        "bathrooms": None,
        "price": None,
        "market_price": None,
        "down_payment": None,
        "installment_amount": None,
        "installment_frequency": None,
        "installment_years": None,
        "remaining_balance": None,
        "gain_over_market_value": None,
        "gain_percentage": None,
        "discount_over_market_price": None,
        "contract_year": None,
        "delivery_year": None,
        "currency": "EGP",
        "amenities": [],
        "extraction_sources": {},
        "parse_warnings": []
    }

    # 1. PARSE JSON-LD STRUCTURED METADATA
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            if not s.string:
                continue
            data = json.loads(s.string)
            if data.get("@type") == "Product":
                record["title"] = data.get("name")
                record["description"] = data.get("description")
                if "brand" in data and isinstance(data["brand"], dict):
                    record["developer_name"] = resolve_developer(data["brand"].get("name"))
                    record["extraction_sources"]["developer"] = "json_ld"

                # Parse additionalProperty array
                for prop in data.get("additionalProperty", []):
                    p_name = prop.get("name", "")
                    p_val = prop.get("value")
                    if "المنطقة" in p_name or "Area" in p_name:
                        record["location_name"] = normalize_entity_name(str(p_val))
                    elif "نوع الوحدة" in p_name or "Unit Type" in p_name:
                        record["property_type_name"] = resolve_property_type(str(p_val))
                    elif "سنة الاستلام" in p_name or "Delivery" in p_name:
                        try:
                            record["delivery_year"] = int(clean_arabic_digits(str(p_val)))
                        except Exception:
                            pass

                # Offers / Price
                if "offers" in data and isinstance(data["offers"], dict):
                    o_price = parse_decimal_value(data["offers"].get("price"))
                    if o_price:
                        record["down_payment"] = o_price
                        record["extraction_sources"]["down_payment"] = "json_ld"
                        
            elif data.get("@type") == "BreadcrumbList":
                items = data.get("itemListElement", [])
                if len(items) >= 3:
                    candidate_dev = items[2].get("name")
                    if candidate_dev and candidate_dev != "Opportunities":
                        record["development_name"] = normalize_entity_name(candidate_dev)
                        record["extraction_sources"]["development"] = "json_ld"
        except Exception as e:
            record["parse_warnings"].append(f"JSON-LD parse error: {e}")

    # 2. PARSE HTML DOM & KEY-VALUE TEXT
    if not record["title"] and soup.title:
        record["title"] = soup.title.string.strip()

    full_text = " ".join(soup.stripped_strings)

    h1 = soup.find("h1")
    if h1:
        h1_text = h1.get_text(strip=True)
        if not record["development_name"]:
            record["development_name"] = normalize_entity_name(h1_text)

    # Key metrics from page text patterns
    m_cash = re.search(r"Cash required now\s+(?:EGP|ج\.م)?\s*([\d,]+)", full_text, re.IGNORECASE)
    if m_cash:
        val = parse_decimal_value(m_cash.group(1))
        if val:
            record["down_payment"] = val
            record["extraction_sources"]["down_payment"] = "html_label"

    m_market = re.search(r"Market price today[^\d]*([\d,]+)", full_text, re.IGNORECASE)
    if m_market:
        val = parse_decimal_value(m_market.group(1))
        if val:
            record["market_price"] = val
            record["extraction_sources"]["market_price"] = "html_label"

    m_gain = re.search(r"Your gain vs\.? current market price[^\d]*([\d,]+)", full_text, re.IGNORECASE)
    if m_gain:
        val = parse_decimal_value(m_gain.group(1))
        if val:
            record["gain_over_market_value"] = val
            record["discount_over_market_price"] = val
            record["extraction_sources"]["gain"] = "html_label"

    m_rem = re.search(r"Remaining with developer[^\d]*([\d,]+)", full_text, re.IGNORECASE)
    if m_rem:
        val = parse_decimal_value(m_rem.group(1))
        if val:
            record["remaining_balance"] = val
            record["extraction_sources"]["remaining_balance"] = "html_label"

    # Total Price calculation
    if record["down_payment"] is not None:
        if record["remaining_balance"] is not None:
            record["price"] = record["down_payment"] + record["remaining_balance"]
        else:
            record["price"] = record["down_payment"]
        record["extraction_sources"]["price"] = "calculated"
    elif record["market_price"] is not None:
        record["price"] = record["market_price"]

    m_area = re.search(r"Area\s*(\d+(?:[.,]\d+)?)\s*(?:م²|m²|sqm)", full_text, re.IGNORECASE)
    if m_area:
        record["area_sqm"] = parse_decimal_value(m_area.group(1))
        record["extraction_sources"]["area_sqm"] = "html_label"

    m_cyear = re.search(r"Contract year\s*(\d{4})", full_text, re.IGNORECASE)
    if m_cyear:
        record["contract_year"] = int(m_cyear.group(1))
        record["extraction_sources"]["contract_year"] = "html_label"

    m_inst = re.search(r"Installment\s+(?:EGP|ج\.م)?\s*([\d,]+)\s*·\s*([A-Za-z]+)", full_text, re.IGNORECASE)
    if m_inst:
        record["installment_amount"] = parse_decimal_value(m_inst.group(1))
        record["installment_frequency"] = m_inst.group(2).capitalize()
        record["extraction_sources"]["installment"] = "html_label"

    m_yrs = re.search(r"Instalments remaining\s*(\d+(?:\.\d+)?)\s*years", full_text, re.IGNORECASE)
    if m_yrs:
        record["installment_years"] = parse_decimal_value(m_yrs.group(1))

    m_del = re.search(r"Delivery\s*(\d{4})", full_text, re.IGNORECASE)
    if m_del and not record["delivery_year"]:
        record["delivery_year"] = int(m_del.group(1))

    if record["remaining_balance"] and record["remaining_balance"] > 0:
        record["payment_method_name"] = "Installments"
    else:
        record["payment_method_name"] = "Cash"

    # 3. AMENITIES EXTRACTION
    amenity_map = {
        "مصعد": "Elevator",
        "جراج": "Garage",
        "أمن 24 ساعة": "24/7 Security",
        "حمام سباحة": "Swimming Pool",
        "جاردن خاصة": "Private Garden",
        "رووف": "Roof",
        "كلوب هاوس": "Clubhouse",
        "قريبة من الخدمات": "Commercial Area",
        "ألعاب أطفال": "Kids Area",
        "صالة ألعاب رياضية": "Gym"
    }
    extracted_amenities = set()
    for ar_term, en_term in amenity_map.items():
        if ar_term in full_text or en_term.lower() in full_text.lower():
            extracted_amenities.add(en_term)

    record["amenities"] = sorted(list(extracted_amenities))

    # 4. FREE TEXT EXTRACTION FALLBACKS
    search_corpus = f"{record.get('title') or ''} {record.get('description') or ''} {soup.title.string if soup.title else ''}"

    if record["bedrooms"] is None:
        br_val, br_conf, _ = extract_bedrooms_from_text(search_corpus)
        if br_val is not None:
            record["bedrooms"] = br_val
            record["extraction_sources"]["bedrooms"] = "text_extractor"

    if record["bathrooms"] is None:
        ba_val, ba_conf, _ = extract_bathrooms_from_text(search_corpus)
        if ba_val is not None:
            record["bathrooms"] = ba_val
            record["extraction_sources"]["bathrooms"] = "text_extractor"

    if record["area_sqm"] is None:
        ar_val, ar_conf, _ = extract_area_from_text(search_corpus)
        if ar_val is not None:
            record["area_sqm"] = ar_val
            record["extraction_sources"]["area_sqm"] = "text_extractor"

    if record["down_payment"] is None:
        m_val, m_conf, _ = extract_money_amount(search_corpus)
        if m_val is not None:
            record["down_payment"] = m_val
            if record["price"] is None:
                record["price"] = m_val
            record["extraction_sources"]["down_payment"] = "text_extractor"

    if record["contract_year"] is None:
        cy_val, cy_conf, _ = extract_contract_year_from_text(search_corpus)
        if cy_val is not None:
            record["contract_year"] = cy_val
            record["extraction_sources"]["contract_year"] = "text_extractor"

    if record["price"] and record["market_price"] and record["market_price"] > record["price"]:
        gain = record["market_price"] - record["price"]
        record["gain_over_market_value"] = gain
        record["gain_percentage"] = round((gain / record["price"]) * 100, 2)
        record["discount_over_market_price"] = gain

    return record

def _process_single_file(file_path: Path) -> Tuple[bool, str]:
    """Helper for parallel file processing."""
    listing_id = file_path.stem
    url = f"https://aqarexit.com/en/buy/opportunity/{listing_id}"
    with open(file_path, "r", encoding="utf-8") as f:
        html_text = f.read()

    record = parse_listing_html(html_text, listing_id, url)
    is_valid, reason = validate_and_quarantine(record)

    serialized = {}
    for k, v in record.items():
        if isinstance(v, Decimal):
            serialized[k] = float(v)
        else:
            serialized[k] = v

    if not is_valid:
        serialized["quarantine_reason"] = reason

    return is_valid, json.dumps(serialized, ensure_ascii=False)

def process_all_raw_files(limit: Optional[int] = None, workers: int = 8):
    """Processes all downloaded raw HTML files in parallel and stages them."""
    raw_files = sorted(list(RAW_DIR.glob("*.html")))
    if limit:
        raw_files = raw_files[:limit]

    total_files = len(raw_files)
    print(f"Staging parser processing {total_files} files with {workers} worker threads...")
    t0 = time.time()

    staging_file = STAGING_DIR / "listings.jsonl"
    quarantine_file = STAGING_DIR / "rejected.jsonl"

    valid_count = 0
    quarantine_count = 0

    with open(staging_file, "w", encoding="utf-8") as f_valid, \
         open(quarantine_file, "w", encoding="utf-8") as f_quar:
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_process_single_file, fp) for fp in raw_files]
            
            for idx, fut in enumerate(as_completed(futures), 1):
                is_valid, json_str = fut.result()
                if is_valid:
                    f_valid.write(json_str + "\n")
                    valid_count += 1
                else:
                    f_quar.write(json_str + "\n")
                    quarantine_count += 1

                if idx % 1000 == 0 or idx == total_files:
                    elapsed = time.time() - t0
                    speed = idx / elapsed if elapsed > 0 else 0
                    print(f"[{idx}/{total_files} ({(idx/total_files)*100:.1f}%)] Parsed in {elapsed:.1f}s ({speed:.1f} files/s)...")

    elapsed_total = time.time() - t0
    print(f"\n--- PARSER SUMMARY ---")
    print(f"Total Files Processed: {total_files} in {elapsed_total:.1f}s ({total_files/elapsed_total:.1f} files/s)")
    print(f"Valid Staged Records  : {valid_count} -> {staging_file}")
    print(f"Quarantined Records   : {quarantine_count} -> {quarantine_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AqarExit HTML Parser")
    parser.add_argument("--all", action="store_true", help="Parse all files in data/raw/")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files")
    parser.add_argument("--workers", type=int, default=8, help="Parallel worker threads")
    args = parser.parse_args()

    process_all_raw_files(limit=args.limit, workers=args.workers)
