# Facebook Marketplace Scraper — Text Fallback Extraction

## Problem

The VPS scraper's Playwright browser gets blocked by Facebook anti-bot within seconds. The `scrape_listing_detail` function tries four strategies (Stealth Browser → Fresh Browser → Scrapling CLI → Apify) but all fail because:

1. FB cookies expire after ~9 days — the `_attempt_fb_login` function uses `mbasic.facebook.com/login` which may be deprecated
2. Bare Playwright without residential proxies triggers immediate bot detection
3. The login wall dialog overlays the page but the underlying HTML still contains listing data in meta tags and visible text

## Solution: Text Fallback in `scrape_listing_detail`

Added text-based extraction that parses `document.body.innerText` when DOM selectors fail. This runs when the page title is "Facebook", "Error", or empty — indicating the login wall is up but content is behind it.

### Key observations (2026-06-12)

- FB listing data IS available WITHOUT login in:
  - `<meta property="og:title">` — "2004 Nissan Pathfinder · XL"
  - `<meta property="og:description">` — full seller description
  - `<meta name="description">` — abbreviated seller description
  - `document.body.innerText` — contains ALL data: price, mileage, location, transmission, fuel type, colors, description
- The login wall is a popup overlay; the page content loads behind it
- Hermes' browser (Browserbase with residential proxies) can extract this data
- The bare Playwright scraper on the VPS gets blocked before reaching the text fallback

### Text fallback code (in `scrape_listing_detail`, after line 1458)

```python
title = og_title or ""
if not title or title in ("Facebook", "Error", ""):
    body_text = await scraper.page.evaluate("() => document.body?.innerText || ''")
    if body_text:
        title_match = re.search(r'^([\d]{4}\s+.+?)\n', body_text)
        if title_match: title = title_match.group(1).strip()
        
        price_match = re.search(r'\$([\d,]+)', body_text)
        if price_match and not price: price = int(price_match.group(1).replace(",", ""))
        
        miles_match = re.search(r'([\d,]+)\s*miles', body_text)
        if miles_match: mileage = int(miles_match.group(1).replace(",", ""))
        
        loc_match = re.search(r'(?:in|Location[:\s]*)([A-Z][a-z]+,\s*[A-Z]{2})', body_text)
        if loc_match: json_location = loc_match.group(1)
        
        trans_match = re.search(r'(Automatic|Manual|CVT)\s*(?:transmission)?', body_text)
        if trans_match: transmission = trans_match.group(1)
        
        fuel_match = re.search(r'Fuel type[:\s]*(\w+)', body_text)
        if fuel_match: fuel_type = fuel_match.group(1)
        
        color_match = re.search(r'Exterior color[:\s]*(\w+)[^·]*Interior color[:\s]*(\w+)', body_text)
        if color_match:
            exterior_color = color_match.group(1)
            interior_color = color_match.group(2)
        
        desc_match = re.search(r"Seller's description\s*\n(.+)", body_text, re.DOTALL)
        if desc_match: description = desc_match.group(1).split("See more")[0].strip()[:500]
```

## Lessons

1. **Don't fight FB scraper for 10+ turns.** When URL scraping fails, tell the user immediately and suggest screenshots.
2. **FB data is in meta tags and body text** even when the login wall is visible.
3. **Hermes' browser (Browserbase) can see FB content** — use it to extract listing data directly when the scraper fails.
4. **FB cookies expire in ~9 days.** The scraper's login flow (`mbasic.facebook.com`) may not work anymore. Fresh cookies from the user's actual browser are the most reliable auth method.
5. **The "stuck Xterra" bug**: When extraction fails and returns empty data, old form state persists because `setForm({...f, ...v})` only overrides populated fields. Always clear form fields explicitly on extraction failure.
