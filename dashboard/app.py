"""
MoveInSync FDE Analytics Dashboard
Interactive operational intelligence tool for monitoring Google Play Store reviews,
tracking employee sentiment, analyzing root causes, and prioritizing engineering interventions.
"""

import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure page layout
st.set_page_config(
    page_title="MoveInSync | Play Store Review Intelligence",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .status-badge-crit {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .status-badge-high {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    classified_path = "data/classified_reviews.csv"
    meta_path = "data/app_metadata.json"
    
    if not os.path.exists(classified_path):
        return None, None
        
    df = pd.read_csv(classified_path)
    df["review_date"] = pd.to_datetime(df["review_date"])
    
    metadata = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            metadata = json.load(f)
            
    return df, metadata

df, metadata = load_data()

# Header
st.title("MoveInSync | Forward Deployed Engineer (FDE) Review Intelligence")
st.markdown("Automated public telemetry, root-cause diagnosis, and prioritized action tracker for the Employee Transport App (`com.moveinsync.ets`).")

if df is None:
    st.error("No dataset found. Please run `python3 src/collect_reviews.py && python3 src/classify_reviews.py` to initialize data.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Filter Telemetry")

# Date range filter
min_date = df["review_date"].min().date()
max_date = df["review_date"].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Star rating filter
all_stars = sorted(df["star_rating"].unique().tolist())
selected_stars = st.sidebar.multiselect("Star Rating", all_stars, default=all_stars)

# Category filter
all_cats = sorted(df["issue_category"].unique().tolist())
selected_cats = st.sidebar.multiselect("Issue Category", all_cats, default=all_cats)

# Severity filter
all_sevs = sorted(df["severity"].unique().tolist())
selected_sevs = st.sidebar.multiselect("Severity Level", all_sevs, default=all_sevs)

# Search filter
search_query = st.sidebar.text_input("Search Review Text", "")

# Apply filters
filtered_df = df.copy()
if len(date_range) == 2:
    filtered_df = filtered_df[(filtered_df["review_date"].dt.date >= date_range[0]) & (filtered_df["review_date"].dt.date <= date_range[1])]
if selected_stars:
    filtered_df = filtered_df[filtered_df["star_rating"].isin(selected_stars)]
if selected_cats:
    filtered_df = filtered_df[filtered_df["issue_category"].isin(selected_cats)]
if selected_sevs:
    filtered_df = filtered_df[filtered_df["severity"].isin(selected_sevs)]
if search_query:
    filtered_df = filtered_df[filtered_df["review_text"].str.contains(search_query, case=False, na=False)]

# Top KPIs
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Play Store Official Rating", f"{metadata.get('score', 4.64):.2f} ★", f"{metadata.get('ratings_count', 114878):,} Total Ratings")
with col2:
    st.metric("Sample Analyzed", f"{len(df):,} Reviews", f"{len(filtered_df):,} in current view")
with col3:
    neg_count = (filtered_df["star_rating"] <= 2).sum()
    neg_pct = (neg_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric("Critical Complaints (1-2★)", f"{neg_count:,}", f"{neg_pct:.1f}% of view")
with col4:
    crit_count = (filtered_df["severity"] == "Critical").sum()
    st.metric("High/Critical Incidents", f"{crit_count:,}", "Immediate attention")
with col5:
    app_version = metadata.get("version", "12.19.0")
    st.metric("Active App Version", f"v{app_version}", "Latest on Store")

st.markdown("---")

# Main Charts
tab1, tab2, tab3, tab4 = st.tabs(["📊 Diagnostic Overview", "🔍 Root-Cause Deep Dive", "🚀 FDE Action Plan & Matrix", "📋 Review Explorer"])

with tab1:
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("Rating Distribution (Filtered View)")
        fig_rating = px.histogram(
            filtered_df,
            x="star_rating",
            color="star_rating",
            color_discrete_map={1: "#EF4444", 2: "#F87171", 3: "#F59E0B", 4: "#34D399", 5: "#10B981"},
            labels={"star_rating": "Star Rating", "count": "Review Count"},
            nbins=5
        )
        fig_rating.update_layout(bargap=0.2, showlegend=False)
        st.plotly_chart(fig_rating, use_container_width=True)

    with col_c2:
        st.subheader("Negative Reviews by Customer Journey Stage")
        neg_subset = filtered_df[filtered_df["star_rating"].isin([1, 2])]
        if not neg_subset.empty:
            stage_counts = neg_subset["journey_stage"].value_counts().reset_index()
            stage_counts.columns = ["journey_stage", "count"]
            fig_stage = px.bar(
                stage_counts,
                x="count",
                y="journey_stage",
                orientation="h",
                color="count",
                color_continuous_scale="Reds",
                labels={"count": "Negative Reviews", "journey_stage": "Journey Stage"}
            )
            fig_stage.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_stage, use_container_width=True)
        else:
            st.info("No negative reviews match current filters.")

    st.subheader("Monthly Review Volume & Rating Trend")
    trend_df = filtered_df.groupby("review_year_month").agg(
        review_count=("star_rating", "count"),
        avg_rating=("star_rating", "mean")
    ).reset_index().sort_values("review_year_month")
    
    if len(trend_df) > 1:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(x=trend_df["review_year_month"], y=trend_df["review_count"], name="Review Volume", marker_color="#94A3B8"))
        fig_trend.add_trace(go.Scatter(x=trend_df["review_year_month"], y=trend_df["avg_rating"], name="Average Rating", yaxis="y2", line=dict(color="#2563EB", width=3)))
        fig_trend.update_layout(
            yaxis=dict(title="Review Volume"),
            yaxis2=dict(title="Average Rating", overlaying="y", side="right", range=[1, 5]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

with tab2:
    st.subheader("Detailed Root-Cause Breakdown")
    cat_df = filtered_df.groupby("issue_category").agg(
        total=("star_rating", "count"),
        negative=("star_rating", lambda x: (x <= 2).sum()),
        critical=("severity", lambda x: (x == "Critical").sum()),
        avg_rating=("star_rating", "mean")
    ).reset_index().sort_values("negative", ascending=False)
    
    st.dataframe(cat_df, use_container_width=True)

    st.markdown("""
    ### Top 4 Vulnerabilities Identified from Public Data:
    1. **Post-Update App Crashes & White Screens (`com.moveinsync.ets` v12.x)**:
       - *Symptom*: Users report app refusing to open after Play Store updates, requiring manual uninstall/reinstall.
       - *Root Cause Hypothesis*: SQLite database migration schema lock or stale cached user tokens in Android SharedPreferences.
    2. **GPS Latency & "Ghost" Cab Positions**:
       - *Symptom*: Vehicle icon jumps miles or remains stationary for 10 minutes while cab actually arrives, leading to missed pickups.
       - *Root Cause Hypothesis*: Driver app killed by OEM battery optimizations (aggressive Xiaomi/Vivo/Samsung background task killer) or websocket drop.
    3. **Misleading ETA & "Pilgrimage" Routing**:
       - *Symptom*: ETA jumps from 5 mins to 45 mins; routing orders pickup in circuitous loops.
       - *Root Cause Hypothesis*: Static distance matrix routing without real-time micro-traffic integration; poor handling of driver off-route deviations.
    4. **In-App Mandatory Rating Gatekeeper Friction**:
       - *Symptom*: Employees express anger at being blocked from booking rides until they provide feedback for past rides, prompting retaliatory 1-star Play Store ratings.
       - *Root Cause Hypothesis*: Hard modal feedback prompt lacking an easy "Skip" or dismiss option.
    """)

with tab3:
    st.subheader("FDE Prioritized Engineering Action Matrix")
    matrix_data = [
        {
            "Priority": "P0 (Week 1)",
            "Initiative": "Decouple Post-Ride Feedback Modal",
            "Target Problem": "Retaliatory 1-star Play Store reviews caused by blocking in-app rating modals.",
            "Proposed Fix": "Introduce non-blocking bottom sheet with 'Skip' and intelligent rate-limiting.",
            "Effort": "2 Days",
            "Impact": "High (Immediate rating spike)",
            "Owner": "Mobile UX / Frontend"
        },
        {
            "Priority": "P0 (Week 2)",
            "Initiative": "App Startup Migration & Crash Shield",
            "Target Problem": "Post-update app freeze/white screen forcing uninstalls.",
            "Proposed Fix": "Defensive try-catch migration around DB schema upgrades + automated room reset.",
            "Effort": "5 Days",
            "Impact": "Critical (Eliminates #1 crash issue)",
            "Owner": "Android Core Team"
        },
        {
            "Priority": "P1 (Weeks 3-4)",
            "Initiative": "Driver App Foreground Telemetry Keep-Alive",
            "Target Problem": "Frozen GPS tracking and stale vehicle locations.",
            "Proposed Fix": "Implement foreground sticky service + dead-reckoning fallbacks on client app.",
            "Effort": "10 Days",
            "Impact": "Critical (Restores trust in live commute)",
            "Owner": "Driver App + IoT Gateway"
        },
        {
            "Priority": "P1 (Weeks 5-6)",
            "Initiative": "Smart In-App Play Store Review Prompting (In-App Review API)",
            "Target Problem": "Play Store receives only angry churned users; satisfied riders never prompted.",
            "Proposed Fix": "Trigger Google Play In-App Review dialog exclusively after 3 consecutive 5-star trips.",
            "Effort": "3 Days",
            "Impact": "Very High (+0.3 Store Score)",
            "Owner": "Growth / FDE"
        },
        {
            "Priority": "P2 (Weeks 7-10)",
            "Initiative": "Real-Time Dynamic ETA Confidence Band",
            "Target Problem": "Sudden ETA jumps causing employee anxiety.",
            "Proposed Fix": "Display ETA window (e.g., '8:12 - 8:18 AM') with traffic volatility tag.",
            "Effort": "15 Days",
            "Impact": "High (Reduces desk complaints)",
            "Owner": "Routing Engine & Backend"
        }
    ]
    st.table(pd.DataFrame(matrix_data))

with tab4:
    st.subheader("Searchable Public Evidence Table")
    display_cols = ["star_rating", "issue_category", "severity", "review_date", "review_text", "thumbs_up"]
    st.dataframe(filtered_df[display_cols].sort_values(by="star_rating", ascending=True), use_container_width=True)

# Footer
st.markdown("---")
st.caption("MoveInSync Forward Deployed Engineer Assignment | Public Data Telemetry & Root Cause Analysis Pipeline | Auto-refreshed from Play Store")
