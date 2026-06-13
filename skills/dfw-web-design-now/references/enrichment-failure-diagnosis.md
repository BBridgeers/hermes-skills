# Enrichment Failure Diagnosis — enrich_waterfall.py (June 2026)

## Result
0/428 owner names found. All 428 flagged to SpiderFoot. This was not a "no data" result — it was a systemic failure of 4 separate access methods.

## Failure Mode 1: TX SOS Direct Requires Paid Login
`direct.sos.state.tx.us` is NOT openly scrapable. SOSDirect requires a paid account with MFA and charges $1 per search. Every call returned the login wall, not data. Zero names extracted.

## Failure Mode 2: TDLR Is a Bulk Dataset (We Were Scraping Wrong)
TDLR publishes the entire license database as a free bulk CSV on the Texas Open Data Portal (data.texas.gov), updated monthly. The script was hitting the search form per-row when it should have been downloading one file. The 428-row loop triggered bot detection and timed out.

## Failure Mode 3: BBB Bot Detection (2025-2026)
Plain `requests` + BeautifulSoup against BBB returns 200 status but serves a Cloudflare challenge page with no actual content. Every parse returned empty strings that looked like "no result."

## Failure Mode 4: These Are Sole Proprietors With No State Filings
The core truth the 0/428 result reveals: businesses with zero digital footprint are overwhelmingly sole proprietors who:
- Never filed an LLC (TX SOS has nothing)
- Don't need a state trade license (TDLR has nothing)
- Aren't BBB-listed (BBB has nothing)
- Filed a county DBA but county portals block automated access

They exist only in county-level records and local databases requiring human/browser access.

## Correct Architecture: 3-Tier Enrichment

```
Your CSV (428/799 rows)
        ↓
  Python orchestrator
        ↓
  ┌─────────────────────────────────────────┐
  │  TIER 1: No-friction sources (instant)  │
  │  TDLR bulk CSV  →  Comptroller API      │
  │  OpenCorporates API                     │
  │  (handles ~55-70% automatically)        │
  └────────────────┬────────────────────────┘
                   │ remaining ~30-45%
                   ↓
  ┌─────────────────────────────────────────┐
  │  TIER 2: Browser-Use + Hermes Agent     │
  │                                         │
  │  Agent navigates to:                    │
  │  → Dallas County DBA portal             │
  │  → Tarrant County DBA portal            │
  │  → TX SOS (after one-time login)        │
  │  → BBB profile pages                    │
  │                                         │
  │  Hits CAPTCHA? → PAUSES                 │
  │  User solves, agent resumes, extracts   │
  └────────────────┬────────────────────────┘
                   │ true ghosts
                   ↓
  ┌─────────────────────────────────────────┐
  │  TIER 3: Exa + SpiderFoot queue        │
  └─────────────────────────────────────────┘
```

## Key Fixes

**TDLR Bulk Download (replaces scraper function):**
```python
import pandas as pd

TDLR_CSV_URL = "https://data.texas.gov/api/views/7358-krk7/rows.csv?accessType=DOWNLOAD"

def load_tdlr_bulk():
    df = pd.read_csv(TDLR_CSV_URL, dtype=str)
    return df[df["Status"].str.lower() == "active"]

def lookup_tdlr_bulk(tdlr_df, business_name):
    biz_lower = business_name.lower()
    match = tdlr_df[tdlr_df["BusinessName"].str.lower().str.contains(biz_lower, na=False)]
    if not match.empty:
        return match.iloc[0]["LicenseeName"]
    return ""
```

**Browser-Use Agent for County DBA (replaces scraper functions):**
```python
from browser_use import Agent, Browser
from langchain_ollama import ChatOllama

browser = Browser()  # real Chromium window
agent = Agent(
    task="Search Dallas County Clerk for assumed name filings for 'BUSINESS_NAME', extract owner name, return as JSON",
    llm=ChatOllama(model="hermes3:8b"),
    browser=browser
)
result = await agent.run()
```

## Revised Reality Check
- ~30-40% trades (HVAC/plumbing/electric) → TDLR bulk CSV solves instantly
- ~25-30% incorporated (LLC/Corp) → Comptroller API or OpenCorporates
- ~30-40% sole proprietors → County DBA (browser agent) or SpiderFoot

The 0/428 result was a false floor caused by broken access methods, not an absence of data.
