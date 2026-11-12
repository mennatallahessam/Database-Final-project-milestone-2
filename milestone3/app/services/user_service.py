"""
User Service (F01)
Handles user registration, profile retrieval, and demographic validation.
Enforces email format, username uniqueness, birthdate reality, and focus areas in a single transaction.
"""
import re
from datetime import date, datetime
from milestone3.app.db import get_db
from milestone3.app.queries import (
    SQL_F01_CHECK_EXISTING,
    SQL_F01_INSERT_USER,
    SQL_F01_INSERT_FOCUS_AREA,
    SQL_F01_GET_PROFILE,
    SQL_F01_GET_USER_FOCUS_AREAS
)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
ALLOWED_GENDERS = {'male', 'female', 'other', 'prefer_not_to_say'}

def validate_user_input(username: str, email: str, gender: str, birthdate_str: str, focus_area_ids: list):
    """Client/Server dual validation for registration fields."""
    errors = []
    
    # 1. Username
    username = (username or "").strip()
    if not username or len(username) < 3 or len(username) > 50:
        errors.append("Username must be between 3 and 50 characters.")
        
    # 2. Email
    email = (email or "").strip().lower()
    if not email or not EMAIL_REGEX.match(email):
        errors.append("A valid email address is required (e.g. user@example.com).")
        
    # 3. Gender
    if gender and gender not in ALLOWED_GENDERS:
        errors.append(f"Invalid gender selection. Choose from: {', '.join(ALLOWED_GENDERS)}.")
        
    # 4. Birthdate & Age Consistency
    parsed_date = None
    if not birthdate_str:
        errors.append("Birthdate is required.")
    else:
        try:
            parsed_date = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
            today = date.today()
            if parsed_date >= today:
                errors.append("Birthdate must be a past date.")
            elif parsed_date.year < 1920:
                errors.append("Birthdate must be after 1920.")
        except ValueError:
            errors.append("Birthdate must be formatted as YYYY-MM-DD.")
            
    # 5. Focus Areas (at least one)
    if not focus_area_ids:
        errors.append("At least one main area of focus must be selected.")
        
    return errors, username, email, gender or None, parsed_date

def register_user(username: str, email: str, gender: str, birthdate_str: str, focus_area_ids: list):
    """
    Registers a new user and records their focus areas in a SINGLE transaction.
    Returns (success: bool, data_or_errors: dict)
    """
    errors, clean_username, clean_email, clean_gender, clean_bdate = validate_user_input(
        username, email, gender, birthdate_str, focus_area_ids
    )
    if errors:
        return False, {"errors": errors}

    db = get_db()
    with db.get_cursor() as cursor:
        # Step 1: Check existing unique constraints with user-friendly messages
        cursor.execute(SQL_F01_CHECK_EXISTING, (clean_email, clean_username))
        existing = cursor.fetchone()
        if existing:
            if existing["email"].lower() == clean_email:
                return False, {"errors": [f"Email '{clean_email}' is already registered."]}
            if existing["username"].lower() == clean_username.lower():
                return False, {"errors": [f"Username '{clean_username}' is already taken."]}

        # Step 2: Insert into app_user
        cursor.execute(SQL_F01_INSERT_USER, (clean_username, clean_email, clean_gender, clean_bdate))
        user_id = cursor.lastrowid

        # Step 3: Insert all focus areas in the SAME transaction
        for loc_id in set(focus_area_ids):
            cursor.execute(SQL_F01_INSERT_FOCUS_AREA, (user_id, int(loc_id)))

        # Step 4: Fetch created profile with derived age via v_user_profile view
        cursor.execute(SQL_F01_GET_PROFILE, (user_id,))
        profile = cursor.fetchone()
        
        cursor.execute(SQL_F01_GET_USER_FOCUS_AREAS, (user_id,))
        profile["focus_areas"] = cursor.fetchall()

    return True, profile

def get_user_by_identifier(identifier: str):
    """Lightweight authentication/lookup by username or email for review authoring."""
    if not identifier:
        return None
    ident = identifier.strip().lower()
    db = get_db()
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT u.user_id, u.username, u.email, u.gender, u.birthdate, u.age, u.registered_at
            FROM v_user_profile u
            WHERE LOWER(u.username) = %s OR LOWER(u.email) = %s
            LIMIT 1;
        """, (ident, ident))
        user = cursor.fetchone()
        if user:
            cursor.execute(SQL_F01_GET_USER_FOCUS_AREAS, (user["user_id"],))
            user["focus_areas"] = cursor.fetchall()
        return user
