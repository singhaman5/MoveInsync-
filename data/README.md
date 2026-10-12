# MoveInSync Data Directory

This directory stores the primary data assets for the MoveInSync Google Play Store review intelligence system.

## Files Description

1. **`app_metadata.json`**: Current official metadata snapshot directly retrieved from the Google Play Store for `com.moveinsync.ets`. Contains total ratings count, cumulative score, latest version, and star histogram.
2. **`raw_reviews.csv`**: Unfiltered public reviews collected from Google Play Store balancing `NEWEST` and `MOST_RELEVANT` vectors.
3. **`cleaned_reviews.csv`**: Normalized review text, deduplicated by `review_id`, cleaned of formatting anomalies, and enriched with temporal attributes (`review_year`, `review_year_month`).
4. **`classified_reviews.csv`**: Primary analytical dataset categorized into 10 domain-specific transport stages, with deterministic sentiment (`Positive`, `Neutral`, `Negative`), severity (`Low`, `Medium`, `High`, `Critical`), and customer journey mapping.
5. **`category_summary.csv`**: Aggregated issue distribution across categories with complaint volumes, average star ratings, and negative review percentages.
6. **`journey_summary.csv`**: Pain-point distribution mapped to employee journey stages (Roster & Booking, Pre-Trip Tracking & ETA, Boarding & Driver Coordination, Transit & Route Experience, Post-Trip & Support/Feedback).
7. **`monthly_trends.csv`**: Longitudinal monthly breakdown of review volume and rating trajectory.
8. **`analysis_summary.json`**: Key statistical highlights consumed by report generators and dashboards.

All datasets are automatically reproducible by running:
```bash
python3 src/collect_reviews.py
python3 src/clean_reviews.py
python3 src/classify_reviews.py
python3 src/analyze_reviews.py
```
