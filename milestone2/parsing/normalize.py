import re
import csv
from decimal import Decimal
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from milestone2.parsing.text_extractors import clean_arabic_digits

# Controlled Developer Alias Resolution Map
DEVELOPER_ALIASES = {
    "lavista": "La Vista Developments",
    "la vista": "La Vista Developments",
    "la vista developments": "La Vista Developments",
    "palm hills": "Palm Hills Developments",
    "palm hills developments": "Palm Hills Developments",
    "sodic": "SODIC",
    "emaar": "Emaar Misr",
    "emaar misr": "Emaar Misr",
    "orascom": "Orascom Development",
    "talaat moustafa": "Talaat Moustafa Group (TMG)",
    "tmg": "Talaat Moustafa Group (TMG)",
    "mountain view": "Mountain View",
    "tatweer misr": "Tatweer Misr",
    "mnhr": "Madinet Masr (MNHD)",
    "madinet masr": "Madinet Masr (MNHD)",
    "hassan allam": "Hassan Allam Properties",
    "al ahly sabbour": "Al Ahly Sabbour",
    "dorra": "Dorra Group",
    "al marasem": "Al Marasem Development",
    "inland": "Inland Developments",
    "gates": "Gates Developments",
    "inertia": "Inertia Egypt",
    "misr italia": "Misr Italia Properties"
}

# Controlled Property Type Map (Canonical English)
PROPERTY_TYPE_MAP = {
    "شقة": "Apartment",
    "apartment": "Apartment",
    "فيلا": "Villa",
    "villa": "Villa",
    "تاون هاوس": "Townhouse",
    "townhouse": "Townhouse",
    "توين هاوس": "Twin House",
    "twin house": "Twin House",
    "دوبلكس": "Duplex",
    "duplex": "Duplex",
    "بنتهاوس": "Penthouse",
    "penthouse": "Penthouse",
    "شاليه": "Chalet",
    "chalet": "Chalet",
    "ستوديو": "Studio",
    "studio": "Studio",
    "اي فيلا": "iVilla",
    "ivilla": "iVilla",
    "محل": "Shop",
    "shop": "Shop",
    "مكتب": "Office",
    "office": "Office",
    "عيادة": "Clinic",
    "clinic": "Clinic",
    "تجاري": "Commercial",
    "commercial": "Commercial",
    "اداري": "Office"
}

# Bilingual Property Type Dictionary (canonical_name -> (name_en, name_ar))
PROPERTY_TYPE_BILINGUAL = {
    "Apartment": ("Apartment", "شقة"),
    "Villa": ("Villa", "فيلا"),
    "Townhouse": ("Townhouse", "تاون هاوس"),
    "Twin House": ("Twin House", "توين هاوس"),
    "Duplex": ("Duplex", "دوبلكس"),
    "Penthouse": ("Penthouse", "بنتهاوس"),
    "Chalet": ("Chalet", "شاليه"),
    "Studio": ("Studio", "ستوديو"),
    "iVilla": ("iVilla", "اي فيلا"),
    "Shop": ("Shop", "محل"),
    "Office": ("Office", "مكتب"),
    "Clinic": ("Clinic", "عيادة"),
    "Commercial": ("Commercial", "تجاري")
}

def normalize_entity_name(name: Optional[str]) -> Optional[str]:
    """Cleans whitespace, casing, and trailing noise from entity names."""
    if not name:
        return None
    cleaned = re.sub(r"\s+", " ", name).strip()
    return cleaned

def resolve_developer(raw_name: Optional[str]) -> Optional[str]:
    """Resolves developer variants to a canonical corporate name."""
    if not raw_name:
        return None
    clean = normalize_entity_name(raw_name)
    key = clean.lower()
    for alias_key, canonical in DEVELOPER_ALIASES.items():
        if alias_key in key:
            return canonical
    return clean

def resolve_property_type(raw_type: Optional[str]) -> str:
    """Maps Arabic or English property unit types to standardized name."""
    if not raw_type:
        return "Apartment"
    clean = normalize_entity_name(raw_type).lower()
    for k, v in PROPERTY_TYPE_MAP.items():
        if k in clean:
            return v
    return normalize_entity_name(raw_type)

def load_location_hierarchy(csv_path: Optional[Path] = None) -> Dict[str, Dict[str, str]]:
    """Loads location hierarchy mappings from location_hierarchy.csv."""
    if not csv_path:
        csv_path = Path(__file__).resolve().parent / "location_hierarchy.csv"
    hierarchy: Dict[str, Dict[str, str]] = {}
    if not csv_path.exists():
        return hierarchy
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            area_en = r["area_name"].strip()
            area_ar = r["area_name_ar"].strip()
            entry = {
                "area_en": area_en,
                "area_ar": area_ar,
                "city_en": r["city"].strip(),
                "city_ar": r.get("city_ar", "").strip() or r["city"].strip(),
                "governorate_en": r["governorate"].strip(),
                "governorate_ar": r.get("governorate_ar", "").strip() or r["governorate"].strip(),
            }
            hierarchy[area_en.lower()] = entry
            hierarchy[area_ar.lower()] = entry
            # Normalized variants
            norm_ar = re.sub(r"[أإآ]", "ا", area_ar).replace("ة", "ه").lower()
            hierarchy[norm_ar] = entry
    return hierarchy

def resolve_location(raw_loc: Optional[str], hierarchy: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    """Resolves a raw location string into a full geographic hierarchy."""
    if not raw_loc:
        return {
            "area_en": "New Cairo",
            "area_ar": "القاهرة الجديدة",
            "city_en": "New Cairo",
            "city_ar": "القاهرة الجديدة",
            "governorate_en": "Cairo",
            "governorate_ar": "القاهرة"
        }
    clean = normalize_entity_name(raw_loc)
    key = clean.lower()
    if key in hierarchy:
        return hierarchy[key]

    norm_key = re.sub(r"[أإآ]", "ا", key).replace("ة", "ه")
    if norm_key in hierarchy:
        return hierarchy[norm_key]

    # Partial substring search
    for h_key, val in hierarchy.items():
        if h_key in key or key in h_key:
            return val

    # Fallback for completely novel areas: map under Cairo / Unclassified
    return {
        "area_en": clean,
        "area_ar": clean,
        "city_en": "Cairo",
        "city_ar": "القاهرة",
        "governorate_en": "Cairo",
        "governorate_ar": "القاهرة"
    }

def generate_entity_resolution_report(out_csv_path: Path):
    """Generates the entity resolution audit report for human review."""
    out_csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []

    # 1. Developer Merges
    for alias, canonical in DEVELOPER_ALIASES.items():
        rows.append({
            "entity_type": "developer",
            "raw_variant": alias,
            "resolved_canonical": canonical,
            "action": "MERGED",
            "rationale": "Corporate spelling/abbreviation normalization"
        })

    # 2. Distinct Developers kept separate (near-duplicates not merged)
    distinct_pairs = [
        ("SODIC West", "SODIC East", "Geographically distinct developments under same parent"),
        ("Palm Hills October", "Palm Hills New Cairo", "Geographically separate project entities"),
        ("Mountain View iCity New Cairo", "Mountain View iCity October", "Separate master-planned communities"),
        ("Emaar Mivida", "Emaar Marassi", "Different property portfolios (East Cairo vs. North Coast)")
    ]
    for d1, d2, reason in distinct_pairs:
        rows.append({
            "entity_type": "development",
            "raw_variant": f"{d1} vs {d2}",
            "resolved_canonical": "KEPT SEPARATE",
            "action": "NOT_MERGED",
            "rationale": reason
        })

    # 3. Property Type Merges
    for raw, canonical in PROPERTY_TYPE_MAP.items():
        bilingual = PROPERTY_TYPE_BILINGUAL.get(canonical, (canonical, raw))
        rows.append({
            "entity_type": "property_type",
            "raw_variant": raw,
            "resolved_canonical": f"{bilingual[0]} ({bilingual[1]})",
            "action": "STANDARDIZED",
            "rationale": "Bilingual unit type classification"
        })

    with open(out_csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["entity_type", "raw_variant", "resolved_canonical", "action", "rationale"])
        writer.writeheader()
        writer.writerows(rows)

def parse_decimal_value(raw: Any) -> Optional[Decimal]:
    """Safely converts string/int/float into a validated Decimal."""
    if raw is None or raw == "":
        return None
    if isinstance(raw, (int, Decimal)):
        return Decimal(raw)
    if isinstance(raw, float):
        return Decimal(str(raw))
    
    # String cleanup
    s = str(raw)
    s = clean_arabic_digits(s)
    s = re.sub(r"[^\d.]", "", s)
    if not s:
        return None
    try:
        return Decimal(s)
    except Exception:
        return None

def validate_and_quarantine(record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validates property listing against business rules.
    Returns: (is_valid, quarantine_reason)
    """
    if not record.get("source_listing_id"):
        return False, "Missing source_listing_id"
    if not record.get("source_url"):
        return False, "Missing source_url"

    price = record.get("price")
    if price is None or price <= 0:
        return False, f"Invalid price: {price}"

    area = record.get("area_sqm")
    if area is None or area <= 0:
        return False, f"Invalid area_sqm: {area}"

    down_payment = record.get("down_payment")
    if down_payment is not None and price is not None:
        if down_payment > price * Decimal("1.05"):
            return False, f"Down payment ({down_payment}) exceeds total price ({price})"

    bedrooms = record.get("bedrooms")
    if bedrooms is not None and (bedrooms < 0 or bedrooms > 20):
        return False, f"Implausible bedroom count: {bedrooms}"

    contract_year = record.get("contract_year")
    if contract_year is not None and not (1990 <= contract_year <= 2030):
        return False, f"Contract year out of range: {contract_year}"

    if not record.get("location_name"):
        return False, "Missing location_name"

    return True, None
