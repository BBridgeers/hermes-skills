---
name: fb-marketplace-scraper
version: 1
description: Facebook Marketplace scraper strategy — credential setup, multi-strategy cascade, login-wall handling, and Groq vision fallback for detail extraction from vehicle-analyzer repo.
triggered_by: Facebook Marketplace scraping via vehicle-analyzer (BBridgeers/vehicle-analyzer). Multi-strategy cascade, credential-based FB login, AI vision fallback for detail extraction.
last_updated: 2026-05-24
domain: web-scraping
---

# Skill: fb-marketplace-scraper

Triggered when scraping Facebook Marketplace listings via the vehicle-analyzer scraper stack. Covers credential setup, strategy cascade behavior, detail extraction, login-wall handling, and AI vision fallback.

## Pattern

Scraping FB Marketplace on veracar.co's backend scraper (VPS port 8765). 5-level strategy cascade degrades gracefully. Detail scraping uses Playwright meta-tag extraction first, falls back to Groq vision OCR for screenshot-based enrichment.

## Protocol

1. **Credential setup** — Set `FB_EMAIL` and `FB_PASSWORD` env vars. Scraper's `_attempt_fb_login()` logs into `mbasic.facebook.com`, saves cookies to `~/.fb_scraper_sessions/<session_id>/cookies.json`, reuses them until FB rotates (~24h).
2. **Strategy cascade** (search): `stealth_browser` → `fresh_browser` → `scrapling_escalate` → `apify_remote` → `screenshot_fallback`. First strategy returning listings wins. Apify needs `APIFY_API_TOKEN` for residential proxies.
3. **Detail scraping** — Playwright launches headless Chromium, loads session cookies, applies `playwright-stealth`, navigates to listing URL at `domcontentloaded`, extracts `og:*` meta tags + JSON price blobs from `<script type="application/json">` elements. Falls back to regex HTML parsing if JSON unavailable.
4. **Vision fallback** — Set `GROQ_API_KEY` to enable `vision_extractor.py`. Captures listing screenshot → Groq LLaVA OCR → merges structured data into result. Non-fatal if it fails.
5. **Session persistence** — `SessionManager` handles per-session_id cookie files. Pass same `session_id` across API requests to reuse authenticated sessions.

## Failure Modes

- **"Could not extract listing data — Facebook may require login"** → Meta tags gated. Fix: set FB credentials so `_attempt_fb_login` runs before detail scrape, or enable Apify residential proxy strategy.
- **Stale cookies** → FB rotates sessions ~24h. Auto-reauthenticates if credentials are set.
- **Groq vision empty** → Screenshot capture failed or model missed data. Non-fatal; falls back to meta-tag data only.
- **Apify skipped** → `APIFY_API_TOKEN` not set. Requires token + paid plan for residential proxies.

## References

- `references/scraper-architecture.md` — Full strategy cascade and code flow map
- `references/credential-setup.md` — Environment variable configuration and 2FA handling