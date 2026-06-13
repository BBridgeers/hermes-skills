---
name: webapp-code-and-ui-audit
description: Systematic full-application code + UI audit for deployed web apps — maps architecture, tests live functionality, cross-references frontend-backend sync, and delivers a structured priority-ranked findings report.
version: 1
triggered-by: User asks for "audit", "full audit", "code + UI audit", "check what's broken", "how functional is X", "what's working and what's not" on a deployed web application.
last-updated: 2026-05-24
---

## Pattern

A deployed web application needs a comprehensive audit to answer: what works, what's broken, what's missing, and where is the frontend out of sync with the backend. The audit must test live functionality in a real browser, not just read code, and must produce a structured report the user can immediately act on.

## Protocol — Four-Phase Audit

### Phase 1 — Map the Codebase

1. Map the directory tree: pages, components, API routes, config files, scrapers/services
2. Read every API route file and extract: method signatures, external dependencies (APIs, databases, KV stores), key logic
3. Grep frontend for all `fetch()`/`axios`/API calls — cross-reference against route file list
4. Identify environment variable dependencies (`process.env.*`, hardcoded URLs, fallback defaults)
5. Inventory all form fields and interactive elements (buttons, dropdowns, upload zones)

### Phase 2 — Test Live Site

1. Navigate to every page via `browser_navigate` — capture full DOM snapshots
2. Exercise form interactions: type into textboxes, select dropdowns, decode VIN, etc.
3. Click every enabled button — observe what triggers an API call vs. what's dead
4. Check browser console for JS errors and failed network requests via `browser_console`
5. Try edge cases: empty form submit, partial data, malformed URLs

### Phase 3 — Check Backend Services

1. SSH/terminal into any backend servers (scraper, Redis, etc.) — check process list + health endpoints
2. Verify connectivity between deployed frontend and backend services (env vars, URLs)
3. Test backend endpoints directly with curl where possible
4. Check for silently disabled features (greyed-out checkboxes, missing source URLs)

### Phase 4 — Synthesize & Report

Produce a structured report with exactly these sections:

1. **Architecture Overview** — table: layer, technology, status
2. **What Works** — verified-by-testing findings, grouped by feature area
3. **What's Broken or Missing** — each finding with: what, impact, root cause if known
4. **Scraper/Service Pipeline Health Check** — if applicable, table of components + status
5. **Frontend/Backend Sync Gaps** — table: feature, frontend status, backend status, sync verdict
6. **Priority Ranking** — P0 (critical/breaks core), P1 (high/missing feature), P2 (medium/UX), P3 (low/nice-to-have)
7. **Bottom Line** — 2-3 sentence executive summary

## Report Format Rules

- Use tables for any multi-attribute comparison
- Use ✅ / ⚠️ / ❌ / ⬜ symbols for status columns
- Each broken finding must state IMPACT, not just existence
- Priority tiers must be actionable — P0 items block core functionality NOW
- Bottom line must name the 2-3 most important findings

## Failure Modes

- **Skip live testing**: Reading code is not enough. API routes can exist but fail at runtime due to missing env vars, timeouts, or dependency failures. Always test.
- **Assume mock data is real**: Pages with hardcoded demo content look functional but have no backend. Check whether data comes from API calls or constants.
- **Miss disabled features**: Greyed-out checkboxes, disabled buttons, "coming soon" labels — flag these as broken/missing, not functional.
- **Ignore env var fallback defaults**: `process.env.X || 'http://localhost:8765'` means the app will silently fail in production if X isn't set. Always flag these.
- **One-pass check**: The first browser snapshot may miss dynamically loaded content. Interact with the page (click, type) to trigger state changes.

## Example Use Case

See `references/veracar-co-audit-template.md` for the output format applied to a real Next.js vehicle evaluation app audit.
