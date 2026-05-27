# 🏏 Cricket Scraping System

CREX website se cricket match data scrape karke MongoDB mein save karta hai.

---

## 📁 Project Structure

```
cricket_scraper/
├── scrapers/
│   ├── __init__.py
│   ├── match_list_scraper.py   # Match schedule page scraper
│   ├── match_detail_scraper.py # Match Info + Squads scraper
│   └── live_scraper.py         # Live scores + Scorecard scraper
├── models.py                   # MongoDB data schemas
├── database.py                 # MongoDB connection
├── main.py                     # Entry point (yahan se run karo)
├── requirements.txt            # Python dependencies
├── .env                        # Config (MongoDB URI, DB name)
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Python aur pip check karo
```bash
python --version    # Python 3.8+ hona chahiye
pip --version
```

### 2. Dependencies install karo
```bash
pip install -r requirements.txt
```

### 3. MongoDB check karo
MongoDB already installed hai. Service start karo:
```bash
# Windows
net start MongoDB

# macOS/Linux
sudo systemctl start mongod
# ya
brew services start mongodb-community
```

### 4. .env file configure karo
`.env` file mein apni settings daalo (by default localhost use hoga):
```
MONGO_URI=mongodb://localhost:27017
DB_NAME=cricket_db
```

### 5. Chrome browser install karo
Selenium Chrome browser use karta hai. Chrome install hona chahiye.  
ChromeDriver automatically download ho jaata hai `webdriver-manager` se.

---

## ▶️ Kaise Run Karein

### Option 1 — Sirf ek baar run karo (testing ke liye)
```bash
python main.py
# ya
python main.py once
```
Yeh kya karta hai:
- CREX se saare upcoming/live matches fetch karta hai
- Har match ka Match Info aur Squads save karta hai

### Option 2 — Sirf live scores track karo
```bash
python main.py live
```
Yeh har **5 minute** mein live matches ka score update karta hai.  
Rokne ke liye `Ctrl+C` dabao.

### Option 3 — Fully automated (production ke liye)
```bash
python main.py schedule
```
Yeh karta hai:
- Match list: har **6 ghante** mein update
- Live scores: har **5 minute** mein update

---

## 🗄️ MongoDB Collections

Scrape kiya hua data `cricket_db` database mein store hota hai:

| Collection    | Data                              |
|---------------|-----------------------------------|
| `matches`     | Match list (title, date, teams)   |
| `match_info`  | Toss, umpires, venue, match type  |
| `squads`      | Dono teams ke players             |
| `scorecard`   | Batting aur bowling stats         |
| `live_scores` | Current score, batsmen, bowler    |

### MongoDB mein data dekhne ke liye:
```bash
mongosh
use cricket_db
db.matches.find().pretty()
db.live_scores.find().pretty()
```

---

## 🔍 Data Flow

```
CREX Schedule Page
       |
       v
match_list_scraper.py  -->  MongoDB: matches
       |
       v (har match URL ke liye)
match_detail_scraper.py --> MongoDB: match_info, squads
       |
       v (match live hone par)
live_scraper.py         --> MongoDB: live_scores, scorecard
```

---

## ❗ Troubleshooting

**ChromeDriver error?**
```bash
pip install --upgrade webdriver-manager
```

**MongoDB connection fail?**
- Check karo MongoDB service chal rahi hai ya nahi
- `.env` mein `MONGO_URI` sahi hai ya nahi

**Website se data nahi aa raha?**
- CREX ka HTML structure kabhi kabhi change hota hai
- Selectors ko browser DevTools se verify karo (F12 → Inspect)
- `time.sleep()` values badha sakte ho agar page slow hai

---

## 📦 Tech Stack

- **Python 3.8+**
- **Selenium** — Browser automation (JavaScript-heavy pages ke liye)
- **BeautifulSoup4** — HTML parsing
- **PyMongo** — MongoDB Python driver
- **schedule** — Simple task scheduling
- **webdriver-manager** — ChromeDriver auto-download
