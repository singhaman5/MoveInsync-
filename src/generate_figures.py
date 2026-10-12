"""
MoveInSync Visual Chart Generator
Generates publication-quality charts for the PDF report and presentation.
"""

import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Set aesthetic style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, sans-serif'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8

PRIMARY_COLOR = '#0F172A'
ACCENT_BLUE = '#2563EB'
ACCENT_RED = '#EF4444'
ACCENT_AMBER = '#F59E0B'
ACCENT_GREEN = '#10B981'

def generate_charts():
    os.makedirs("figures", exist_ok=True)
    df = pd.read_csv("data/classified_reviews.csv")
    cat_summary = pd.read_csv("data/category_summary.csv")

    # 1. Rating Distribution Chart
    fig, ax = plt.subplots(figsize=(7, 4), dpi=300)
    rating_counts = df["star_rating"].value_counts().sort_index()
    colors = [ACCENT_RED, '#F87171', ACCENT_AMBER, '#34D399', ACCENT_GREEN]
    bars = ax.bar(rating_counts.index, rating_counts.values, color=colors, width=0.55, edgecolor='#334155', linewidth=0.5)
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 15, f'{int(yval)}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1E293B')

    ax.set_title("Play Store Sample Rating Distribution (N = 1,778)", fontsize=13, fontweight='bold', pad=15, color=PRIMARY_COLOR)
    ax.set_xlabel("Star Rating", fontsize=11, fontweight='bold', color='#334155')
    ax.set_ylabel("Number of Reviews", fontsize=11, fontweight='bold', color='#334155')
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(['1 Star (39.0%)', '2 Star (6.2%)', '3 Star (5.5%)', '4 Star (7.5%)', '5 Star (41.8%)'])
    ax.set_ylim(0, max(rating_counts.values) * 1.15)
    plt.tight_layout()
    fig.savefig("figures/rating_distribution.png", dpi=300)
    plt.close()

    # 2. Top Complaint Categories Chart (1 & 2 stars)
    neg_cats = cat_summary[cat_summary["issue_category"] != "General / Unclassified"].sort_values(by="neg_reviews", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    bars = ax.barh(neg_cats["issue_category"], neg_cats["neg_reviews"], color='#DC2626', height=0.6, edgecolor='#7F1D1D', linewidth=0.5)

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 3, bar.get_y() + bar.get_height()/2.0, f'{int(width)} ({width/neg_cats["neg_reviews"].sum()*100:.1f}%)', 
                ha='left', va='center', fontsize=9, fontweight='bold', color='#1E293B')

    ax.set_title("Root-Cause Breakdown: Negative Reviews (1 & 2 Stars)", fontsize=13, fontweight='bold', pad=15, color=PRIMARY_COLOR)
    ax.set_xlabel("Volume of Negative Reviews", fontsize=11, fontweight='bold', color='#334155')
    ax.set_xlim(0, max(neg_cats["neg_reviews"]) * 1.25)
    plt.tight_layout()
    fig.savefig("figures/complaint_categories.png", dpi=300)
    plt.close()

    # 3. Customer Journey Pain Point Breakdown
    journey_summary = pd.read_csv("data/journey_summary.csv")
    journey_filtered = journey_summary[journey_summary["journey_stage"] != "General / App Lifecycle"]
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    bars = ax.bar(journey_filtered["journey_stage"], journey_filtered["neg_reviews"], color=ACCENT_BLUE, width=0.5, edgecolor='#1E3A8A', linewidth=0.5)

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 5, f'{int(yval)}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1E293B')

    ax.set_title("Negative Experience Volume Across Employee Journey Stages", fontsize=12, fontweight='bold', pad=15, color=PRIMARY_COLOR)
    ax.set_ylabel("Negative Reviews", fontsize=10, fontweight='bold', color='#334155')
    plt.xticks(rotation=15, ha='right', fontsize=9)
    ax.set_ylim(0, max(journey_filtered["neg_reviews"]) * 1.15)
    plt.tight_layout()
    fig.savefig("figures/journey_stages.png", dpi=300)
    plt.close()

    print("All chart figures generated in figures/")

if __name__ == "__main__":
    generate_charts()
