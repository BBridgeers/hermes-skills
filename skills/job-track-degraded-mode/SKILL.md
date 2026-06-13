# Skill: job-track-degraded-mode
Version: 1
Triggered-by: Firecrawl credit exhaustion blocking job-track cron runs (10+ consecutive days)
Last-updated: 2026-06-06

## Pattern
The job-track cron job depends on `web_search` and `web_extract` for: (1) pulling fresh data from the GitHub dashboard repo (`BBridgeers/job-dashboard`), (2) verifying listing URLs are still live, and (3) discovering new job postings. When Firecrawl credits are exhausted, ALL three of these paths fail silently or with "Payment Required" errors. The cron job still runs but operates exclusively on stale local data — producing reports that flag the same broken state repeatedly without the operator's attention.

## Protocol
1. **Check search backend health first.** Before ingesting any data, attempt a lightweight probe (`web_search` for "test" or similar). If it fails with Payment Required, immediately set a `SEARCH_BACKEND_DOWN=true` flag.
2. **Divert to local-only path.** When search is down, skip all GitHub dashboard extraction and listing-verification steps. Go directly to reading local files (`/root/.hermes/output/`, `/root/.hermes/data/applications.csv`).
3. **Surface the outage prominently.** In the generated report, include a dedicated "⚠️ Search Backend Outage" section with: provider name, status, days down, impact summary, and remediation steps (top-up URL, alternative install command). Place this section HIGH in the report — before the pipeline tables.
4. **Flag consecutive-report staleness.** If applications.csv has been empty for 3+ consecutive reports, include a "Report #N with same finding" counter. Make it impossible for the operator to miss.
5. **Lead-age analysis as a proxy.** Since no actual applications exist to age, generate lead-level aging using the same thresholds (>7d = needs-action, >14d = likely-dead). This provides directional signal even without tracked applications.
6. **Produce actionable apply-now targets.** Sort the freshest leads by match score and age. Produce a short "Apply Now" table with 3–5 entries. Include the exact CSV rows the operator needs to add to applications.csv after applying.

## Failure Modes
- **Eternal empty-loop**: Cron runs daily, produces identical "zero applications" finding, operator ignores it because no new information is presented. Break this by escalating the counter and varying the presentation.
- **Silent search death**: Firecrawl exhausts, cron continues running with no errors, reports simply have fewer/new leads. The degradation is invisible unless explicitly surfaced.
- **Wrong target for aging**: Applying the 7/14-day aging rules to leads instead of applications produces misleading "ghosted" labels. Distinguish clearly: lead aging vs. application aging.

## Examples
From June 6, 2026 run:
- Firecrawl exhaustion: Day ~10. Both web_search and web_extract returned "Payment Required"
- applications.csv: empty (Day 15 since first alert, 7th consecutive report)
- Lead aging: 6 leads at 15+ days (likely dead), 11 leads at 11–14 days (likely closing), 12 leads at 4–8 days (still fresh)
- Actionable output: 3 apply-now targets (Datadog 94% 4d, Humach 92% 8d, Responsive 90% 8d) with ready CSV rows
