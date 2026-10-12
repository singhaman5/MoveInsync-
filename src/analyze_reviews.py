"""
MoveInSync Review Analytics & Summary Engine
Computes comprehensive statistical aggregates, ratings breakdowns, category distributions,
time-series trends, and exports structured CSVs and charts for the report and dashboard.
"""

import os
import json
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def analyze_reviews(input_path="data/classified_reviews.csv", output_dir="data"):
    logging.info(f"Loading classified dataset from {input_path}...")
    df = pd.read_csv(input_path)

    total_reviews = len(df)
    avg_rating = df["star_rating"].mean()
    rating_counts = df["star_rating"].value_counts().sort_index().to_dict()
    
    # 1. Category Breakdown
    cat_summary = df.groupby("issue_category").agg(
        total_reviews=("star_rating", "count"),
        avg_rating=("star_rating", "mean"),
        neg_reviews=("star_rating", lambda s: (s <= 2).sum()),
        pos_reviews=("star_rating", lambda s: (s >= 4).sum()),
        critical_count=("severity", lambda s: (s == "Critical").sum())
    ).reset_index()

    cat_summary["neg_percentage"] = (cat_summary["neg_reviews"] / cat_summary["total_reviews"] * 100).round(1)
    cat_summary = cat_summary.sort_values(by="neg_reviews", ascending=False)
    cat_summary.to_csv(os.path.join(output_dir, "category_summary.csv"), index=False)

    # 2. Journey Stage Breakdown
    journey_summary = df.groupby("journey_stage").agg(
        total_reviews=("star_rating", "count"),
        avg_rating=("star_rating", "mean"),
        neg_reviews=("star_rating", lambda s: (s <= 2).sum()),
        critical_count=("severity", lambda s: (s == "Critical").sum())
    ).reset_index().sort_values(by="neg_reviews", ascending=False)
    journey_summary.to_csv(os.path.join(output_dir, "journey_summary.csv"), index=False)

    # 3. Monthly Trends
    if "review_year_month" in df.columns:
        monthly_trends = df.groupby(["review_year_month"]).agg(
            review_count=("star_rating", "count"),
            avg_rating=("star_rating", "mean"),
            neg_count=("star_rating", lambda s: (s <= 2).sum()),
            pos_count=("star_rating", lambda s: (s >= 4).sum())
        ).reset_index()
        monthly_trends = monthly_trends.sort_values("review_year_month")
        monthly_trends.to_csv(os.path.join(output_dir, "monthly_trends.csv"), index=False)

    # 4. Overall Metrics Summary Dict
    metrics = {
        "total_sample_reviews": total_reviews,
        "sample_average_rating": round(avg_rating, 2),
        "total_negative_reviews": int((df["star_rating"] <= 2).sum()),
        "total_positive_reviews": int((df["star_rating"] >= 4).sum()),
        "negative_percentage": round((df["star_rating"] <= 2).sum() / total_reviews * 100, 2),
        "rating_distribution": rating_counts,
        "top_complaint_categories": cat_summary[cat_summary["issue_category"] != "General / Unclassified"].head(5)[["issue_category", "neg_reviews", "neg_percentage"]].to_dict(orient="records"),
        "date_min": str(df["review_date"].min()),
        "date_max": str(df["review_date"].max())
    }

    with open(os.path.join(output_dir, "analysis_summary.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    logging.info("Analysis summaries generated successfully.")
    return metrics

if __name__ == "__main__":
    analyze_reviews()
