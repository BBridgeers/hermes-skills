---
name: job-search-ops
description: End-to-end job search operations pipeline — multi-source searching, lead scoring, tracker management, and application pack generation. Use for any job search session.
---

# Job Search Operations

Full pipeline for finding, scoring, tracking, and applying to jobs. Run as "Job Search Ops Analyst + Senior Recruiter."

## When to Load
- Any job search session
- Building application packs for specific roles
- Managing the running job tracker
- Researching companies/roles/compensation

## Pipeline Stages

### 0. BACKGROUND DISCOVERY (MANDATORY — do not skip)
**CRITICAL**: Never infer the user's background from their project files, VPS activity, shell history, or what you see them doing in other sessions. Use their actual resume. 

**Steps**:
1. Search for resume files on the filesystem: `search_files` with patterns `*resume*`, `*cv*`, `*cover*letter*` under the user's home/project directories
2. The resume is almost always a PDF — extract text with `pdftotext` (install poppler-utils if needed)
3. Read the extracted text and identify: job titles, employers, dates, industry, quota/attainment numbers, certifications, education, territory, and compensation level
4. Check for supplementary files: cover letters from past applications, LinkedIn profile exports, older resume versions
5. Only after you have the user's actual employment history and skills — not their hobby projects — proceed to Phase 1

**Pitfall — do NOT do this**: Looking at what the user does on their VPS (Docker, AI agents, scraping, Linux admin) and assuming that's their professional background. Side projects and self-taught skills are not their resume. If they have 12 years in enterprise sales, search for enterprise sales roles — not DevOps jobs.

### 1. SEARCH
- Search across multiple job boards simultaneously (LinkedIn, Indeed, Monster, Greenhouse, Workday, Built In, etc.)
- Run parallel web_search_plus calls for corporate + nonprofit tracks
- Prefer canonical ATS URLs (Greenhouse/Lever/Workday) over aggregators
- Dedupe: one record per unique job (canonical URL; else company+title+location)

### 2. SCORE & RANK
- Rank by: (1) role match, (2) org/mission fit, (3) compensation fit, (4) freshness, (5) location/work-type
- Tier 1: 85%+ match — apply immediately
- Tier 2: 70-84% — monitor and apply if fresh
- Tier 3: <70% — track only

### 3. EXTRACT & ENRICH
For each lead, extract from the actual listing page:
- Verbatim job description (responsibilities + requirements)
- Posted date / freshness (exact when available; "Unverified" if not)
- Compensation (exact when available; "Not listed" if not)
- Company overview, recent news, competitive position
- Red flags: vague comp, contractor mislabeling, unrealistic scope, excessive travel, hunter/new-logo quotas

### 4. TRACK
- Insert into SQLite `jobs.db` (schema in references/schema.md)
- Maintain RUNNING_JOB_OPPORTUNITIES.md as living tracker
- Track: freshness, status, comp, ATS link, red flags, prep status
- Never guess. Missing fields = "Not listed", "Unknown", or "Unverified"

### 5. BUILD APPLICATION PACK
For Tier 1 matches, build comprehensive pack (see references/application-pack-format.md):
- Verbatim job listing
- Match/quality analysis (subsets A-E + percentages)
- Skills gap analysis + sell-around strategy
- Company overview (5W framework)
- Tailored resume (.docx)
- Tailored cover letter
- Interview prep (STAR stories, elevator pitch, questions to ask)

### 6. APPLY
- Apply via ATS link with tailored resume + cover letter
- Update tracker immediately (status → Applied, date logged)
- Log resume version used

## Output Standard
1. Start with ranked Markdown table (compact, decision-first)
2. Mini-profiles for each Job ID with consistent headings
3. Always end with: "Which Job IDs should I save to the Running Job Opportunities list?"
4. Use bullet points, tables, headers — no walls of text
5. Never guess. Missing fields = "Not listed"

## Exclusions
- Pure hunter/cold outbound sales
- Quota-only SDR/BDR roles
- Contractor mislabeling
- Unrealistic scope
- Mismatched seniority

## References
- `references/application-pack-format.md` — JLL-style comprehensive application pack template
- `references/schema.md` — SQLite jobs.db schema
- `references/tracker-sections.md` — Running tracker required sections
- `references/linkedin-cdp-monitor.md` — Chromium + noVNC + CDP LinkedIn monitoring setup
