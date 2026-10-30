import re
from decimal import Decimal
from typing import Optional, Dict, Any, Tuple
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
    "al ahly sabbour": "Al Ahly Sabbour"
}

# Controlled Property Type Map
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
    "ivilla": "iVilla"
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
    # Strip currency, words, commas
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
    # 1. Mandatory natural key & URL
    if not record.get("source_listing_id"):
        return False, "Missing source_listing_id"
    if not record.get("source_url"):
        return False, "Missing source_url"

    # 2. Financial validation
    price = record.get("price")
    if price is None or price <= 0:
        return False, f"Invalid price: {price}"

    # 3. Area validation
    area = record.get("area_sqm")
    if area is None or area <= 0:
        return False, f"Invalid area_sqm: {area}"

    # 4. Down payment sanity
    down_payment = record.get("down_payment")
    if down_payment is not None and price is not None:
        if down_payment > price * Decimal("1.05"): # Allow slight fee rounding
            return False, f"Down payment ({down_payment}) exceeds total price ({price})"

    # 5. Bedrooms sanity
    bedrooms = record.get("bedrooms")
    if bedrooms is not None and (bedrooms < 0 or bedrooms > 20):
        return False, f"Implausible bedroom count: {bedrooms}"

    # 6. Contract year sanity
    contract_year = record.get("contract_year")
    if contract_year is not None and not (1990 <= contract_year <= 2030):
        return False, f"Contract year out of range: {contract_year}"

    # 7. Location presence
    if not record.get("location_name"):
        return False, "Missing location_name"

    return True, None

