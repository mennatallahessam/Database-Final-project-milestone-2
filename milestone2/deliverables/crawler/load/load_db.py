import json
import argparse
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, Optional
import pymysql

from milestone2.config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    BASE_DIR,
    STAGING_DIR
)

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

def init_database():
    """Initializes schema from sql/schema.sql."""
    schema_file = BASE_DIR / "sql" / "schema.sql"
    print(f"Applying schema from {schema_file}...")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset="utf8mb4"
    )
    with conn.cursor() as cursor:
        with open(schema_file, "r", encoding="utf-8") as f:
            sql_statements = f.read().split(";")
            for stmt in sql_statements:
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt)
        conn.commit()
    conn.close()
    print("Schema initialized successfully.")

def load_staging_data():
    """Loads staged listings into MySQL database in FK dependency order."""
    staging_file = STAGING_DIR / "listings.jsonl"
    if not staging_file.exists():
        print(f"Staging file {staging_file} not found. Run parse_listing first.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # In-memory lookup caches to avoid redundant SELECTs
    cache_property_type: Dict[str, int] = {}
    cache_payment_method: Dict[str, int] = {}
    cache_amenity: Dict[str, int] = {}
    cache_location: Dict[str, int] = {}
    cache_developer: Dict[str, int] = {}
    cache_development: Dict[str, int] = {}

    def get_or_create_property_type(name: str) -> int:
        if name in cache_property_type:
            return cache_property_type[name]
        cursor.execute("SELECT property_type_id FROM property_type WHERE name = %s", (name,))
        row = cursor.fetchone()
        if row:
            tid = row["property_type_id"]
        else:
            cursor.execute("INSERT INTO property_type (name) VALUES (%s)", (name,))
            tid = cursor.lastrowid
        cache_property_type[name] = tid
        return tid

    def get_or_create_payment_method(name: str) -> int:
        if not name:
            return None
        if name in cache_payment_method:
            return cache_payment_method[name]
        cursor.execute("SELECT payment_method_id FROM payment_method WHERE name = %s", (name,))
        row = cursor.fetchone()
        if row:
            pid = row["payment_method_id"]
        else:
            cursor.execute("INSERT INTO payment_method (name) VALUES (%s)", (name,))
            pid = cursor.lastrowid
        cache_payment_method[name] = pid
        return pid

    def get_or_create_amenity(name: str) -> int:
        if name in cache_amenity:
            return cache_amenity[name]
        cursor.execute("SELECT amenity_id FROM amenity WHERE name = %s", (name,))
        row = cursor.fetchone()
        if row:
            aid = row["amenity_id"]
        else:
            cursor.execute("INSERT INTO amenity (name) VALUES (%s)", (name,))
            aid = cursor.lastrowid
        cache_amenity[name] = aid
        return aid

    def get_or_create_location(name: str, parent_id: Optional[int] = None, loc_type: str = "area") -> int:
        if not name:
            name = "Cairo"
        key = f"{parent_id}_{name.lower()}"
        if key in cache_location:
            return cache_location[key]
        cursor.execute("SELECT location_id FROM location WHERE name = %s AND (parent_location_id = %s OR (parent_location_id IS NULL AND %s IS NULL))", (name, parent_id, parent_id))
        row = cursor.fetchone()
        if row:
            lid = row["location_id"]
        else:
            cursor.execute("INSERT INTO location (parent_location_id, name, location_type) VALUES (%s, %s, %s)", (parent_id, name, loc_type))
            lid = cursor.lastrowid
        cache_location[key] = lid
        return lid

    def get_or_create_developer(name: Optional[str]) -> Optional[int]:
        if not name:
            return None
        if name in cache_developer:
            return cache_developer[name]
        cursor.execute("SELECT developer_id FROM developer WHERE name = %s", (name,))
        row = cursor.fetchone()
        if row:
            did = row["developer_id"]
        else:
            slug = name.lower().replace(" ", "-")[:150]
            cursor.execute("INSERT INTO developer (name, slug) VALUES (%s, %s)", (name, slug))
            did = cursor.lastrowid
        cache_developer[name] = did
        return did

    def get_or_create_development(name: Optional[str], dev_id: Optional[int], loc_id: Optional[int]) -> Optional[int]:
        if not name:
            return None
        key = f"{dev_id}_{name.lower()}"
        if key in cache_development:
            return cache_development[key]
        cursor.execute("SELECT development_id FROM development WHERE name = %s AND (developer_id = %s OR (developer_id IS NULL AND %s IS NULL))", (name, dev_id, dev_id))
        row = cursor.fetchone()
        if row:
            d_id = row["development_id"]
        else:
            cursor.execute("INSERT INTO development (developer_id, location_id, name) VALUES (%s, %s, %s)", (dev_id, loc_id, name))
            d_id = cursor.lastrowid
        cache_development[key] = d_id
        return d_id

    # 0. Ensure root governorate exists
    root_cairo_id = get_or_create_location("Cairo", None, "governorate")
    new_cairo_id = get_or_create_location("New Cairo", root_cairo_id, "city")

    # Read and process listings in batches
    loaded_properties = 0
    loaded_amenities = 0

    with open(staging_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)

            # 1. Lookups
            type_id = get_or_create_property_type(rec.get("property_type_name", "Apartment"))
            pm_id = get_or_create_payment_method(rec.get("payment_method_name"))
            
            # Location
            loc_name = rec.get("location_name") or "New Cairo"
            loc_id = get_or_create_location(loc_name, new_cairo_id, "area")

            # Developer & Development
            dev_comp_id = get_or_create_developer(rec.get("developer_name"))
            development_id = get_or_create_development(rec.get("development_name"), dev_comp_id, loc_id)

            # 2. Upsert Property
            sql_prop = """
                INSERT INTO property (
                    source_listing_id, source_url, title, description,
                    development_id, location_id, property_type_id, payment_method_id,
                    area_sqm, bedrooms, bathrooms, price, market_price, down_payment,
                    installment_amount, installment_frequency, installment_years, remaining_balance,
                    gain_over_market_value, gain_percentage, discount_over_market_price,
                    contract_year, delivery_year, currency
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    description = VALUES(description),
                    development_id = VALUES(development_id),
                    location_id = VALUES(location_id),
                    property_type_id = VALUES(property_type_id),
                    payment_method_id = VALUES(payment_method_id),
                    area_sqm = VALUES(area_sqm),
                    bedrooms = VALUES(bedrooms),
                    bathrooms = VALUES(bathrooms),
                    price = VALUES(price),
                    market_price = VALUES(market_price),
                    down_payment = VALUES(down_payment),
                    installment_amount = VALUES(installment_amount),
                    installment_frequency = VALUES(installment_frequency),
                    installment_years = VALUES(installment_years),
                    remaining_balance = VALUES(remaining_balance),
                    gain_over_market_value = VALUES(gain_over_market_value),
                    gain_percentage = VALUES(gain_percentage),
                    discount_over_market_price = VALUES(discount_over_market_price),
                    contract_year = VALUES(contract_year),
                    delivery_year = VALUES(delivery_year)
            """
            cursor.execute(sql_prop, (
                rec["source_listing_id"],
                rec["source_url"],
                rec.get("title"),
                rec.get("description"),
                development_id,
                loc_id,
                type_id,
                pm_id,
                rec["area_sqm"],
                rec.get("bedrooms"),
                rec.get("bathrooms"),
                rec["price"],
                rec.get("market_price"),
                rec.get("down_payment"),
                rec.get("installment_amount"),
                rec.get("installment_frequency"),
                rec.get("installment_years"),
                rec.get("remaining_balance"),
                rec.get("gain_over_market_value"),
                rec.get("gain_percentage"),
                rec.get("discount_over_market_price"),
                rec.get("contract_year"),
                rec.get("delivery_year"),
                rec.get("currency", "EGP")
            ))

            # Retrieve property_id
            cursor.execute("SELECT property_id FROM property WHERE source_listing_id = %s", (rec["source_listing_id"],))
            p_row = cursor.fetchone()
            property_id = p_row["property_id"]
            loaded_properties += 1

            # 3. Property Amenities (M:N)
            for amenity_name in rec.get("amenities", []):
                aid = get_or_create_amenity(amenity_name)
                cursor.execute("""
                    INSERT IGNORE INTO property_amenity (property_id, amenity_id)
                    VALUES (%s, %s)
                """, (property_id, aid))
                loaded_amenities += 1

    conn.commit()
    conn.close()

    print("\n--- DATABASE LOAD SUMMARY ---")
    print(f"Properties Upserted: {loaded_properties}")
    print(f"Amenity Links Upserted: {loaded_amenities}")

def main():
    parser = argparse.ArgumentParser(description="Load Staged Property Data into MySQL")
    parser.add_argument("--init", action="store_true", help="Re-initialize schema from sql/schema.sql")
    args = parser.parse_args()

    if args.init:
        init_database()
    load_staging_data()

if __name__ == "__main__":
    main()

