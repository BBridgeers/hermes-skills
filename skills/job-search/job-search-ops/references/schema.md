# jobs.db Schema

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT UNIQUE,
    title TEXT,
    company TEXT,
    location TEXT,
    salary TEXT,
    url TEXT,
    ats_url TEXT,
    brief TEXT,
    match_score INTEGER DEFAULT 0,
    track TEXT CHECK(track IN ('corporate','nonprofit')),
    status TEXT DEFAULT 'New' CHECK(status IN ('New','Viewed','Applied','Phone Screen','Interview','Offer','Not a Fit','Not Interested')),
    tier INTEGER DEFAULT 2,
    freshness TEXT,
    full_description TEXT,
    key_requirements TEXT,
    company_overview TEXT,
    why_this_role TEXT,
    interview_prep TEXT,
    talking_points TEXT,
    red_flags TEXT,
    application_url TEXT,
    notes TEXT,
    resume_version TEXT,
    cover_letter_version TEXT,
    viewed_date TEXT,
    applied_date TEXT,
    follow_up_date TEXT,
    is_top_match INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

## CLI (tracker.py)
```bash
python3 tracker.py                    # full board sorted by match score
python3 tracker.py show corp          # corporate only
python3 tracker.py show nonprofit     # nonprofit only
python3 tracker.py show tier1         # Tier 1 (⭐) only
python3 tracker.py update C2 Applied  # mark applied
python3 tracker.py stats              # summary counts
```

## Key Fields
- **job_id**: Short unique ID (C1-CX for corporate, N1-NX for nonprofit)
- **freshness**: Exact when available; "Unverified" if uncertain; never blank
- **red_flags**: ⚠️ prefixed for visibility; include age warnings, comp issues, role misalignment
- **status**: Default "New"; auto-update on Viewed/Applied
