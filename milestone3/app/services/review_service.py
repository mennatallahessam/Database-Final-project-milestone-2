"""
Review Service (F02, F03)
Handles posting development project reviews and viewing existing project reviews.
"""
from milestone3.app.db import get_db
from milestone3.app.queries import (
    SQL_F02_CHECK_EXISTING_REVIEW,
    SQL_F02_INSERT_REVIEW,
    SQL_F03_GET_DEV_SUMMARY,
    SQL_F03_GET_REVIEWS_LIST,
    SQL_F05_LOCATION_PATH
)

def add_review(user_id: int, development_id: int, rating: int, review_text: str):
    """
    F02: Adds a new user review on a project development.
    Validates rating 1..10, text presence, and ensures clean error messages.
    """
    errors = []
    try:
        rating_int = int(rating)
        if rating_int < 1 or rating_int > 10:
            errors.append("Rating must be an integer between 1 and 10.")
    except (ValueError, TypeError):
        errors.append("Rating must be a valid number between 1 and 10.")
        
    cleaned_text = (review_text or "").strip()
    if not cleaned_text:
        errors.append("Review text cannot be empty.")
    elif len(cleaned_text) > 2000:
        errors.append("Review text is too long (maximum 2000 characters).")
        
    if not user_id:
        errors.append("You must be registered or signed in to write a review.")
        
    if not development_id:
        errors.append("Please select a valid development project.")
        
    if errors:
        return False, {"errors": errors}

    db = get_db()
    with db.get_cursor() as cursor:
        # Check if this user already reviewed this development
        cursor.execute(SQL_F02_CHECK_EXISTING_REVIEW, (user_id, development_id))
        existing = cursor.fetchone()
        if existing:
            return False, {
                "errors": [
                    f"You have already reviewed this project (Rating: {existing['rating']}/10). "
                    "Multiple reviews per project are restricted to prevent review manipulation."
                ]
            }

        # Insert new review
        cursor.execute(SQL_F02_INSERT_REVIEW, (user_id, development_id, rating_int, cleaned_text))
        new_review_id = cursor.lastrowid
        
    return True, {"review_id": new_review_id, "development_id": development_id}

def get_project_reviews(development_id: int, page: int = 1, page_size: int = 10):
    """
    F03: Fetches project development details, summary metrics, and paginated reviews.
    """
    db = get_db()
    offset = max(0, (page - 1) * page_size)
    
    with db.get_cursor() as cursor:
        # 1. Development summary
        cursor.execute(SQL_F03_GET_DEV_SUMMARY, (development_id,))
        summary = cursor.fetchone()
        
        if not summary:
            return None
            
        # 2. Location hierarchy path
        if summary.get("location_id"):
            cursor.execute(SQL_F05_LOCATION_PATH, (summary["location_id"],))
            summary["location_path"] = cursor.fetchall()
        else:
            summary["location_path"] = []

        # 3. Paginated reviews
        cursor.execute(SQL_F03_GET_REVIEWS_LIST, (development_id, page_size, offset))
        reviews = cursor.fetchall()
        
        total_reviews = summary["total_reviews"]
        total_pages = max(1, (total_reviews + page_size - 1) // page_size)
        
        return {
            "summary": summary,
            "reviews": reviews,
            "page": page,
            "page_size": page_size,
            "total_reviews": total_reviews,
            "total_pages": total_pages
        }
