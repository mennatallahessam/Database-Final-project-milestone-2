"""
Milestone III End-to-End Smoke Test
Runs all 10 project functionalities (F01 to F10) against the configured database,
measures execution duration, and asserts structural correctness.
"""
import sys
import time
from tabulate import tabulate
from milestone3.app.db import get_db
from milestone3.app.services.user_service import register_user, get_user_by_identifier
from milestone3.app.services.review_service import add_review, get_project_reviews
from milestone3.app.services.analytics_service import (
    get_lookups, get_top_projects, get_development_details,
    get_area_properties, get_filtered_amenity_properties,
    get_top_developers, get_properties_grouped_summary,
    get_area_dev_averages
)

def run_smoke_test(allow_local: bool = False):
    print("\n" + "=" * 70)
    print("AQAREXIT MILESTONE III: END-TO-END SMOKE TEST (F01 - F10)")
    print("=" * 70)

    db = get_db(allow_local=allow_local)
    results = []
    
    # -------------------------------------------------------------------------
    # Lookups Check
    # -------------------------------------------------------------------------
    t0 = time.time()
    try:
        lookups = get_lookups()
        dur = (time.time() - t0) * 1000
        assert len(lookups["property_types"]) > 0, "Missing property types"
        assert len(lookups["locations"]) > 0, "Missing locations"
        results.append(["Lookups (Types, Locations, Amenities)", "PASS", f"{dur:.2f} ms", f"{len(lookups['locations'])} locations loaded"])
    except Exception as e:
        results.append(["Lookups", "FAIL", "-", str(e)])

    # -------------------------------------------------------------------------
    # F01: Register User & Focus Areas
    # -------------------------------------------------------------------------
    test_user = f"m3smoke_{int(time.time())}"
    test_email = f"{test_user}@example.com"
    t0 = time.time()
    created_user_id = None
    try:
        success, res = register_user(test_user, test_email, "female", "1998-03-20", [1, 2])
        dur = (time.time() - t0) * 1000
        if success:
            created_user_id = res["user_id"]
            results.append(["F01: User Registration & Derived Age", "PASS", f"{dur:.2f} ms", f"User #{created_user_id}, Age: {res['age']}"])
        else:
            results.append(["F01: User Registration", "FAIL", f"{dur:.2f} ms", str(res.get("errors"))])
    except Exception as e:
        results.append(["F01: User Registration", "FAIL", "-", str(e)])

    # -------------------------------------------------------------------------
    # F02 & F03: Reviews
    # -------------------------------------------------------------------------
    t0 = time.time()
    try:
        # Find a valid development id
        with db.get_cursor() as cur:
            cur.execute("SELECT development_id FROM development LIMIT 1;")
            dev_id = cur.fetchone()["development_id"]
            
        if created_user_id and dev_id:
            ok, rev_res = add_review(created_user_id, dev_id, 9, "Excellent project layout and prime facilities.")
            dur = (time.time() - t0) * 1000
            if ok:
                results.append(["F02: Add Project Review", "PASS", f"{dur:.2f} ms", f"Review #{rev_res['review_id']}"])
            else:
                results.append(["F02: Add Project Review", "FAIL", f"{dur:.2f} ms", str(rev_res.get("errors"))])
        else:
            results.append(["F02: Add Project Review", "SKIP", "-", "No user or development"])
    except Exception as e:
        results.append(["F02: Add Project Review", "FAIL", "-", str(e)])

    # F03: View Project Reviews
    t0 = time.time()
    try:
        rev_data = get_project_reviews(dev_id, page=1, page_size=5)
        dur = (time.time() - t0) * 1000
        assert rev_data is not None
        results.append(["F03: View Existing Project Reviews", "PASS", f"{dur:.2f} ms", f"{rev_data['total_reviews']} reviews total"])
    except Exception as e:
        results.append(["F03: View Project Reviews", "FAIL", "-", str(e)])

    # -------------------------------------------------------------------------
    # F04: Top 10 Projects by Type
    # -------------------------------------------------------------------------
    t0 = time.time()
    try:
        type_id = lookups["property_types"][0]["property_type_id"]
        top_res = get_top_projects(type_id, min_listings=2)
        dur = (time.time() - t0) * 1000
        results.append(["F04: Top 10 Projects by Type", "PASS", f"{dur:.2f} ms", f"{len(top_res['top_inventory'])} inventory, {len(top_res['top_gain'])} gain"])
    except Exception as e:
        results.append(["F04: Top 10 Projects", "FAIL", "-", str(e)])

    # -------------------------------------------------------------------------
    # F05: Development Deep Dive
    # -------------------------------------------------------------------------
    t0 = time.time()
    try:
        dev_details = get_development_details(dev_id)
        dur = (time.time() - t0) * 1000
        results.append(["F05: Development Location & Breakdown", "PASS", f"{dur:.2f} ms", f"{len(dev_details['unit_types'])} unit types"])
    except Exception as e:
        results.append(["F05: Development Location", "FAIL", "-", str(e)])

    # -------------------------------------------------------------------------
    # F06: Area Hierarchy & Listings
    # -------------------------------------------------------------------------
    t0 = time.time()
    try:
        loc_id = lookups["locations"][0]["location_id"]
        area_res = get_area_properties(loc_id, page=1, page_size=10)
        dur = (time.time() - t0) * 1000
        results.append(["F06: Area Hierarchy & Listings", "PASS", f"{dur:.2f} ms", f"{area_res['total_count']} properties in tree"])
    except Exception as e:
        results.append(["F06: Area Hierarchy", "FAIL", "-", str(e)])

    # -------------------------------------------------------------------------
    # F07: Multi-Amenity Search
    # -------------------------------------------------------------------------
    t0 = time.time()
    try:
        am_ids = [a["amenity_id"] for a in lookups["amenities"][:2]]
        f07_res = get_filtered_amenity_properties(loc_id, min_price=500000, max_price=50000000, amenity_ids=am_ids, match_mode="ALL")
        dur = (time.time() - t0) * 1000
        results.append(["F07: Multi-Amenity Relational Division", "PASS", f"{dur:.2f} ms", f"{f07_res['total_matches']} matches"])
    except Exception as e:
        results.append(["F07: Multi-Amenity Search", "FAIL", "-", str(e)])

    # -------------------------------------------------------------------------
    # F08: Top 5 Developers
    # -------------------------------------------------------------------------
    t0 = time.time()
    try:
        top_devs = get_top_developers()
        dur = (time.time() - t0) * 1000
        results.append(["F08: Top 5 Developers", "PASS", f"{dur:.2f} ms", f"{len(top_devs)} developers returned"])
    except Exception as e:
        results.append(["F08: Top 5 Developers", "FAIL", "-", str(e)])

    # -------------------------------------------------------------------------
    # F09: Area × Type × Year Matrix
    # -------------------------------------------------------------------------
    t0 = time.time()
    try:
        matrix = get_properties_grouped_summary(loc_id)
        dur = (time.time() - t0) * 1000
        results.append(["F09: Area × Type × Year Matrix", "PASS", f"{dur:.2f} ms", f"{len(matrix)} clusters"])
    except Exception as e:
        results.append(["F09: Grouped Summary Matrix", "FAIL", "-", str(e)])

    # -------------------------------------------------------------------------
    # F10: Area & Development Averages
    # -------------------------------------------------------------------------
    t0 = time.time()
    try:
        f10_data = get_area_dev_averages(min_properties=2, page=1, page_size=10)
        dur = (time.time() - t0) * 1000
        results.append(["F10: Area-Development Averages", "PASS", f"{dur:.2f} ms", f"{len(f10_data['averages'])} rows returned"])
    except Exception as e:
        results.append(["F10: Benchmark Averages", "FAIL", "-", str(e)])

    # -------------------------------------------------------------------------
    # Cleanup Test User & Review
    # -------------------------------------------------------------------------
    if created_user_id:
        try:
            with db.get_cursor() as cur:
                cur.execute("DELETE FROM app_user WHERE user_id = %s;", (created_user_id,))
            print(f"\n[✓] Cleaned up temporary smoke test user #{created_user_id} and associated review/focus rows.")
        except Exception as e:
            print(f"[!] Warning: Test row cleanup error: {e}")

    # Print Summary Table
    print("\n" + tabulate(results, headers=["Functionality", "Status", "Duration", "Details"], tablefmt="github"))
    all_passed = all(r[1] == "PASS" for r in results)
    print("\n" + ("=" * 70))
    if all_passed:
        print("🎉 ALL 10 FUNCTIONALITIES PASSED END-TO-END SMOKE TESTS!")
    else:
        print("⚠️ SOME FUNCTIONALITIES ENCOUNTERED ISSUES — REVIEW ABOVE TABLE.")
    print("=" * 70 + "\n")
    return all_passed

if __name__ == "__main__":
    allow_local = "--allow-local" in sys.argv
    run_smoke_test(allow_local=allow_local)
