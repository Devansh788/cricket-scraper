# database.py
# MongoDB se connect karne ka code

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# .env file se variables load karo
load_dotenv()


def get_database():
    """
    MongoDB se connection banata hai aur database return karta hai.
    """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "cricket_db")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    return db


# Global database object — isko import karke use karo
db = get_database()

# Collections (MongoDB mein tables ki jagah collections hote hain)
matches_col = db["matches"]           # Match list
match_info_col = db["match_info"]     # Match Info tab
squads_col = db["squads"]            # Squads tab
scorecard_col = db["scorecard"]      # Scorecard tab
live_score_col = db["live_scores"]   # Live tab


def save_or_update(collection, filter_query, data):
    """
    Agar document pehle se hai to update karo, warna naya insert karo.
    (Yeh MongoDB ka upsert feature use karta hai)
    """
    collection.update_one(
        filter_query,
        {"$set": data},
        upsert=True   # Agar nahi mila to naya bana do
    )
    print(f"  Saved to '{collection.name}' collection.")
