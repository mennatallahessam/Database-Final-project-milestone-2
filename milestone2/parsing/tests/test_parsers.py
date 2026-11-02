import unittest
from decimal import Decimal
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
    validate_and_quarantine,
    parse_decimal_value
)

class TestParserExtraction(unittest.TestCase):

    def test_clean_arabic_digits(self):
        self.assertEqual(clean_arabic_digits("١٢٣٤٥"), "12345")
        self.assertEqual(clean_arabic_digits("السعر ٢٠٢٥"), "السعر 2025")

    def test_extract_area(self):
        val, conf, snip = extract_area_from_text("شقة فاخرة بمساحة 176 m² للبيع")
        self.assertEqual(val, Decimal("176"))
        self.assertGreater(conf, 0.8)

        val_ar, _, _ = extract_area_from_text("المساحة ١٥٠ م²")
        self.assertEqual(val_ar, Decimal("150"))

    def test_extract_bedrooms(self):
        val, conf, _ = extract_bedrooms_from_text("4 BR apartment overlooking lake")
        self.assertEqual(val, 4)

        val_studio, _, _ = extract_bedrooms_from_text("Modern studio in New Cairo")
        self.assertEqual(val_studio, 0)

        val_ar, _, _ = extract_bedrooms_from_text("شقة ٣ غرف نوم وصالة")
        self.assertEqual(val_ar, 3)

    def test_extract_bathrooms(self):
        val, _, _ = extract_bathrooms_from_text("Spacious unit with 2 bathrooms and terrace")
        self.assertEqual(val, 2)

    def test_extract_money(self):
        val, _, _ = extract_money_amount("Cash required now: EGP 3,600,000 only")
        self.assertEqual(val, Decimal("3600000"))

        val_m, _, _ = extract_money_amount("Total price 3.6M EGP")
        self.assertEqual(val_m, Decimal("3600000"))

    def test_extract_contract_year(self):
        year, _, _ = extract_contract_year_from_text("Signed contract in 2021 with developer")
        self.assertEqual(year, 2021)

    def test_extract_installment_terms(self):
        terms = extract_installment_terms_from_text("Installments over 6 years, quarterly payments")
        self.assertEqual(terms["years"], Decimal("6"))
        self.assertEqual(terms["frequency"], "Quarterly")

    def test_extract_amenities(self):
        text = "المشروع يحتوي على حمام سباحة، وجراج خاص، وأمن ٢٤ ساعة، ومصعد"
        amenities = extract_amenities_from_text(text)
        self.assertIn("Swimming Pool", amenities)
        self.assertIn("Garage", amenities)
        self.assertIn("24/7 Security", amenities)
        self.assertIn("Elevator", amenities)

    def test_developer_resolution(self):
        self.assertEqual(resolve_developer("lavista"), "La Vista Developments")
        self.assertEqual(resolve_developer("PALM HILLS Developments"), "Palm Hills Developments")
        self.assertEqual(resolve_developer("Emaar Misr"), "Emaar Misr")

    def test_property_type_resolution(self):
        self.assertEqual(resolve_property_type("شقة"), "Apartment")
        self.assertEqual(resolve_property_type("فيلا"), "Villa")
        self.assertEqual(resolve_property_type("تاون هاوس"), "Townhouse")
        self.assertEqual(resolve_property_type("محل"), "Shop")
        self.assertEqual(resolve_property_type("مكتب"), "Office")

    def test_location_hierarchy_resolution(self):
        from milestone2.parsing.normalize import load_location_hierarchy, resolve_location
        hierarchy = load_location_hierarchy()
        
        # Test North Coast
        loc_nc = resolve_location("الساحل الشمالي", hierarchy)
        self.assertEqual(loc_nc["governorate_en"], "Matrouh")
        self.assertEqual(loc_nc["city_en"], "North Coast")

        # Test New Administrative Capital
        loc_nac = resolve_location("العاصمة الإدارية الجديدة", hierarchy)
        self.assertEqual(loc_nac["governorate_en"], "Cairo")

        # Test 6th of October
        loc_oct = resolve_location("6 أكتوبر", hierarchy)
        self.assertEqual(loc_oct["governorate_en"], "Giza")
        self.assertEqual(loc_oct["city_en"], "6th of October")

    def test_validation_and_quarantine(self):
        # Valid listing
        valid_rec = {
            "source_listing_id": "TEST-001",
            "source_url": "https://example.com/1",
            "price": Decimal("5000000"),
            "area_sqm": Decimal("150"),
            "down_payment": Decimal("2000000"),
            "bedrooms": 3,
            "contract_year": 2022,
            "location_name": "New Cairo"
        }
        is_val, reason = validate_and_quarantine(valid_rec)
        self.assertTrue(is_val)
        self.assertIsNone(reason)

        # Invalid price (<= 0)
        neg_price_rec = dict(valid_rec, price=Decimal("-1000"))
        is_val, reason = validate_and_quarantine(neg_price_rec)
        self.assertFalse(is_val)
        self.assertIn("Invalid price", reason)

        # Invalid down payment (> price)
        bad_dp_rec = dict(valid_rec, down_payment=Decimal("9000000"))
        is_val, reason = validate_and_quarantine(bad_dp_rec)
        self.assertFalse(is_val)
        self.assertIn("exceeds total price", reason)

if __name__ == "__main__":
    unittest.main()

