# scrapers/live_scraper.py
# Sirf live ya recently started matches ke liye:
# Live scores aur Scorecard scrape karta hai

import time
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from models import live_score_schema, scorecard_schema
from database import live_score_col, scorecard_col, matches_col, save_or_update


def make_match_id(url):
    return hashlib.md5(url.encode()).hexdigest()[:12]


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    return driver


def click_tab(driver, tab_name):
    try:
        tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//button[contains(text(), '{tab_name}')] | //a[contains(text(), '{tab_name}')]")
            )
        )
        tab.click()
        time.sleep(3)
        return True
    except Exception as e:
        print(f"  Tab '{tab_name}' click nahi ho saka: {e}")
        return False


def scrape_live_score(driver, match_id):
    """
    'Live' tab se current match score scrape karta hai.
    """
    print("  -> Live score scraping...")
    live_data = {}

    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text
        lines = [l.strip() for l in page_text.split("\n") if l.strip()]

        for i, line in enumerate(lines):
            line_lower = line.lower()
            next_val = lines[i + 1] if i + 1 < len(lines) else ""

            # Score format dhundho: jaise "145/3" ya "145-3"
            if "/" in line and any(c.isdigit() for c in line):
                if len(line) < 15:  # Short line = likely a score
                    live_data["current_score"] = line

            elif "overs" in line_lower:
                live_data["overs"] = next_val

            elif "run rate" in line_lower or "crr" in line_lower:
                live_data["run_rate"] = next_val

            elif "req" in line_lower and "rate" in line_lower:
                live_data["required_rate"] = next_val

            elif "last wicket" in line_lower:
                live_data["last_wicket"] = next_val

        # Batsmen dhundho (2 hote hain pitch par)
        batsmen = []
        for i, line in enumerate(lines):
            if line and lines[i - 1:i] and any(
                keyword in lines[i - 1].lower()
                for keyword in ["batting", "striker", "batsman"]
            ):
                batsmen.append({"name": line, "runs": "", "balls": ""})

        live_data["batsmen"] = batsmen
        live_data["bowler"] = {}  # Bowler details alag se parse kar sakte ho

    except Exception as e:
        print(f"  Live score parse error: {e}")

    data = live_score_schema(match_id, live_data)
    save_or_update(live_score_col, {"match_id": match_id}, data)
    print(f"  ✓ Live score saved: {live_data.get('current_score', 'N/A')}")


def scrape_scorecard(driver, match_id):
    """
    'Scorecard' tab se batting aur bowling ka poora data scrape karta hai.
    """
    print("  -> Scorecard scraping...")
    innings_list = []

    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text
        lines = [l.strip() for l in page_text.split("\n") if l.strip()]

        current_innings = None
        current_batting = []
        current_bowling = []
        mode = None  # "batting" ya "bowling"

        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Naya innings shuru
            if "innings" in line_lower and ("1st" in line_lower or "2nd" in line_lower):
                # Pichla innings save karo
                if current_innings:
                    current_innings["batting"] = current_batting
                    current_innings["bowling"] = current_bowling
                    innings_list.append(current_innings)

                current_innings = {
                    "team": line,
                    "total": "",
                    "overs": "",
                    "batting": [],
                    "bowling": [],
                }
                current_batting = []
                current_bowling = []
                mode = None

            # Mode switch
            elif "batting" in line_lower and len(line) < 20:
                mode = "batting"
            elif "bowling" in line_lower and len(line) < 20:
                mode = "bowling"

            # Total score line (jaise "250/8 (50 ov)")
            elif current_innings and "/" in line and "(" in line:
                current_innings["total"] = line

            # Batting row parse karo
            elif mode == "batting" and current_innings:
                # Rough check: player rows mein numbers hote hain
                parts = line.split()
                if len(parts) >= 4 and parts[-1].replace(".", "").isdigit():
                    current_batting.append({
                        "name": " ".join(parts[:2]),
                        "dismissal": "",   # Agle line se aa sakta hai
                        "runs": parts[-4] if len(parts) > 4 else "",
                        "balls": parts[-3] if len(parts) > 3 else "",
                        "fours": parts[-2] if len(parts) > 2 else "",
                        "sixes": parts[-1] if len(parts) > 1 else "",
                        "sr": "",
                    })

            # Bowling row parse karo
            elif mode == "bowling" and current_innings:
                parts = line.split()
                if len(parts) >= 5 and parts[-1].replace(".", "").isdigit():
                    current_bowling.append({
                        "name": " ".join(parts[:2]),
                        "overs": parts[2] if len(parts) > 2 else "",
                        "maidens": parts[3] if len(parts) > 3 else "",
                        "runs": parts[4] if len(parts) > 4 else "",
                        "wickets": parts[5] if len(parts) > 5 else "",
                        "economy": parts[-1] if parts else "",
                    })

        # Last innings save karo
        if current_innings:
            current_innings["batting"] = current_batting
            current_innings["bowling"] = current_bowling
            innings_list.append(current_innings)

    except Exception as e:
        print(f"  Scorecard parse error: {e}")

    data = scorecard_schema(match_id, innings_list)
    save_or_update(scorecard_col, {"match_id": match_id}, data)
    print(f"  ✓ Scorecard saved: {len(innings_list)} innings")


def scrape_live_matches():
    """
    MongoDB se SIRF live matches nikalo aur unka Live + Scorecard scrape karo.
    Yeh function bar bar call hota hai (scheduler ke through).
    """
    print("\n" + "=" * 50)
    print("Live matches check ho rahe hain...")

    # MongoDB se live matches nikalo
    live_matches = list(matches_col.find({"status": "live"}))
    print(f"{len(live_matches)} live match(es) mila!")

    if not live_matches:
        print("Abhi koi match live nahi hai.")
        return

    for match in live_matches:
        match_url = match.get("match_url", "")
        match_id = match.get("match_id", make_match_id(match_url))
        title = match.get("title", "Unknown")

        print(f"\nProcessing: {title}")
        driver = create_driver()

        try:
            driver.get(match_url)
            time.sleep(4)

            # Live tab
            if click_tab(driver, "Live"):
                scrape_live_score(driver, match_id)

            # Scorecard tab
            if click_tab(driver, "Scorecard"):
                scrape_scorecard(driver, match_id)

        except Exception as e:
            print(f"ERROR: {match_url} — {e}")

        finally:
            driver.quit()
