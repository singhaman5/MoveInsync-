"""
MoveInSync Review Collector
Fetches real, publicly available Google Play Store reviews for com.moveinsync.ets
using the official public Google Play Scraper.
Supports sorting by NEWEST and MOST_RELEVANT to collect both recent trends and high-impact complaints.
"""

import os
import sys
import json
import logging
from datetime import datetime
from google_play_scraper import app, reviews, Sort
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

APP_ID = "com.moveinsync.ets"
APP_NAME = "MoveInSync"
COUNTRY = "in"
LANG = "en"

def fetch_app_metadata(app_id=APP_ID):
    logging.info(f"Fetching app metadata for {app_id}...")
    try:
        app_info = app(app_id, lang=LANG, country=COUNTRY)
        metadata = {
            "title": app_info.get("title"),
            "score": app_info.get("score"),
            "ratings_count": app_info.get("ratings"),
            "reviews_count": app_info.get("reviews"),
            "histogram": app_info.get("histogram"),
            "version": app_info.get("version"),
            "updated": str(app_info.get("updated")),
            "url": f"https://play.google.com/store/apps/details?id={app_id}&hl={LANG}&gl={COUNTRY}",
            "collected_at": datetime.now().isoformat()
        }
        logging.info(f"App Metadata retrieved: Score={metadata['score']:.2f}, Total Ratings={metadata['ratings_count']}")
        return metadata
    except Exception as e:
        logging.error(f"Failed to fetch app metadata: {e}")
        return None

def fetch_reviews(app_id=APP_ID, total_target=2000):
    """
    Fetches reviews balancing NEWEST and MOST_RELEVANT.
    """
    logging.info(f"Initiating review collection for {app_id} (Target: ~{total_target} reviews)...")
    collected_reviews = []
    seen_ids = set()

    for sort_strategy, name in [(Sort.NEWEST, "NEWEST"), (Sort.MOST_RELEVANT, "MOST_RELEVANT")]:
        logging.info(f"Fetching reviews with sort strategy: {name}...")
        batch_count = min(1000, total_target // 2)
        try:
            results, continuation_token = reviews(
                app_id,
                lang=LANG,
                country=COUNTRY,
                sort=sort_strategy,
                count=batch_count
            )
            logging.info(f"Retrieved {len(results)} reviews via {name}")
            for r in results:
                rev_id = r.get("reviewId")
                if rev_id and rev_id not in seen_ids:
                    seen_ids.add(rev_id)
                    collected_reviews.append({
                        "review_id": rev_id,
                        "app_name": APP_NAME,
                        "review_date": r.get("at").isoformat() if r.get("at") else None,
                        "star_rating": r.get("score"),
                        "review_text": r.get("content", "").strip(),
                        "thumbs_up": r.get("thumbsUpCount", 0),
                        "review_created_version": r.get("reviewCreatedVersion", "unknown"),
                        "reply_content": r.get("replyContent"),
                        "replied_at": r.get("repliedAt").isoformat() if r.get("repliedAt") else None,
                        "source_url": f"https://play.google.com/store/apps/details?id={app_id}",
                        "collection_date": datetime.now().strftime("%Y-%m-%d"),
                        "evidence_type": "Verified Public Play Store Review"
                    })
        except Exception as e:
            logging.error(f"Error fetching reviews for {name}: {e}")

    logging.info(f"Total unique reviews collected: {len(collected_reviews)}")
    return collected_reviews

def main():
    metadata = fetch_app_metadata(APP_ID)
    if metadata:
        meta_path = os.path.join("data", "app_metadata.json")
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
        logging.info(f"Saved metadata to {meta_path}")

    raw_reviews = fetch_reviews(APP_ID, total_target=2500)
    if raw_reviews:
        df = pd.DataFrame(raw_reviews)
        raw_csv_path = os.path.join("data", "raw_reviews.csv")
        df.to_csv(raw_csv_path, index=False)
        logging.info(f"Successfully exported {len(df)} raw reviews to {raw_csv_path}")

if __name__ == "__main__":
    main()
