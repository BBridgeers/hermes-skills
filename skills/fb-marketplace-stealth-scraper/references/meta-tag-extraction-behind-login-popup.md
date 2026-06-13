# FB Meta Tag Extraction Behind Login Popup

**Date**: 2026-06-12
**URL**: `https://www.facebook.com/marketplace/item/1291380143164878/` (2004 Nissan Pathfinder XL, Denton TX, $4,750)

## Discovery

Facebook Marketplace shows a login popup overlay for non-authenticated users, but ALL listing data is served in the HTML:

### Meta tags (visible without login)
```
og:title: "2004 Nissan Pathfinder · XL"
og:description: "For Sale: 2004 Nissan Pathfinder 4WD - Excellent Condition. Clean title, only 120k miles!"
description: same as og:description
og:image: full FB CDN URL to primary photo
og:url: clean listing URL
twitter:title / twitter:description: duplicates
```

### Visible body text (behind popup, extractable via JS)
```
$4,750
Listed 4 days ago in Denton, TX
Driven 120,000 miles
Automatic transmission
Exterior color: Gold · Interior color: Black
Fuel type: Gasoline
1 owner
This vehicle is paid off
Seller's description: For Sale: 2004 Nissan Pathfinder 4WD - Excellent Condition...
```

## Extraction Pattern

```python
# Always extract meta tags FIRST — they work without login
page_title = await page.title()
og_title = await page.evaluate("document.querySelector('meta[property=\"og:title\"]')?.content")
og_desc = await page.evaluate("document.querySelector('meta[property=\"og:description\"]')?.content")

# Parse visible body text — listing renders behind login popup
body_text = await page.evaluate("document.body.innerText")

# Regex extraction from body text
price_match = re.search(r'\$([\d,]+)', body_text)           # "$4,750"
mileage_match = re.search(r'(\d{2,3}(?:,\d{3})*)\s*miles', body_text, re.IGNORECASE)
trans_match = re.search(r'(Automatic|Manual|CVT)\s*transmission', body_text, re.IGNORECASE)
color_match = re.search(r'Exterior color:\s*(\w+)\s*·\s*Interior color:\s*(\w+)', body_text)
fuel_match = re.search(r'Fuel type:\s*(\w+)', body_text, re.IGNORECASE)
```

## Why Scraper Misses This

The `scrape_listing_detail` function checks `if page_title in ("Facebook", "Error", ...)` and attempts login before extracting meta tags. When login fails (which it often does with bare Playwright), the function returns an error instead of parsing what it already has. Fix: always parse meta tags + body text FIRST, login is optional enhancement.

## Browserbase vs Bare Playwright

Hermes' browser (Browserbase with residential proxies) can see the full page including meta tags. Bare Playwright on the VPS gets blocked by FB anti-bot before reaching extraction logic. The meta tags are there in BOTH cases — the difference is whether the scraper tries to parse them before giving up.
