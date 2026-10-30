import re
from decimal import Decimal
from typing import Optional, Tuple, Dict, Any, List

def clean_arabic_digits(text: str) -> str:
    """Replaces Arabic-Indic digits (٠١٢٣٤٥٦٧٨٩) with standard ASCII digits (0-9)."""
    if not text:
        return ""
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    english_digits = "0123456789"
    translation = str.maketrans("".join(arabic_digits), "".join(english_digits))
    return text.translate(translation)

def extract_area_from_text(text: str) -> Tuple[Optional[Decimal], float, Optional[str]]:
    """Extracts built-up area in square meters from free text.
    Returns: (value_in_sqm, confidence, matched_snippet)
    """
    if not text:
        return None, 0.0, None
    text = clean_arabic_digits(text)
    # Matches: 176 m², 176 sqm, 176 sq.m, 176 م², 176 متر
    pattern = r"(\d+(?:[.,]\d+)?)\s*(?:sqm|sq\.m|m²|م²|متر|m2)\b"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        val_str = match.group(1).replace(",", "")
        try:
            val = Decimal(val_str)
            if 15 <= val <= 10000:
                return val, 0.95, match.group(0)
        except Exception:
            pass
    return None, 0.0, None

def extract_bedrooms_from_text(text: str) -> Tuple[Optional[int], float, Optional[str]]:
    """Extracts bedroom count from free text (e.g. 4 BR, 3 bedrooms, 3 غرف)."""
    if not text:
        return None, 0.0, None
    text = clean_arabic_digits(text)
    # Studio check
    if re.search(r"\b(?:studio|ستوديو)\b", text, re.IGNORECASE):
        return 0, 0.90, "studio"
    
    # Matches: 4 BR, 4 bedrooms, 4 bed, 4 غرف, 4 نوم
    pattern = r"(\d+)\s*(?:br|bed|bedrooms?|bedroom|غرف نوم|غرف|نوم)\b"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            val = int(match.group(1))
            if 0 <= val <= 20:
                return val, 0.95, match.group(0)
        except Exception:
            pass
    return None, 0.0, None

def extract_bathrooms_from_text(text: str) -> Tuple[Optional[int], float, Optional[str]]:
    """Extracts bathroom count from free text (e.g. 3 bathrooms, 3 bath, 3 حمام)."""
    if not text:
        return None, 0.0, None
    text = clean_arabic_digits(text)
    pattern = r"(\d+)\s*(?:baths?|bathrooms?|حمام|حمامات)\b"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            val = int(match.group(1))
            if 0 <= val <= 20:
                return val, 0.95, match.group(0)
        except Exception:
            pass
    return None, 0.0, None

def extract_money_amount(text: str) -> Tuple[Optional[Decimal], float, Optional[str]]:
    """Extracts money amounts formatted as EGP 3.6M, 3,600,000, 3.6 million, etc."""
    if not text:
        return None, 0.0, None
    text = clean_arabic_digits(text)
    
    # Matches e.g. 3.6M or 3.6 million or 3.6 مليون
    m_pattern = r"(?:EGP|ج\.م|LE|L\.E\.)?\s*(\d+(?:[.,]\d+)?)\s*(?:M|million|مليون)\b"
    match_m = re.search(m_pattern, text, re.IGNORECASE)
    if match_m:
        val_str = match_m.group(1).replace(",", "")
        try:
            val = Decimal(val_str) * Decimal("1000000")
            return val, 0.90, match_m.group(0)
        except Exception:
            pass

    # Matches full numbers e.g. EGP 3,600,000 or 3600000
    full_pattern = r"(?:EGP|ج\.م|LE|L\.E\.)\s*(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d{5,}(?:\.\d+)?)"
    match_full = re.search(full_pattern, text, re.IGNORECASE)
    if match_full:
        val_str = match_full.group(1).replace(",", "")
        try:
            val = Decimal(val_str)
            return val, 0.95, match_full.group(0)
        except Exception:
            pass

    return None, 0.0, None

def extract_contract_year_from_text(text: str) -> Tuple[Optional[int], float, Optional[str]]:
    """Extracts contract signing year (1990 to 2030) from free text."""
    if not text:
        return None, 0.0, None
    text = clean_arabic_digits(text)
    # Matches: contract 2021, contracted in 2020, عقد 2021
    pattern = r"(?:contract|contracted in|contract year|عقد|سنة العقد|تعاقد)\s*(?:in|عام|سنة)?\s*(20[0-2][0-9]|199[0-9])\b"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1)), 0.90, match.group(0)
    return None, 0.0, None

def extract_installment_terms_from_text(text: str) -> Dict[str, Any]:
    """Extracts installment duration and frequency from text."""
    result = {"years": None, "frequency": None, "snippet": None}
    if not text:
        return result
    text = clean_arabic_digits(text)
    
    # Years remaining: e.g. 6 years, 7 سنوات, 8 سنين
    years_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:years|yrs|سنوات|سنين|سنة)\b", text, re.IGNORECASE)
    if years_match:
        try:
            result["years"] = Decimal(years_match.group(1))
            result["snippet"] = years_match.group(0)
        except Exception:
            pass

    # Frequency: quarterly / monthly / semi-annual / annual
    if re.search(r"\b(?:quarterly|كل 3 شهور|ربع سنوي)\b", text, re.IGNORECASE):
        result["frequency"] = "Quarterly"
    elif re.search(r"\b(?:monthly|شهريا?|كل شهر)\b", text, re.IGNORECASE):
        result["frequency"] = "Monthly"
    elif re.search(r"\b(?:semi-annually?|نصف سنوي)\b", text, re.IGNORECASE):
        result["frequency"] = "Semi-Annual"
    elif re.search(r"\b(?:annually?|سنويا?)\b", text, re.IGNORECASE):
        result["frequency"] = "Annual"

    return result

def extract_amenities_from_text(text: str) -> List[str]:
    """Extracts amenities mentioned in free text against controlled vocabulary."""
    found = set()
    if not text:
        return list(found)
    text_lower = text.lower()
    
    keywords = {
        "Swimming Pool": ["pool", "swimming", "حمام سباحة", "بيسين", "لاجون", "lagoon"],
        "Elevator": ["elevator", "lift", "مصعد", "اسانسير"],
        "Garage": ["garage", "parking", "جراج", "موقف سيارات", "باكية"],
        "24/7 Security": ["security", "guard", "أمن", "حراسة", "كاميرات"],
        "Private Garden": ["private garden", "garden", "حديقة خاصة", "جاردن"],
        "Roof": ["roof", "رووف", "سطح"],
        "Clubhouse": ["clubhouse", "club house", "كلوب هاوس", "نادي"],
        "Gym": ["gym", "fitness", "جيم", "صالة رياضية"],
        "Balcony": ["balcony", "terrace", "بلكونة", "تراس"],
        "Commercial Area": ["commercial", "services", "خدمات", "مول", "mall"]
    }
    
    for amenity_name, terms in keywords.items():
        for term in terms:
            if term in text_lower or term in text:
                found.add(amenity_name)
                break
                
    return sorted(list(found))

