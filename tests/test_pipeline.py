"""
Test suite for MoveInSync Review Analytics Pipeline
Tests data cleaning, classification heuristics, sentiment mapping, and aggregation.
"""

import os
import pytest
import pandas as pd
from src.clean_reviews import clean_text
from src.classify_reviews import classify_text, assign_sentiment, assign_severity, map_journey_stage
from src.analyze_reviews import analyze_reviews

def test_clean_text():
    raw = "   Worst app    ever   \n\n crash on open "
    cleaned = clean_text(raw)
    assert cleaned == "Worst app ever crash on open"

def test_classify_text_gps():
    cat, conf = classify_text("The GPS is totally wrong, live tracking is not moving at all on the map")
    assert cat == "GPS Accuracy & Live Tracking"
    assert conf > 0.5

def test_classify_text_crash():
    cat, conf = classify_text("App keeps crashing after new update, not opening showing white screen")
    assert cat == "App Stability, Crashes & Login"
    assert conf > 0.5

def test_classify_text_booking():
    cat, conf = classify_text("Unable to book my roster seat for weekend shift, cutoff time error")
    assert cat == "Booking & Schedule Management"
    assert conf > 0.5

def test_assign_sentiment():
    assert assign_sentiment(1, "worst ever") == "Negative"
    assert assign_sentiment(5, "awesome experience") == "Positive"
    assert assign_sentiment(5, "worst pathetic app") == "Negative"  # detects mismatch/sarcasm

def test_assign_severity():
    assert assign_severity(1, "Negative", "App Stability, Crashes & Login") == "Critical"
    assert assign_severity(5, "Positive", "General / Unclassified") == "Low"

def test_map_journey_stage():
    assert map_journey_stage("GPS Accuracy & Live Tracking") == "Pre-Trip Tracking & ETA"
    assert map_journey_stage("Booking & Schedule Management") == "Roster & Booking"
    assert map_journey_stage("App Stability, Crashes & Login") == "Platform Core / App Layer"

def test_pipeline_integration():
    # Verify classified data file exists and contains expected columns
    classified_file = "data/classified_reviews.csv"
    assert os.path.exists(classified_file)
    df = pd.read_csv(classified_file)
    assert len(df) > 0
    expected_cols = ["review_id", "star_rating", "review_text", "issue_category", "sentiment", "severity", "journey_stage"]
    for col in expected_cols:
        assert col in df.columns
