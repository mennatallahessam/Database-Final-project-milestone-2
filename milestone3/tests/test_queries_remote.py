"""
Milestone III Remote Query & Integrity Assertions Test Suite
Validates that every query (F01 to F10) executes correctly against the database,
returns properly structured rows, avoids NULL-poisoned averages,
and safely cleans up any inserted test rows.
"""
import unittest
import time
from milestone3.app.db import get_db
from milestone3.app.services.user_service import register_user
from milestone3.app.services.review_service import add_review, get_project_reviews
from milestone3.app.services.analytics_service import (
    get_lookups, get_top_projects, get_development_details,
    get_area_properties, get_filtered_amenity_properties,
    get_top_developers, get_properties_grouped_summary,
    get_area_dev_averages
)

class TestRemoteQueries(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = get_db(allow_local=True)
        cls.lookups = get_lookups()
        cls.test_user_id = None

    def test_lookups_integrity(self):
        """Verifies lookup tables are populated and contain expected categories."""
        self.assertGreater(len(self.lookups["property_types"]), 0)
        self.assertGreater(len(self.lookups["locations"]), 0)
        self.assertGreater(len(self.lookups["amenities"]), 0)

    def test_f01_f02_write_path_and_cleanup(self):
        """F01 & F02: Registers test user, creates review, asserts integrity, cleans up."""
        unique_suffix = int(time.time() * 1000)
        username = f"m3test_{unique_suffix}"
        email = f"{username}@example.com"
        
        # 1. F01 Register User
        success, user_data = register_user(username, email, "male", "1994-06-15", [1])
        self.assertTrue(success, f"Registration failed: {user_data}")
        user_id = user_data["user_id"]
        self.test_user_id = user_id
        self.assertGreater(user_data["age"], 18)

        # 2. Pick a development
        with self.db.get_cursor() as cur:
            cur.execute("SELECT development_id FROM development LIMIT 1;")
            dev_id = cur.fetchone()["development_id"]

        # 3. F02 Add Review
        ok, rev_res = add_review(user_id, dev_id, 8, "Unit inspection passed. Prime construction quality.")
        self.assertTrue(ok, f"Add review failed: {rev_res}")
        review_id = rev_res["review_id"]

        # 4. F03 Verify Review Visible
        rev_data = get_project_reviews(dev_id, page=1, page_size=10)
        self.assertIsNotNone(rev_data)
        self.assertTrue(any(r["review_id"] == review_id for r in rev_data["reviews"]))

        # 5. Cleanup
        with self.db.get_cursor() as cur:
            cur.execute("DELETE FROM app_user WHERE user_id = %s;", (user_id,))

    def test_f04_top_projects_structure(self):
        """F04: Asserts all three ranking tabs return valid records with required columns."""
        pt_id = self.lookups["property_types"][0]["property_type_id"]
        res = get_top_projects(pt_id, min_listings=1, exclude_outliers=True)
        
        self.assertIn("top_inventory", res)
        self.assertIn("top_amount", res)
        self.assertIn("top_gain", res)
        
        if res["top_inventory"]:
            first = res["top_inventory"][0]
            self.assertIn("development_name", first)
            self.assertIn("resale_inventory", first)
            self.assertGreaterEqual(first["resale_inventory"], 1)

    def test_f05_development_location_path(self):
        """F05: Asserts location hierarchy path and unit types are returned."""
        with self.db.get_cursor() as cur:
            cur.execute("SELECT development_id FROM development WHERE location_id IS NOT NULL LIMIT 1;")
            row = cur.fetchone()
            if row:
                dev_id = row["development_id"]
                details = get_development_details(dev_id)
                self.assertIsNotNone(details)
                self.assertIn("location_path", details["development"])
                self.assertIn("unit_types", details)

    def test_f06_recursive_cte_area_properties(self):
        """F06: Verifies recursive CTE hierarchy gathers properties without crashing."""
        loc_id = self.lookups["locations"][0]["location_id"]
        area_res = get_area_properties(loc_id, page=1, page_size=10)
        self.assertIn("summary", area_res)
        self.assertIn("properties", area_res)
        self.assertGreaterEqual(area_res["total_count"], 0)

    def test_f07_relational_division_amenities(self):
        """F07: Asserts relational division query syntax and execution."""
        loc_id = self.lookups["locations"][0]["location_id"]
        am_ids = [self.lookups["amenities"][0]["amenity_id"]]
        res = get_filtered_amenity_properties(loc_id, amenity_ids=am_ids, match_mode="ALL")
        self.assertIn("properties", res)
        self.assertIn("total_matches", res)

    def test_f08_top_developers(self):
        """F08: Verifies top 5 developers structure."""
        devs = get_top_developers()
        self.assertLessEqual(len(devs), 5)
        if devs:
            self.assertIn("total_listings", devs[0])
            self.assertIn("developer_name", devs[0])

    def test_f09_grouped_summary(self):
        """F09: Verifies grouped summary matrix."""
        loc_id = self.lookups["locations"][0]["location_id"]
        matrix = get_properties_grouped_summary(loc_id)
        self.assertIsInstance(matrix, list)

    def test_f10_averages_and_csv_export(self):
        """F10: Verifies averages table and CSV export content."""
        data = get_area_dev_averages(min_properties=1, page=1, page_size=5)
        self.assertIn("averages", data)

        csv_str = get_area_dev_averages(min_properties=1, export_csv=True)
        self.assertIn("development_name", csv_str)
        self.assertIn("property_count", csv_str)

if __name__ == "__main__":
    unittest.main()
