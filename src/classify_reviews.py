"""
MoveInSync Review Classifier (Enhanced)
Classifies reviews into domain-specific operational and product categories,
determines sentiment, severity, and customer journey stage.
Uses an explainable, deterministic rule-based NLP matcher with keyword scoring.
"""

import os
import re
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Taxonomy definition
CATEGORY_RULES = {
    "GPS Accuracy & Live Tracking": {
        "keywords": [
            r"\bgps\b", r"\btrack", r"\blocation\b", r"\blive track", r"\bmap\b", r"\bpin\b",
            r"\bwrong location\b", r"\bnot moving\b", r"\bvehicle location\b", r"\baccuracy\b",
            r"\bmapping\b", r"\blive status\b"
        ],
        "weight": 1.2
    },
    "ETA Accuracy & Delays": {
        "keywords": [
            r"\beta\b", r"\bdelay", r"\blate\b", r"\btime\b", r"\btiming\b", r"\bwaiting\b",
            r"\bwaited\b", r"\bhours\b", r"\breach late\b", r"\bnever on time\b", r"\bschedule\b",
            r"\bpilgrimage\b"
        ],
        "weight": 1.0
    },
    "App Stability, Crashes & Login": {
        "keywords": [
            r"\bcrash", r"\bhang", r"\bfreeze", r"\bblack screen\b", r"\bwhite screen\b",
            r"\blogin\b", r"\bsign in\b", r"\botp\b", r"\bupdate\b", r"\binstall\b", r"\buninstall\b",
            r"\bnot opening\b", r"\bopen\b", r"\bglitch\b", r"\bbug\b", r"\bnetwork error\b",
            r"\bserver error\b", r"\bslow\b", r"\bload", r"\bversion\b", r"\bstopped working\b",
            r"\bnot working\b", r"\bapp error\b", r"\bloading issue\b", r"\berror\b"
        ],
        "weight": 1.1
    },
    "Booking & Schedule Management": {
        "keywords": [
            r"\bbook", r"\bbooking\b", r"\bcancel", r"\broster\b", r"\bshift\b", r"\bmodify\b",
            r"\bseat\b", r"\breschedule\b", r"\bslot\b", r"\bcut off\b", r"\bcutoff\b", r"\bweekend\b",
            r"\bapply\b", r"\brequest\b"
        ],
        "weight": 1.1
    },
    "Driver Behavior & Coordination": {
        "keywords": [
            r"\bdriver\b", r"\brude\b", r"\bcall\b", r"\bcalling\b", r"\bnot picking\b",
            r"\brash\b", r"\bdriving\b", r"\bspeed\b", r"\bbehavior\b", r"\bbehaviour\b",
            r"\barrogant\b", r"\babuse\b", r"\bcontact\b", r"\bnumber\b", r"\bdriver details\b"
        ],
        "weight": 1.1
    },
    "Route Optimization & Detours": {
        "keywords": [
            r"\broute\b", r"\bdetour\b", r"\blong route\b", r"\bcircuitous\b", r"\bround\b",
            r"\bfirst pickup\b", r"\blast drop\b", r"\bdropping\b", r"\bpickup point\b",
            r"\bdrop point\b", r"\bway\b", r"\bdirection\b", r"\btour\b"
        ],
        "weight": 1.1
    },
    "Boarding, OTP & Attendance/No-Show": {
        "keywords": [
            r"\botp\b", r"\bboard", r"\bno show\b", r"\bnoshow\b", r"\babsent\b",
            r"\bpenalty\b", r"\bcheck in\b", r"\bcheck-in\b", r"\bscan\b", r"\bqr\b",
            r"\bleft me\b", r"\bcab left\b"
        ],
        "weight": 1.0
    },
    "Support & Complaint Resolution": {
        "keywords": [
            r"\bsupport\b", r"\bhelpdesk\b", r"\btransport desk\b", r"\bticket\b",
            r"\bcomplaint\b", r"\bno response\b", r"\bcare\b", r"\bhelpline\b",
            r"\bescalat", r"\bexecutive\b", r"\badmin\b", r"\bfeedback\b",
            r"\btransport management\b", r"\bhelp\b"
        ],
        "weight": 1.0
    },
    "Notification & Alerting": {
        "keywords": [
            r"\bnotif", r"\balert\b", r"\bsms\b", r"\bmessage\b", r"\bno sound\b",
            r"\blate notification\b", r"\bnot receiving\b", r"\bpop up\b"
        ],
        "weight": 1.0
    },
    "Ratings Pop-up & UX Friction": {
        "keywords": [
            r"\bfeedback pop\b", r"\brate ride\b", r"\bforcing to rate\b", r"\brating after every\b",
            r"\bui\b", r"\bux\b", r"\binterface\b", r"\bconfusing\b", r"\bdark mode\b", r"\bforce\b"
        ],
        "weight": 1.0
    }
}

JOURNEY_STAGES = {
    "Roster & Booking": ["Booking & Schedule Management"],
    "Pre-Trip Tracking & ETA": ["GPS Accuracy & Live Tracking", "ETA Accuracy & Delays", "Notification & Alerting"],
    "Boarding & Driver Coordination": ["Driver Behavior & Coordination", "Boarding, OTP & Attendance/No-Show"],
    "Transit & Route Experience": ["Route Optimization & Detours"],
    "Post-Trip & Support/Feedback": ["Support & Complaint Resolution", "Ratings Pop-up & UX Friction"],
    "Platform Core / App Layer": ["App Stability, Crashes & Login"]
}

def classify_text(text):
    if not text or not isinstance(text, str):
        return ("General / Unclassified", 0.0)

    text_lower = text.lower()
    scores = {}

    for category, config in CATEGORY_RULES.items():
        score = 0
        for pattern in config["keywords"]:
            matches = len(re.findall(pattern, text_lower))
            score += matches * config["weight"]
        if score > 0:
            scores[category] = score

    if not scores:
        return ("General / Unclassified", 0.3)

    best_cat = max(scores, key=scores.get)
    confidence = min(1.0, round(scores[best_cat] / (scores[best_cat] + 1.0), 2))
    return (best_cat, confidence)

def assign_sentiment(rating, text):
    if rating <= 2:
        return "Negative"
    elif rating == 3:
        text_lower = str(text).lower()
        if any(w in text_lower for w in ["bad", "worst", "hate", "terrible", "useless", "waste", "poor", "issue", "problem"]):
            return "Negative"
        elif any(w in text_lower for w in ["good", "great", "best", "nice", "love", "awesome", "smooth"]):
            return "Positive"
        return "Neutral"
    else:
        text_lower = str(text).lower()
        if any(w in text_lower for w in ["worst", "pathetic", "waste", "hate", "terrible", "useless"]):
            return "Negative"
        return "Positive"

def assign_severity(rating, sentiment, category):
    if sentiment == "Positive":
        return "Low"
    
    if rating == 1:
        if category in ["App Stability, Crashes & Login", "GPS Accuracy & Live Tracking", "ETA Accuracy & Delays", "Boarding, OTP & Attendance/No-Show"]:
            return "Critical"
        return "High"
    elif rating == 2:
        return "High"
    elif rating == 3:
        return "Medium"
    else:
        return "Low"

def map_journey_stage(category):
    for stage, cats in JOURNEY_STAGES.items():
        if category in cats:
            return stage
    return "General / App Lifecycle"

def classify_dataset(input_path="data/cleaned_reviews.csv", output_path="data/classified_reviews.csv"):
    logging.info(f"Loading cleaned dataset from {input_path}...")
    df = pd.read_csv(input_path)

    cats = []
    confs = []
    for text in df["review_text"]:
        c, conf = classify_text(text)
        cats.append(c)
        confs.append(conf)

    df["issue_category"] = cats
    df["confidence"] = confs
    df["sentiment"] = [assign_sentiment(r, t) for r, t in zip(df["star_rating"], df["review_text"])]
    df["severity"] = [assign_severity(r, s, c) for r, s, c in zip(df["star_rating"], df["sentiment"], df["issue_category"])]
    df["journey_stage"] = df["issue_category"].apply(map_journey_stage)

    df.to_csv(output_path, index=False)
    logging.info(f"Classified dataset saved to {output_path} ({len(df)} records).")
    return df

if __name__ == "__main__":
    classify_dataset()
