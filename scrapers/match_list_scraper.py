# scrapers/match_list_scraper.py
import hashlib
import requests
from bs4 import BeautifulSoup
from models import match_schema
from database import matches_col, save_or_update

BASE_URL = "https://crex.com"
SCHEDULE_URL = "https://crex.com/fixtures/match-list"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def make_match_id(url):
    return hashlib.md5(url.encode()).hexdigest()[:12]

def scrape_match_list():
    print("=" * 50)
    print("Match list scraping shuru ho rahi hai...")
    print(f"URL: {SCHEDULE_URL}")
    print("=" * 50)

    match_urls = []

    try:
        r = requests.get(SCHEDULE_URL, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')

        match_cards = soup.find_all('a', href=lambda x: x and '/cricket-live-score/' in x)
        print(f"\n{len(match_cards)} match cards mile!")

        for card in match_cards:
            try:
                match_url = BASE_URL + card['href']
                if match_url in match_urls:
                    continue

                text = card.get_text(separator='\n').strip()
                lines = [l.strip() for l in text.split('\n') if l.strip()]

                title = lines[0] if lines else "Unknown"
                match_date = lines[1] if len(lines) > 1 else ""
                venue = lines[2] if len(lines) > 2 else ""

                full_text = text.lower()
                if "live" in full_text:
                    status = "live"
                elif "won" in full_text or "result" in full_text:
                    status = "completed"
                else:
                    status = "upcoming"

                teams = title.split(" vs ")
                team1 = teams[0].strip() if teams else ""
                team2 = teams[1].strip() if len(teams) > 1 else ""

                match_id = make_match_id(match_url)
                data = match_schema(match_id, title, match_url, match_date, venue, status, team1, team2)
                save_or_update(matches_col, {"match_id": match_id}, data)
                match_urls.append(match_url)
                print(f"  ✓ Saved: {title} ({status})")

            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue

    except Exception as e:
        print(f"ERROR: {e}")

    print(f"\nTotal {len(match_urls)} matches save kiye gaye!")
    return match_urls