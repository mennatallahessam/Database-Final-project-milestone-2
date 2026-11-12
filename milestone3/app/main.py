"""
Milestone III Flask Application Factory & Route Controller
Exposes routes for all 10 project functionalities (F01 to F10).
Integrates startup security guards, session management, and friendly error handlers.
"""
import os
import sys
from pathlib import Path
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, Response
)
import pymysql
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

from milestone3.app.db import get_db, verify_remote_host
from milestone3.app.services.user_service import (
    register_user, get_user_by_identifier
)
from milestone3.app.services.review_service import (
    add_review, get_project_reviews
)
from milestone3.app.services.analytics_service import (
    get_lookups, search_developments, search_areas,
    get_top_projects, get_development_details,
    get_area_properties, get_filtered_amenity_properties,
    get_top_developers, get_properties_grouped_summary,
    get_area_dev_averages
)

def create_app(allow_local: bool = False):
    # Verify remote host upon initialization
    host_name = verify_remote_host(allow_local=allow_local)
    
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )
    app.secret_key = os.getenv("APP_SECRET", "super_secret_m3_resale_key_auc_f26")

    # Global context processor to make remote DB host and current user available to all templates
    @app.context_processor
    def inject_global_data():
        current_user = None
        user_ident = session.get("user_identifier")
        if user_ident:
            try:
                current_user = get_user_by_identifier(user_ident)
            except Exception:
                current_user = None
        return {
            "remote_db_host": host_name,
            "current_user": current_user
        }

    # -------------------------------------------------------------------------
    # Home Dashboard
    # -------------------------------------------------------------------------
    @app.route("/")
    def index():
        return render_template("index.html")

    # -------------------------------------------------------------------------
    # F01: User Registration & Session
    # -------------------------------------------------------------------------
    @app.route("/f01-register", methods=["GET", "POST"])
    def f01_register():
        lookups = get_lookups()
        if request.method == "POST":
            username = request.form.get("username", "")
            email = request.form.get("email", "")
            gender = request.form.get("gender", "")
            birthdate = request.form.get("birthdate", "")
            focus_areas = request.form.getlist("focus_areas")

            success, result = register_user(username, email, gender, birthdate, focus_areas)
            if success:
                session["user_identifier"] = result["username"]
                flash(f"User '{result['username']}' registered successfully! (Derived Age: {result['age']})", "success")
                return redirect(url_for("f01_register"))
            else:
                for err in result.get("errors", ["Registration failed."]):
                    flash(err, "error")

        return render_template("f01_register.html", locations=lookups["locations"])

    @app.route("/login", methods=["POST"])
    def login():
        identifier = request.form.get("identifier", "").strip()
        user = get_user_by_identifier(identifier)
        if user:
            session["user_identifier"] = user["username"]
            flash(f"Welcome back, {user['username']}!", "success")
        else:
            flash(f"User '{identifier}' not found. Please register first.", "error")
        return redirect(request.referrer or url_for("f01_register"))

    @app.route("/logout")
    def logout():
        session.pop("user_identifier", None)
        flash("You have signed out.", "info")
        return redirect(url_for("index"))

    # -------------------------------------------------------------------------
    # F02 & F03: Project Reviews
    # -------------------------------------------------------------------------
    @app.route("/reviews")
    def f02_f03_reviews():
        search_query = request.args.get("search", "").strip()
        dev_id = request.args.get("dev_id", type=int)
        page = request.args.get("page", 1, type=int)

        dev_search_results = []
        if search_query:
            dev_search_results = search_developments(search_query, limit=12)

        selected_dev = None
        review_data = None
        if dev_id:
            review_data = get_project_reviews(dev_id, page=page, page_size=8)
            if review_data:
                selected_dev = review_data["summary"]

        return render_template(
            "f02_f03_reviews.html",
            search_query=search_query,
            dev_search_results=dev_search_results,
            selected_dev=selected_dev,
            review_data=review_data
        )

    @app.route("/f02-post-review", methods=["POST"])
    def f02_post_review():
        user_ident = session.get("user_identifier")
        user = get_user_by_identifier(user_ident) if user_ident else None
        if not user:
            flash("Please sign in or register before submitting a review.", "error")
            return redirect(url_for("f01_register"))

        development_id = request.form.get("development_id", type=int)
        rating = request.form.get("rating", type=int)
        review_text = request.form.get("review_text", "")

        success, result = add_review(user["user_id"], development_id, rating, review_text)
        if success:
            flash("Your project review has been posted successfully!", "success")
            return redirect(url_for("f02_f03_reviews", dev_id=development_id))
        else:
            for err in result.get("errors", ["Failed to add review."]):
                flash(err, "error")
            return redirect(url_for("f02_f03_reviews", dev_id=development_id))

    # -------------------------------------------------------------------------
    # F04: Top 10 Projects by Type
    # -------------------------------------------------------------------------
    @app.route("/f04-top-projects")
    def f04_top_projects():
        lookups = get_lookups()
        pts = lookups["property_types"]
        default_type_id = pts[0]["property_type_id"] if pts else 1
        
        type_id = request.args.get("type_id", default_type_id, type=int)
        min_listings = request.args.get("min_listings", 3, type=int)
        exclude_outliers = request.args.get("exclude_outliers", "1") == "1"

        top_data = get_top_projects(type_id, min_listings=min_listings, exclude_outliers=exclude_outliers)

        return render_template(
            "f04_top_projects.html",
            property_types=pts,
            selected_type_id=type_id,
            min_listings=min_listings,
            exclude_outliers=exclude_outliers,
            top_data=top_data,
            excluded_count=top_data["excluded_count"]
        )

    # -------------------------------------------------------------------------
    # F05: Development Location & Pricing
    # -------------------------------------------------------------------------
    @app.route("/f05-development")
    def f05_dev_location():
        search_query = request.args.get("search", "").strip()
        dev_id = request.args.get("dev_id", type=int)

        dev_search_results = []
        if search_query:
            dev_search_results = search_developments(search_query, limit=12)

        dev_data = None
        if dev_id:
            dev_data = get_development_details(dev_id)

        return render_template(
            "f05_dev_location.html",
            search_query=search_query,
            dev_search_results=dev_search_results,
            dev_data=dev_data
        )

    # -------------------------------------------------------------------------
    # F06: Area Hierarchy & Listings
    # -------------------------------------------------------------------------
    @app.route("/f06-area-properties")
    def f06_area_properties():
        lookups = get_lookups()
        locations = lookups["locations"]
        default_area_id = locations[0]["location_id"] if locations else 1

        area_id = request.args.get("area_id", default_area_id, type=int)
        page = request.args.get("page", 1, type=int)
        sort_col = request.args.get("sort", "price")
        sort_dir = request.args.get("dir", "ASC")

        area_data = get_area_properties(area_id, page=page, page_size=20, sort_col=sort_col, sort_dir=sort_dir)

        return render_template(
            "f06_area_properties.html",
            locations=locations,
            selected_area_id=area_id,
            area_data=area_data
        )

    # -------------------------------------------------------------------------
    # F07: Multi-Amenity Search
    # -------------------------------------------------------------------------
    @app.route("/f07-amenity-filter")
    def f07_amenity_filter():
        lookups = get_lookups()
        locations = lookups["locations"]
        amenities = lookups["amenities"]
        default_area_id = locations[0]["location_id"] if locations else 1

        area_id = request.args.get("area_id", default_area_id, type=int)
        min_p = request.args.get("min_price", type=float)
        max_p = request.args.get("max_price", type=float)
        selected_amenities = [int(a) for a in request.args.getlist("amenities") if a.isdigit()]
        match_mode = request.args.get("match_mode", "ALL")

        filter_results = None
        if request.args:
            filter_results = get_filtered_amenity_properties(
                area_id, min_price=min_p, max_price=max_p,
                amenity_ids=selected_amenities, match_mode=match_mode,
                page=1, page_size=25
            )

        return render_template(
            "f07_amenity_filter.html",
            locations=locations,
            amenities=amenities,
            selected_area_id=area_id,
            min_price=min_p,
            max_price=max_p,
            selected_amenities=selected_amenities,
            match_mode=match_mode,
            filter_results=filter_results
        )

    # -------------------------------------------------------------------------
    # F08: Top 5 Developers
    # -------------------------------------------------------------------------
    @app.route("/f08-top-developers")
    def f08_top_developers():
        lookups = get_lookups()
        pts = lookups["property_types"]
        type_id = request.args.get("type_id", type=int)

        developers = get_top_developers(property_type_id=type_id)

        return render_template(
            "f08_top_developers.html",
            property_types=pts,
            selected_type_id=type_id,
            developers=developers
        )

    # -------------------------------------------------------------------------
    # F09: Area × Type × Year Matrix
    # -------------------------------------------------------------------------
    @app.route("/f09-area-type-year")
    def f09_area_type_year():
        lookups = get_lookups()
        locations = lookups["locations"]
        pts = lookups["property_types"]
        years = lookups["contract_years"]
        default_area_id = locations[0]["location_id"] if locations else 1

        area_id = request.args.get("area_id", default_area_id, type=int)
        type_id = request.args.get("type_id", type=int)
        year = request.args.get("year", type=int)

        matrix_rows = get_properties_grouped_summary(area_id, property_type_id=type_id, contract_year=year)

        return render_template(
            "f09_area_type_year.html",
            locations=locations,
            property_types=pts,
            contract_years=years,
            selected_area_id=area_id,
            selected_type_id=type_id,
            selected_year=year,
            matrix_rows=matrix_rows
        )

    # -------------------------------------------------------------------------
    # F10: Area & Development Benchmark Averages
    # -------------------------------------------------------------------------
    @app.route("/f10-averages")
    def f10_averages():
        lookups = get_lookups()
        locations = lookups["locations"]

        area_id = request.args.get("area_id", type=int)
        min_prop = request.args.get("min_prop", 3, type=int)
        sort_col = request.args.get("sort", "property_count")
        sort_dir = request.args.get("dir", "DESC")
        page = request.args.get("page", 1, type=int)

        table_data = get_area_dev_averages(
            location_id=area_id, min_properties=min_prop,
            page=page, page_size=20, sort_col=sort_col, sort_dir=sort_dir
        )

        return render_template(
            "f10_averages.html",
            locations=locations,
            selected_area_id=area_id,
            min_prop=min_prop,
            sort_col=sort_col,
            sort_dir=sort_dir,
            table_data=table_data
        )

    @app.route("/f10-export-csv")
    def f10_export_csv():
        area_id = request.args.get("area_id", type=int)
        min_prop = request.args.get("min_prop", 3, type=int)
        sort_col = request.args.get("sort", "property_count")
        sort_dir = request.args.get("dir", "DESC")

        csv_content = get_area_dev_averages(
            location_id=area_id, min_properties=min_prop,
            sort_col=sort_col, sort_dir=sort_dir, export_csv=True
        )

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=aqarexit_f10_benchmark_averages.csv"}
        )

    # -------------------------------------------------------------------------
    # Friendly Error Handler for Unreachable Remote Database
    # -------------------------------------------------------------------------
    @app.errorhandler(ConnectionError)
    @app.errorhandler(pymysql.OperationalError)
    def handle_database_connection_error(e):
        return render_template(
            "partials/db_error.html",
            error_message=str(e),
            remote_db_host=host_name
        ), 503

    return app

if __name__ == "__main__":
    allow_local_flag = "--allow-local" in sys.argv
    app = create_app(allow_local=allow_local_flag)
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1")
    print(f"🚀 Starting AqarExit Analytics Web Server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
