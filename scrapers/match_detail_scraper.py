# scrapers/match_detail_scraper.py
import hashlib
import requests
from bs4 import BeautifulSoup
from models import match_info_schema, squads_schema
from database import match_info_col, squads_col, save_or_update

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def make_match_id(url):
    return hashlib.md5(url.encode()).hexdigest()[:12]

def scrape_match_info(soup, match_id):
    print("  -> Match Info scraping...")
    info_data = {}
    try:
        text = soup.get_text(separator='\n')
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for i, line in enumerate(lines):
            ll = line.lower()
            nxt = lines[i+1] if i+1 < len(lines) else ""
            if "match type" in ll or "format" in ll:
                info_data["match_type"] = nxt
            elif "toss" in ll and not info_data.get("toss"):
                info_data["toss"] = nxt
            elif "venue" in ll and not info_data.get("venue"):
                info_data["venue"] = nxt
            elif "umpire" in ll:
                info_data.setdefault("umpires", []).append(nxt)
            elif "referee" in ll:
                info_data["referee"] = nxt
            elif "series" in ll and not info_data.get("series"):
                info_data["series"] = nxt
    except Exception as e:
        print(f"  Match info error: {e}")
    data = match_info_schema(match_id, info_data)
    save_or_update(match_info_col, {"match_id": match_id}, data)
    print(f"  ✓ Match Info saved")

def scrape_squads(soup, match_id):
    print("  -> Squads scraping...")
    try:
        text = soup.get_text(separator='\n')
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        current_team = None
        current_players = []
        teams_data = {}
        for line in lines:
            if " xi" in line.lower() or "squad" in line.lower():
                if current_team and current_players:
                    teams_data[current_team] = current_players
                current_team = line
                current_players = []
            elif current_team and len(line) > 2:
                role = ""
                name = line
                if "(c)" in line.lower():
                    role = "Captain"
                    name = line.replace("(c)", "").replace("(C)", "").strip()
                elif "(wk)" in line.lower():
                    role = "Wicket-keeper"
                    name = line.replace("(wk)", "").replace("(WK)", "").strip()
                current_players.append({"name": name, "role": role, "is_playing_xi": True})
        if current_team and current_players:
            teams_data[current_team] = current_players
        for team_name, players in teams_data.items():
            data = squads_schema(match_id, team_name, players)
            save_or_update(squads_col, {"match_id": match_id, "team_name": team_name}, data)
            print(f"  ✓ Squad saved: {team_name} ({len(players)} players)")
    except Exception as e:
        print(f"  Squads error: {e}")

def scrape_match_detail(match_url):
    match_id = make_match_id(match_url)
    print(f"\nMatch detail scraping: {match_url}")
    try:
        r = requests.get(match_url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        scrape_match_info(soup, match_id)
        scrape_squads(soup, match_id)
    except Exception as e:
        print(f"ERROR: {e}")