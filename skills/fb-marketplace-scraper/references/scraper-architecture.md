# FB Marketplace Scraper — Architecture & Strategy Cascade

Source: `BBridgeers/vehicle-analyzer` → `/scraper/fb_marketplace.py`

## Search Flow (5-Strategy Cascade)

```
stealth_browser (saved cookies)
    ↓ fails
fresh_browser (new fingerprint, may trigger FB challenge)
    ↓ fails
scrapling_escalate (Cloudflare bypass via Scrapling CLI)
    ↓ fails
apify_remote (managed browsers + residential proxies, requires APIFY_API_TOKEN)
    ↓ fails
screenshot_fallback (fresh browser again, last resort)
```

Each strategy runs in a try/except inside `search()` (~line 970). On failure, logs the exception and continues. First strategy to return listings wins.

## Detail Scraping Flow

`scrape_listing_detail()` (line 1018):

1. Launch headless Chromium via Playwright
2. Load session cookies if available (`session_id` param)
3. Apply `playwright-stealth` to mask automation
4. Navigate to listing URL, `domcontentloaded` (no JS wait needed for meta tags)
5. Extract `og:title`, `og:description`, `og:image` from meta tags
6. Parse JSON blobs in `<script type="application/json">` for price, condition, location
7. Fallback: regex price extraction from raw HTML
8. Parse year/make/model/trim from title
9. Extract mileage from description
10. AI vision enrichment: screenshot → Groq LLaVA → merge structured data (lines 1229-1265)
11. Return merged result dict

If step 5-6 fail (no meta tags returned), raises exception at line 1276.

## Login Flow

`_attempt_fb_login()` (line 399):
- Targets `mbasic.facebook.com` (lighter anti-bot than www)
- Reads `FB_EMAIL` / `FB_PASSWORD` from env
- Handles 2FA checkpoint detection (screenshot + manual intervention prompt)
- Saves cookies to `~/.fb_scraper_sessions/<session_id>/cookies.json`
- Subsequent runs load cookies directly, skipping login

## Key Code Locations

| What | File | Line(s) |
|---|---|---|
| Strategy cascade loop | `fb_marketplace.py` | ~970-1014 |
| Detail scraper (meta tags + JSON) | `fb_marketplace.py` | 1018-1276 |
| Login flow | `fb_marketplace.py` | 399-515 |
| Login wall detection | `fb_marketplace.py` | 529 |
| Vision extraction integration | `fb_marketplace.py` | 1229-1265 |
| API server (FastAPI) | `server.py` | 1-211 |
| Apify actor mapping | `apify_strategy.py` | 1-411 |