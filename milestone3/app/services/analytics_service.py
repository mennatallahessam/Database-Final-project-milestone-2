"""
Analytics Service (F04 - F10)
Powers all real-estate market intelligence and analytical queries.
Enforces parameterized query execution, whitelisted dynamic sorting,
recursive CTE geographic expansion, and outlier filtering.
"""
import io
import csv
from milestone3.app.db import get_db
from milestone3.app.queries import (
    ALLOWED_SORT_COLUMNS,
    SQL_GET_PROPERTY_TYPES,
    SQL_GET_AMENITIES,
    SQL_GET_LOCATIONS_TREE,
    SQL_GET_DISTINCT_CONTRACT_YEARS,
    SQL_SEARCH_DEVELOPMENTS,
    SQL_SEARCH_AREAS,
    SQL_F04_TOP_PROJECTS,
    SQL_F04_EXCLUDED_COUNT,
    SQL_F05_DEV_LOCATION,
    SQL_F05_LOCATION_PATH,
    SQL_F05_UNIT_TYPES,
    SQL_F06_AREA_SUMMARY,
    SQL_F06_PROPERTIES_PAGINATED,
    SQL_F06_COUNT,
    SQL_F08_TOP_DEVELOPERS,
    SQL_F09_GROUPED_SUMMARY,
    SQL_F10_AREA_DEV_AVERAGES,
    SQL_F10_COUNT,
    build_f07_query
)

def get_lookups():
    """Fetches common lookup tables (cached for session use)."""
    db = get_db()
    with db.get_cursor() as cursor:
        cursor.execute(SQL_GET_PROPERTY_TYPES)
        types = cursor.fetchall()
        cursor.execute(SQL_GET_AMENITIES)
        amenities = cursor.fetchall()
        cursor.execute(SQL_GET_LOCATIONS_TREE)
        locations = cursor.fetchall()
        cursor.execute(SQL_GET_DISTINCT_CONTRACT_YEARS)
        years = [row["contract_year"] for row in cursor.fetchall()]
    return {
        "property_types": types,
        "amenities": amenities,
        "locations": locations,
        "contract_years": years
    }

def search_developments(query_str: str, limit: int = 15):
    """Type-ahead autocomplete for developments (limited to avoid rendering 6,300 items)."""
    db = get_db()
    term = f"%{query_str.strip()}%"
    with db.get_cursor() as cursor:
        cursor.execute(SQL_SEARCH_DEVELOPMENTS, (term, term, limit))
        return cursor.fetchall()

def search_areas(query_str: str, limit: int = 15):
    """Type-ahead autocomplete for areas."""
    db = get_db()
    term = f"%{query_str.strip()}%"
    with db.get_cursor() as cursor:
        cursor.execute(SQL_SEARCH_AREAS, (term, term, term, limit))
        return cursor.fetchall()

# -----------------------------------------------------------------------------
# F04: Top 10 projects by resale inventory, amount, gain by property type
# -----------------------------------------------------------------------------
def get_top_projects(property_type_id: int, min_listings: int = 3, exclude_outliers: bool = True):
    db = get_db()
    outlier_clause = "AND (p.price / p.area_sqm BETWEEN 1000 AND 300000)" if exclude_outliers else ""
    
    with db.get_cursor() as cursor:
        # 1. Rank by Resale Inventory
        q_inv = SQL_F04_TOP_PROJECTS.format(
            outlier_filter=outlier_clause,
            order_by="resale_inventory DESC, total_resale_amount DESC, d.name ASC"
        )
        cursor.execute(q_inv, (property_type_id, min_listings))
        top_inventory = cursor.fetchall()

        # 2. Rank by Resale Amount
        q_amt = SQL_F04_TOP_PROJECTS.format(
            outlier_filter=outlier_clause,
            order_by="total_resale_amount DESC, resale_inventory DESC, d.name ASC"
        )
        cursor.execute(q_amt, (property_type_id, min_listings))
        top_amount = cursor.fetchall()

        # 3. Rank by Gain over Market Value
        q_gain = SQL_F04_TOP_PROJECTS.format(
            outlier_filter=outlier_clause,
            order_by="avg_gain DESC, total_gain DESC, d.name ASC"
        )
        cursor.execute(q_gain, (property_type_id, min_listings))
        top_gain = cursor.fetchall()

        # 4. Count properties excluded because they lack development association
        cursor.execute(SQL_F04_EXCLUDED_COUNT, (property_type_id,))
        excluded = cursor.fetchone()["excluded_count"]

    return {
        "top_inventory": top_inventory,
        "top_amount": top_amount,
        "top_gain": top_gain,
        "excluded_count": excluded
    }

# -----------------------------------------------------------------------------
# F05: Location of a given development + avg price/sqm + listings per unit type
# -----------------------------------------------------------------------------
def get_development_details(development_id: int):
    db = get_db()
    with db.get_cursor() as cursor:
        cursor.execute(SQL_F05_DEV_LOCATION, (development_id,))
        dev_info = cursor.fetchone()
        if not dev_info:
            return None

        # Hierarchy Path
        if dev_info.get("location_id"):
            cursor.execute(SQL_F05_LOCATION_PATH, (dev_info["location_id"],))
            dev_info["location_path"] = cursor.fetchall()
        else:
            dev_info["location_path"] = []

        # Unit Types Breakdown
        cursor.execute(SQL_F05_UNIT_TYPES, (development_id,))
        unit_types = cursor.fetchall()

        # Compute 'All Types' Total Row
        total_listings = sum(r["listing_count"] for r in unit_types)
        weighted_avg_sqm = (
            round(sum(r["avg_price_sqm"] * r["listing_count"] for r in unit_types) / total_listings, 2)
            if total_listings > 0 else 0
        )
        total_row = {
            "type_name": "All Types (Total)",
            "listing_count": total_listings,
            "avg_price_sqm": weighted_avg_sqm,
            "min_price": min((r["min_price"] for r in unit_types), default=0),
            "max_price": max((r["max_price"] for r in unit_types), default=0)
        }

    return {
        "development": dev_info,
        "unit_types": unit_types,
        "total_row": total_row
    }

# -----------------------------------------------------------------------------
# F06: All properties in a certain area with avg price/sqm for each unit type
# -----------------------------------------------------------------------------
def get_area_properties(location_id: int, page: int = 1, page_size: int = 25, sort_col: str = "price", sort_dir: str = "ASC"):
    db = get_db()
    offset = max(0, (page - 1) * page_size)
    
    # Safe whitelisted sorting
    safe_col = ALLOWED_SORT_COLUMNS.get(sort_col, "p.price")
    safe_dir = "DESC" if sort_dir.upper() == "DESC" else "ASC"
    order_clause = f"{safe_col} {safe_dir}"

    with db.get_cursor() as cursor:
        # Summary table by unit type
        cursor.execute(SQL_F06_AREA_SUMMARY, (location_id,))
        summary = cursor.fetchall()

        # Total properties count
        cursor.execute(SQL_F06_COUNT, (location_id,))
        total_count = cursor.fetchone()["total_count"]

        # Paginated properties list
        query = SQL_F06_PROPERTIES_PAGINATED.format(order_by=order_clause)
        cursor.execute(query, (location_id, page_size, offset))
        properties = cursor.fetchall()

        total_pages = max(1, (total_count + page_size - 1) // page_size)

    return {
        "summary": summary,
        "properties": properties,
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "sort_col": sort_col,
        "sort_dir": safe_dir
    }

# -----------------------------------------------------------------------------
# F07: Properties in area, price range, with given amenities
# -----------------------------------------------------------------------------
def get_filtered_amenity_properties(
    location_id: int,
    min_price: float = None,
    max_price: float = None,
    amenity_ids: list = None,
    match_mode: str = "ALL",
    page: int = 1,
    page_size: int = 25,
    sort_col: str = "price",
    sort_dir: str = "ASC"
):
    db = get_db()
    offset = max(0, (page - 1) * page_size)
    clean_amenities = [int(a) for a in (amenity_ids or []) if str(a).isdigit()]

    safe_col = ALLOWED_SORT_COLUMNS.get(sort_col, "p.price")
    safe_dir = "DESC" if sort_dir.upper() == "DESC" else "ASC"
    order_clause = f"{safe_col} {safe_dir}"

    query_template = build_f07_query(clean_amenities, match_mode)
    sql_query = query_template.format(order_by=order_clause)

    params = [location_id]
    if clean_amenities:
        params.extend(clean_amenities)
    params.extend([min_price, min_price, max_price, max_price, page_size, offset])

    with db.get_cursor() as cursor:
        cursor.execute(sql_query, tuple(params))
        properties = cursor.fetchall()

    return {
        "properties": properties,
        "total_matches": len(properties),
        "page": page,
        "page_size": page_size,
        "match_mode": match_mode
    }

# -----------------------------------------------------------------------------
# F08: Top 5 developers by number of resale listings
# -----------------------------------------------------------------------------
def get_top_developers(property_type_id: int = None):
    db = get_db()
    with db.get_cursor() as cursor:
        cursor.execute(SQL_F08_TOP_DEVELOPERS, (property_type_id, property_type_id))
        developers = cursor.fetchall()
    return developers

# -----------------------------------------------------------------------------
# F09: All properties by area, property type, and contract year
# -----------------------------------------------------------------------------
def get_properties_grouped_summary(location_id: int, property_type_id: int = None, contract_year: int = None):
    db = get_db()
    with db.get_cursor() as cursor:
        cursor.execute(
            SQL_F09_GROUPED_SUMMARY,
            (location_id, property_type_id, property_type_id, contract_year, contract_year)
        )
        return cursor.fetchall()

# -----------------------------------------------------------------------------
# F10: Averages by area and development project
# -----------------------------------------------------------------------------
def get_area_dev_averages(
    location_id: int = None,
    min_properties: int = 3,
    page: int = 1,
    page_size: int = 25,
    sort_col: str = "property_count",
    sort_dir: str = "DESC",
    export_csv: bool = False
):
    db = get_db()
    offset = max(0, (page - 1) * page_size)

    safe_col = ALLOWED_SORT_COLUMNS.get(sort_col, "COUNT(p.property_id)")
    safe_dir = "ASC" if sort_dir.upper() == "ASC" else "DESC"
    order_clause = f"{safe_col} {safe_dir}"

    if export_csv:
        # Unlimited rows for export
        query = SQL_F10_AREA_DEV_AVERAGES.format(order_by=order_clause)
        with db.get_cursor() as cursor:
            cursor.execute(query, (location_id, location_id, min_properties, 5000, 0))
            rows = cursor.fetchall()
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "area_name", "development_name", "property_count",
                "avg_installment", "installment_count",
                "avg_down_payment", "down_payment_count",
                "avg_discount", "discount_count",
                "avg_contract_age", "contract_year_count",
                "avg_market_price", "market_price_count"
            ])
            writer.writeheader()
            for r in rows:
                writer.writerow({
                    "area_name": r["area_name"],
                    "development_name": r["development_name"],
                    "property_count": r["property_count"],
                    "avg_installment": r["avg_installment"] or "",
                    "installment_count": r["installment_count"],
                    "avg_down_payment": r["avg_down_payment"] or "",
                    "down_payment_count": r["down_payment_count"],
                    "avg_discount": r["avg_discount"] or "",
                    "discount_count": r["discount_count"],
                    "avg_contract_age": r["avg_contract_age"] or "",
                    "contract_year_count": r["contract_year_count"],
                    "avg_market_price": r["avg_market_price"] or "",
                    "market_price_count": r["market_price_count"]
                })
            return output.getvalue()

    with db.get_cursor() as cursor:
        query = SQL_F10_AREA_DEV_AVERAGES.format(order_by=order_clause)
        cursor.execute(query, (location_id, location_id, min_properties, page_size, offset))
        averages = cursor.fetchall()

    return {
        "averages": averages,
        "page": page,
        "page_size": page_size,
        "sort_col": sort_col,
        "sort_dir": safe_dir,
        "min_properties": min_properties
    }
