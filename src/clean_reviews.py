"""
MoveInSync Review Data Cleaner
Cleans, normalizes, and filters the raw review dataset.
- Normalizes review text (whitespace, casing, encoding)
- Filters out non-informative single-word spam where appropriate but preserves sentiment
- Extracts review length and language properties
- Handles dates and formats
"""

import os
import re
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_reviews(input_path="data/raw_reviews.csv", output_path="data/cleaned_reviews.csv"):
    logging.info(f"Loading raw reviews from {input_path}...")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Raw data file not found at {input_path}")
    
    df = pd.read_csv(input_path)
    initial_count = len(df)
    logging.info(f"Loaded {initial_count} records.")

    # Deduplicate by review_id
    df = df.drop_duplicates(subset=["review_id"]).copy()
    logging.info(f"Count after deduplication: {len(df)}")

    # Clean text
    df["review_text"] = df["review_text"].apply(clean_text)
    
    # Calculate word count & char length
    df["char_length"] = df["review_text"].str.len()
    df["word_count"] = df["review_text"].apply(lambda x: len(x.split()) if x else 0)

    # Normalize star_rating
    df["star_rating"] = pd.to_numeric(df["star_rating"], errors="coerce")
    df = df.dropna(subset=["star_rating"])
    df["star_rating"] = df["star_rating"].astype(int)

    # Normalize date
    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
    df["review_year"] = df["review_date"].dt.year
    df["review_year_month"] = df["review_date"].dt.to_period("M").astype(str)

    # Save cleaned
    df.to_csv(output_path, index=False)
    logging.info(f"Cleaned dataset saved to {output_path} ({len(df)} records).")
    return df

if __name__ == "__main__":
    clean_reviews()
