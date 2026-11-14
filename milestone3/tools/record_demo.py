"""
Automated Demo Walkthrough & Video Recorder for Milestone III
Uses Playwright to interactively navigate through all 10 functionalities,
records high-definition browser video, and converts it to MP4 via ffmpeg.
"""
import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:5000"
DEMO_DIR = Path(__file__).resolve().parent.parent / "deliverables" / "demo"
TEMP_VIDEO_DIR = DEMO_DIR / "temp_video"
FINAL_MP4_PATH = DEMO_DIR / "aqarexit_milestone3_demo.mp4"

def step_scroll(page, target_y, duration=1.2, steps=10):
    current_y = page.evaluate("window.scrollY")
    diff = (target_y - current_y) / steps
    for _ in range(steps):
        current_y += diff
        page.evaluate(f"window.scrollTo(0, {current_y})")
        time.sleep(duration / steps)

def run_demo_recording():
    print("\n" + "=" * 70, flush=True)
    print("🎬 STARTING AUTOMATED MILESTONE III DEMO VIDEO RECORDING", flush=True)
    print(f"Target App: {BASE_URL}", flush=True)
    print(f"Output MP4: {FINAL_MP4_PATH}", flush=True)
    print("=" * 70, flush=True)

    if TEMP_VIDEO_DIR.exists():
        shutil.rmtree(TEMP_VIDEO_DIR)
    TEMP_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(TEMP_VIDEO_DIR),
            record_video_size={"width": 1440, "height": 900}
        )
        page = context.new_page()
        page.set_default_timeout(8000)

        # ---------------------------------------------------------------------
        # Scene 1: Executive Analytics Dashboard
        # ---------------------------------------------------------------------
        print("[Scene 1/11] Executive Analytics Dashboard Overview...", flush=True)
        page.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(2.0)
        step_scroll(page, 450, duration=1.5, steps=12)
        time.sleep(1.2)
        step_scroll(page, 850, duration=1.5, steps=12)
        time.sleep(1.2)
        step_scroll(page, 0, duration=1.2, steps=10)
        time.sleep(1.5)

        # ---------------------------------------------------------------------
        # Scene 2: Navigation Dropdown Interaction
        # ---------------------------------------------------------------------
        print("[Scene 2/11] Navigation Dropdown Menus...", flush=True)
        try:
            page.click("button:has-text('Market Analytics')")
            time.sleep(1.5)
            page.click("button:has-text('Account & Reviews')")
            time.sleep(1.5)
            page.click("body") # close dropdown
        except Exception as e:
            print(f"Dropdown click note: {e}", flush=True)

        # ---------------------------------------------------------------------
        # Scene 3: F01 - User Registration
        # ---------------------------------------------------------------------
        print("[Scene 3/11] F01: User Registration & Dynamic Derived Age...", flush=True)
        page.goto(f"{BASE_URL}/f01-register", wait_until="networkidle")
        time.sleep(1.5)
        step_scroll(page, 300, duration=1.0, steps=8)
        
        demo_username = f"karim_auc_rec_{int(time.time()) % 10000}"
        page.fill("input[name='username']", demo_username)
        time.sleep(0.3)
        page.fill("input[name='email']", f"{demo_username}@example.com")
        time.sleep(0.3)
        page.select_option("select[name='gender']", "Male")
        time.sleep(0.3)
        page.fill("input[name='birthdate']", "1998-05-12")
        time.sleep(0.3)
        
        # Select 2 focus areas
        options = page.query_selector_all("select[name='focus_areas'] option")
        if len(options) >= 3:
            page.select_option("select[name='focus_areas']", [options[1].get_attribute("value"), options[2].get_attribute("value")])
        time.sleep(0.6)

        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        time.sleep(2.5) # show derived age alert

        # ---------------------------------------------------------------------
        # Scene 4: F02 & F03 - Project Reviews
        # ---------------------------------------------------------------------
        print("[Scene 4/11] F02 & F03: Project Search & Community Reviews...", flush=True)
        page.goto(f"{BASE_URL}/reviews?dev_id=42", wait_until="networkidle")
        time.sleep(1.5)
        step_scroll(page, 350, duration=1.0, steps=8)
        time.sleep(1.0)

        # Fill review form if signed in
        if page.query_selector("input[name='rating']"):
            page.fill("input[name='rating']", "9")
            time.sleep(0.4)
            page.fill("textarea[name='review_text']", "Exceptional compound landscaping, reliable underground parking, and modern architectural finishings.")
            time.sleep(0.6)
            page.click("button:has-text('Submit Project Review')")
            page.wait_for_load_state("networkidle")
            time.sleep(2.0)
        else:
            time.sleep(1.5)
        step_scroll(page, 300, duration=1.0, steps=8)
        time.sleep(1.0)

        # ---------------------------------------------------------------------
        # Scene 5: F04 - Top 10 Projects by Type
        # ---------------------------------------------------------------------
        print("[Scene 5/11] F04: Top 10 Projects by Type (3-Way Ranking & Chart.js)...", flush=True)
        page.goto(f"{BASE_URL}/f04-top-projects?type_id=1", wait_until="networkidle")
        time.sleep(1.5)
        step_scroll(page, 350, duration=1.0, steps=8)
        time.sleep(1.2)
        try:
            page.click("button:has-text('Resale Capital')")
            time.sleep(1.5)
            page.click("button:has-text('Gain Over Market Value')")
            time.sleep(1.5)
            page.click("button:has-text('Resale Inventory')")
            time.sleep(1.0)
        except Exception:
            pass

        # ---------------------------------------------------------------------
        # Scene 6: F05 - Development Deep Dive
        # ---------------------------------------------------------------------
        print("[Scene 6/11] F05: Development Deep Dive & Pricing Matrix...", flush=True)
        page.goto(f"{BASE_URL}/f05-development?dev_id=165", wait_until="networkidle")
        time.sleep(1.5)
        step_scroll(page, 450, duration=1.2, steps=10)
        time.sleep(1.5)

        # ---------------------------------------------------------------------
        # Scene 7: F06 - Area Hierarchy via Recursive CTE
        # ---------------------------------------------------------------------
        print("[Scene 7/11] F06: Area Hierarchy & Listings (Recursive CTE)...", flush=True)
        page.goto(f"{BASE_URL}/f06-area-properties?area_id=20", wait_until="networkidle")
        time.sleep(1.5)
        step_scroll(page, 550, duration=1.5, steps=12)
        time.sleep(1.5)

        # ---------------------------------------------------------------------
        # Scene 8: F07 - Amenities Multi-Filter (Relational Division)
        # ---------------------------------------------------------------------
        print("[Scene 8/11] F07: Amenities Multi-Filter (Relational Division)...", flush=True)
        page.goto(f"{BASE_URL}/f07-amenity-filter?area_id=20&amenities=1&amenities=2&match_mode=ALL", wait_until="networkidle")
        time.sleep(1.5)
        step_scroll(page, 450, duration=1.2, steps=10)
        time.sleep(1.5)

        # ---------------------------------------------------------------------
        # Scene 9: F08 - Top 5 Developers
        # ---------------------------------------------------------------------
        print("[Scene 9/11] F08: Top 5 Developers by Resale Inventory...", flush=True)
        page.goto(f"{BASE_URL}/f08-top-developers", wait_until="networkidle")
        time.sleep(1.5)
        step_scroll(page, 400, duration=1.0, steps=8)
        time.sleep(1.5)

        # ---------------------------------------------------------------------
        # Scene 10: F09 - Area × Type × Year Matrix
        # ---------------------------------------------------------------------
        print("[Scene 10/11] F09: Multi-Dimensional Slicing Matrix...", flush=True)
        page.goto(f"{BASE_URL}/f09-area-type-year?area_id=20", wait_until="networkidle")
        time.sleep(1.5)
        step_scroll(page, 500, duration=1.2, steps=10)
        time.sleep(1.5)

        # ---------------------------------------------------------------------
        # Scene 11: F10 - Benchmark Averages & CSV Export
        # ---------------------------------------------------------------------
        print("[Scene 11/11] F10: Benchmark Averages & Single-Click CSV Export...", flush=True)
        page.goto(f"{BASE_URL}/f10-averages?min_prop=3", wait_until="networkidle")
        time.sleep(1.5)
        step_scroll(page, 450, duration=1.2, steps=10)
        time.sleep(1.0)
        
        # Trigger CSV download
        try:
            with page.expect_download(timeout=5000) as download_info:
                page.click("a:has-text('Export CSV')")
            download = download_info.value
            download_path = DEMO_DIR / "aqarexit_f10_download_test.csv"
            download.save_as(str(download_path))
            print(f"✓ Verified F10 CSV download: {download_path}", flush=True)
            if download_path.exists():
                download_path.unlink()
        except Exception as e:
            print(f"Note: CSV download trigger simulated ({e})", flush=True)
        time.sleep(1.5)

        # Return to Dashboard & Highlight Remote Host Proof in Footer
        page.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(1.5)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2.5)

        page.close()
        context.close()
        browser.close()

    recorded_files = list(TEMP_VIDEO_DIR.glob("*.webm"))
    if not recorded_files:
        print("❌ Error: No video file was generated by Playwright.", flush=True)
        sys.exit(1)

    raw_video = recorded_files[0]
    raw_size_mb = raw_video.stat().st_size / (1024 * 1024)
    print(f"\n[Post-Processing] Raw WebM Video Captured: {raw_video.name} ({raw_size_mb:.2f} MB)", flush=True)

    print(f"[Post-Processing] Transcoding to H.264 MP4: {FINAL_MP4_PATH.name} ...", flush=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(FINAL_MP4_PATH)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0 and FINAL_MP4_PATH.exists():
        mp4_size_mb = FINAL_MP4_PATH.stat().st_size / (1024 * 1024)
        print(f"🎉 SUCCESS! Milestone III demo recording is ready: {FINAL_MP4_PATH.name} ({mp4_size_mb:.2f} MB)", flush=True)
        shutil.rmtree(TEMP_VIDEO_DIR)
    else:
        fallback_path = DEMO_DIR / "aqarexit_milestone3_demo.webm"
        shutil.move(str(raw_video), str(fallback_path))
        print(f"✓ Video saved as WebM: {fallback_path}", flush=True)
        if TEMP_VIDEO_DIR.exists():
            shutil.rmtree(TEMP_VIDEO_DIR)

if __name__ == "__main__":
    run_demo_recording()
