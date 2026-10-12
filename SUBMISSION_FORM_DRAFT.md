# MoveInSync FDE Candidate Assignment — Submission Form Draft

This document contains pre-drafted responses for the official MoveInSync submission form / Google Form. Review and fill in your personal contact details, repository links, and Google Drive / presentation links before submitting.

---

### Field 1: Candidate Full Name
`[YOUR FULL NAME]` *(e.g., Aman Singh)*

### Field 2: Registration / Application ID
`[YOUR REGISTRATION / APPLICATION ID]` *(if applicable, or enter N/A)*

### Field 3: Email Address
`[YOUR EMAIL ADDRESS]`

### Field 4: Contact Number
`[YOUR PHONE NUMBER]`

### Field 5: LinkedIn Profile URL
`[YOUR LINKEDIN URL]` *(e.g., https://www.linkedin.com/in/yourprofile)*

### Field 6: Latest CV / Resume Link
`[LINK TO YOUR CV / RESUME ON GOOGLE DRIVE]` *(Ensure access is set to "Anyone with the link can view")*

---

### Field 7: Primary Submission Link (GitHub Repository)
`[LINK TO YOUR GITHUB REPOSITORY]` *(e.g., https://github.com/yourusername/moveinsync-fde-case-study)*

*(Note: Follow the instructions in `README.md` to push the local Git repository to your personal GitHub account).*

---

### Field 8: Supporting Links (Presentation / Case Study PDF / Live Dashboard)
- **Case Study PDF Report (Google Drive Link)**: `[UPLOAD reports/case_study.pdf TO GOOGLE DRIVE AND PASTE LINK HERE]`
- **Slide Deck Presentation (Google Drive / Canva Link)**: `[UPLOAD reports/presentation.pptx TO GOOGLE DRIVE AND PASTE LINK HERE]`
- **Interactive Review Dashboard (Streamlit Cloud URL, Optional)**: `[DEPLOYED URL IF HOSTED ON STREAMLIT CLOUD]`

---

### Field 9: Methodology & Tools Note
*(Copy and paste the exact text below into the Google Form's text response box)*

```text
To diagnose MoveInSync's Play Store rating landscape, I developed an end-to-end Forward Deployed Engineering (FDE) telemetry and root-cause analysis pipeline using public Google Play Store data for com.moveinsync.ets.

1. Research & Data Mining:
Using an automated Python scraper (google-play-scraper), I extracted 1,778 unique, deduplicated public Play Store reviews balancing NEWEST and MOST_RELEVANT sort vectors across recent app releases (v12.x).

2. Data Processing & Taxonomy:
I cleaned and normalized the data using Pandas, engineering a deterministic NLP classification engine mapped to 10 transport lifecycle categories (App Stability, GPS Tracking, ETA & Delays, Booking & Roster, Driver Behavior, Route Optimization, OTP/Boarding, Notifications, UX Friction, and Support Desk). Sentiment and severity were calculated based on star rating, symptom keywords, and commute failure severity.

3. Key Root-Cause Findings (from 804 negative reviews):
- App Stability & Post-Update Crashes (24.3%): Release updates trigger white-screen startup hangs, likely caused by SQLite schema migration locks.
- GPS Latency & Ghost Cabs (16.5%): Vehicle icons freezing due to aggressive OEM background battery killers stalling driver app telemetry.
- In-App Rating Gatekeeper Friction: Intrusive post-ride feedback modals blocking self-booking, causing commuters to vent with retaliatory 1-star Play Store reviews.
- ETA Volatility (11.0%): Inaccurate arrival estimates causing missed cab boarding.

4. Engineering Roadmap (ICE Prioritized):
- P0: Decouple post-ride feedback modals with a non-blocking 'Skip' bottom sheet; implement defensive try-catch database migrations; trigger Google Play In-App Review API for verified 3-trip 5-star commuters.
- P1: Implement Android Foreground Sticky Service on driver devices to bypass OEM battery killing; introduce client-side dead-reckoning animation; display dynamic ETA confidence intervals (e.g., '8:15–8:22 AM').

5. Repeatable Tooling & Validation:
Built an interactive Streamlit & Plotly analytics dashboard for recurring leadership inquiries, wrote a Pytest suite (100% passing), and compiled an executive PDF case study and a 10-slide PowerPoint presentation. All tools are reproducible and ready for immediate engineering execution.
```

---

### Field 10: Confirmation of Public Access Permissions
- [x] **I confirm that all uploaded Google Drive links, presentation decks, PDF reports, and GitHub repositories have permissions set to "Anyone with the link can view".**
