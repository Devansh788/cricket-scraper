# main.py
# Yeh project ka main entry point hai — isse run karo

import sys
import time
import schedule

# Apne scrapers import karo
from scrapers.match_list_scraper import scrape_match_list
from scrapers.match_detail_scraper import scrape_match_detail
from scrapers.live_scraper import scrape_live_matches


def run_full_pipeline():
    """
    Step 1: Match list scrape karo
    Step 2: Har match ka detail (Match Info + Squads) scrape karo
    """
    print("\n🏏 Full pipeline shuru ho rahi hai...")

    # Step 1: Match list
    match_urls = scrape_match_list()

    # Step 2: Har match ka detail
    print(f"\n{len(match_urls)} matches ke details scrape ho rahe hain...")
    for url in match_urls:
        scrape_match_detail(url)
        time.sleep(2)  # Website par zyada load mat daalo

    print("\n✅ Full pipeline complete!")


def run_live_updates():
    """
    Sirf live matches ka score update karo.
    Yeh har 5 minute mein chalta hai.
    """
    scrape_live_matches()


def main():
    """
    Command line se control:
      python main.py           -> Ek baar full pipeline run karo
      python main.py live      -> Sirf live updates (5 min interval)
      python main.py schedule  -> Full pipeline + live updates dono schedule karo
    """

    mode = sys.argv[1] if len(sys.argv) > 1 else "once"

    if mode == "once":
        # Sirf ek baar run karo aur band ho jao
        run_full_pipeline()

    elif mode == "live":
        # Sirf live scores track karo
        print("Live mode: Har 5 minute mein live scores update honge.")
        print("Rokne ke liye Ctrl+C dabao.\n")
        run_live_updates()  # Pehle abhi run karo
        schedule.every(5).minutes.do(run_live_updates)

        while True:
            schedule.run_pending()
            time.sleep(30)

    elif mode == "schedule":
        # Full pipeline: match list subah ek baar, live updates har 5 min
        print("Scheduled mode:")
        print("  - Match list: Har 6 ghante mein")
        print("  - Live scores: Har 5 minute mein")
        print("Rokne ke liye Ctrl+C dabao.\n")

        run_full_pipeline()  # Abhi pehli baar run karo

        schedule.every(6).hours.do(run_full_pipeline)
        schedule.every(5).minutes.do(run_live_updates)

        while True:
            schedule.run_pending()
            time.sleep(30)

    else:
        print(f"Unknown mode: '{mode}'")
        print("Use: python main.py [once|live|schedule]")


if __name__ == "__main__":
    main()
