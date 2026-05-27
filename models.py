# models.py
# Yahan hum define karte hain ki MongoDB mein data kaisa store hoga

from datetime import datetime


def match_schema(
    match_id,
    title,
    match_url,
    match_date,
    venue,
    status,
    team1,
    team2,
):
    """
    Match list page se aane wala basic match data.
    """
    return {
        "match_id": match_id,          # Unique ID (URL se nikala hua)
        "title": title,                # e.g. "India vs Australia"
        "match_url": match_url,        # CREX match detail page URL
        "match_date": match_date,      # Match ki date/time
        "venue": venue,                # Stadium ka naam
        "status": status,              # "upcoming" / "live" / "completed"
        "team1": team1,
        "team2": team2,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def match_info_schema(match_id, info_data):
    """
    Match Info tab ka data — toss, umpires, match type, etc.
    """
    return {
        "match_id": match_id,
        "match_type": info_data.get("match_type", ""),       # T20, ODI, Test
        "toss": info_data.get("toss", ""),                   # Toss winner + decision
        "umpires": info_data.get("umpires", []),             # List of umpires
        "referee": info_data.get("referee", ""),
        "venue": info_data.get("venue", ""),
        "series": info_data.get("series", ""),               # Series ka naam
        "updated_at": datetime.utcnow(),
    }


def squads_schema(match_id, team_name, players):
    """
    Squads tab — dono teams ke players ki list.
    players = list of dicts: [{name, role, is_playing_xi}, ...]
    """
    return {
        "match_id": match_id,
        "team_name": team_name,
        "players": players,            # [{name, role, is_playing_xi}]
        "updated_at": datetime.utcnow(),
    }


def scorecard_schema(match_id, innings_data):
    """
    Scorecard tab — batting aur bowling ka complete data.
    innings_data = list of innings, har innings mein batting + bowling
    """
    return {
        "match_id": match_id,
        "innings": innings_data,
        # innings format:
        # [{
        #   "team": "India",
        #   "total": "250/8",
        #   "overs": "50",
        #   "batting": [{name, runs, balls, fours, sixes, sr, dismissal}],
        #   "bowling": [{name, overs, maidens, runs, wickets, economy}],
        # }]
        "updated_at": datetime.utcnow(),
    }


def live_score_schema(match_id, live_data):
    """
    Live tab — current score, current batsmen, current bowler.
    """
    return {
        "match_id": match_id,
        "current_score": live_data.get("current_score", ""),   # e.g. "120/3"
        "overs": live_data.get("overs", ""),                   # e.g. "15.2"
        "run_rate": live_data.get("run_rate", ""),
        "batsmen": live_data.get("batsmen", []),               # [{name, runs, balls}]
        "bowler": live_data.get("bowler", {}),                 # {name, overs, runs, wickets}
        "last_wicket": live_data.get("last_wicket", ""),
        "required_rate": live_data.get("required_rate", ""),
        "updated_at": datetime.utcnow(),
    }
