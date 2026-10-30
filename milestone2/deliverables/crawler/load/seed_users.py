import random
from datetime import datetime, timedelta, date
from faker import Faker
import pymysql

from milestone2.config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME
)

# Realistic English Review Templates
REVIEW_TEMPLATES = [
    "Great community with excellent landscaping and solid building finishes. Very quiet atmosphere.",
    "The compound amenities are top-notch, especially the club house and swimming pools.",
    "Prompt security and clean common areas. A bit distant from the highway, but overall very peaceful.",
    "High quality construction by the developer. Handover inspection was smooth with minimal snagging.",
    "Good project infrastructure, though maintenance fees have risen slightly this past year.",
    "Impressive architectural design and spacious underground parking. Perfect for growing families.",
    "Prime location with easy access to schools and commercial malls. Highly recommend for living or resale.",
    "Very satisfied with the facility management and green spaces. Roads and streetlights are well maintained.",
    "Quiet residential neighborhood with reliable 24/7 security. The community vibe is exceptional.",
    "Nice views over the lakes and lagoons. Delivery was slightly later than estimated, but quality made up for it."
]

def seed_synthetic_user_data(num_users: int = 40, num_reviews: int = 120):
    """Generates synthetic users, focus areas, and project reviews with fixed seed 2501."""
    fake = Faker()
    Faker.seed(2501)
    random.seed(2501)

    print(f"Connecting to {DB_NAME} to seed {num_users} users and {num_reviews} reviews...")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )
    cursor = conn.cursor()

    try:
        # 1. Clear existing synthetic user tables (idempotency)
        cursor.execute("DELETE FROM review")
        cursor.execute("DELETE FROM user_focus_area")
        cursor.execute("DELETE FROM app_user")

        # 2. Retrieve real existing locations from the location table
        cursor.execute("SELECT location_id FROM location")
        loc_rows = cursor.fetchall()
        location_ids = [r["location_id"] for r in loc_rows]
        if not location_ids:
            cursor.execute("INSERT INTO location (name, location_type) VALUES ('Cairo', 'governorate')")
            location_ids = [cursor.lastrowid]

        # 3. Retrieve real existing developments from the development table
        cursor.execute("SELECT development_id, name FROM development")
        dev_rows = cursor.fetchall()
        if not dev_rows:
            cursor.execute("INSERT INTO development (name) VALUES ('Sample Compound')")
            dev_rows = [{"development_id": cursor.lastrowid, "name": "Sample Compound"}]
        development_ids = [r["development_id"] for r in dev_rows]

        # 4. Generate Users
        user_ids = []
        user_reg_dates = {}
        usernames_set = set()

        genders = ["male", "female", "other", "prefer_not_to_say"]
        gender_weights = [0.48, 0.48, 0.02, 0.02]

        print(f"Creating {num_users} synthetic users...")
        for i in range(1, num_users + 1):
            first_name = fake.first_name()
            last_name = fake.last_name()
            base_username = f"{first_name.lower()}_{last_name.lower()}"
            username = base_username
            counter = 1
            while username in usernames_set:
                username = f"{base_username}_{counter}"
                counter += 1
            usernames_set.add(username)

            email = f"{username}@{fake.domain_word()}.example.com"
            gender = random.choices(genders, weights=gender_weights)[0]

            # Age between 22 and 65
            age_years = random.randint(22, 65)
            birth_year = date.today().year - age_years
            birthdate = fake.date_between_dates(
                date_start=date(birth_year, 1, 1),
                date_end=date(birth_year, 12, 28)
            )

            # Registration timestamp within the last 365 days
            days_ago = random.randint(5, 365)
            registered_at = datetime.utcnow() - timedelta(days=days_ago)

            cursor.execute("""
                INSERT INTO app_user (username, email, gender, birthdate, registered_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, email, gender, birthdate, registered_at))
            u_id = cursor.lastrowid
            user_ids.append(u_id)
            user_reg_dates[u_id] = registered_at

            # 5. Link 1 to 4 Focus Areas per User (M:N)
            focus_count = random.randint(1, min(4, len(location_ids)))
            chosen_locs = random.sample(location_ids, focus_count)
            for lid in chosen_locs:
                cursor.execute("""
                    INSERT INTO user_focus_area (user_id, location_id)
                    VALUES (%s, %s)
                """, (u_id, lid))

        # 6. Generate Reviews
        print(f"Creating {num_reviews} synthetic reviews on real developments...")
        ratings_pool = [6, 7, 8, 8, 9, 9, 10, 10, 5, 4] # realistic skew towards positive
        for r_idx in range(1, num_reviews + 1):
            uid = random.choice(user_ids)
            did = random.choice(development_ids)
            rating = random.choice(ratings_pool)
            base_text = random.choice(REVIEW_TEMPLATES)
            dev_name = next(d["name"] for d in dev_rows if d["development_id"] == did)
            review_text = f"{base_text} ({dev_name})"

            # Created timestamp must be strictly after user's registration
            u_reg = user_reg_dates[uid]
            now = datetime.utcnow()
            if now > u_reg + timedelta(hours=1):
                days_window = max(1, (now - u_reg).days)
                review_date = u_reg + timedelta(days=random.randint(1, days_window), hours=random.randint(1, 12))
            else:
                review_date = now

            cursor.execute("""
                INSERT INTO review (user_id, development_id, rating, review_text, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (uid, did, rating, review_text, review_date))

        conn.commit()
        print("\n--- USER SEEDING SUMMARY ---")
        print(f"Users Seeded: {len(user_ids)}")
        print(f"Focus Area Links: {num_users * 2} (approx)")
        print(f"Reviews Seeded: {num_reviews}")

    except Exception as e:
        conn.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    seed_synthetic_user_data()

