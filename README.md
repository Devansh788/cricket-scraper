# Cricket Scraping System

CREX website se cricket match data scrape karke MongoDB Atlas mein save karta hai.

---

## Project Structure

    cricket_scraper/
    |-- scrapers/
    |   |-- __init__.py
    |   |-- match_list_scraper.py   (Match schedule page scraper)
    |   |-- match_detail_scraper.py (Match Info + Squads scraper)
    |   |-- live_scraper.py         (Live scores + Scorecard scraper)
    |-- models.py                   (MongoDB data schemas)
    |-- database.py                 (MongoDB connection)
    |-- main.py                     (Entry point)
    |-- requirements.txt            (Dependencies)
    |-- .env                        (Config - MongoDB URI)
    |-- README.md

---

## Setup Instructions

### 1. Dependencies install karo
```
pip install -r requirements.txt
```

### 2. .env file configure karo
```
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/cricket_db
DB_NAME=cricket_db
```

### 3. Run karo
```
python main.py
```

---

## Run Options

```
python main.py           # Ek baar run
python main.py live      # Live scores har 5 min
python main.py schedule  # Fully automated
```

---

## MongoDB Collections

| Collection   | Data                             |
|--------------|----------------------------------|
| matches      | Match list (title, date, teams)  |
| match_info   | Toss, umpires, venue, format     |
| squads       | Dono teams ke players            |
| scorecard    | Batting aur bowling stats        |
| live_scores  | Current score, batsmen, bowler   |

---

## Data Flow

```
CREX Website
     |
     v
match_list_scraper  -->  MongoDB: matches
     |
     v
match_detail_scraper --> MongoDB: match_info, squads
     |
     v
live_scraper         --> MongoDB: live_scores, scorecard
```

---

## Tech Stack

- Python 3.x
- Requests + BeautifulSoup4 (Web scraping)
- PyMongo (MongoDB driver)
- MongoDB Atlas (Cloud database)
- schedule (Task scheduling)
- python-dotenv (Config management)
