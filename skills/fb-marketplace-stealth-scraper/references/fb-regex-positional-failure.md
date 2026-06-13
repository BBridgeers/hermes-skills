# FB Regex Positional Indexing Failure — Session Detail

## When This Happened
2026-05-26 — User reported regex extraction failing on new FB Marketplace layout.

## Root Cause
`fb_marketplace.py:_parse_marketplace_html()` (line 678) extracts data into global arrays then matches by position:
```python
item_links[0] → vehicle_patterns[0] → prices[0] → mileage_patterns[0]
```

FB changed their HTML layout — prices/vehicle text/mileage now appear in different order or count than listing links. Arrays misalign, fields land on wrong listings or return null.

## What Still Works
- **Apify (Strategy 4)**: Uses residential proxies + crawlerbros actor. Returns fully structured JSON. Not affected by DOM changes.
- **Craigslist**: Uses JSON-LD. Independent of FB.
- **Detail scraping**: `scrape_listing_detail()` extracts from single page — positional issue doesn't apply to single-item extraction.

## Fix Plan (priority order)
1. **Chunk-based extraction**: Find each listing ID in HTML, extract surrounding 3500-char chunk, regex within chunk only
2. **JSON-LD sniffing**: Check for `application/ld+json` script tags before falling back to regex
3. **Apify auto-escalation**: When DIY strategies return 0, automatically fall through to Apify instead of returning empty

## Files to Modify
- `/root/vehicle-analyzer/scraper/fb_marketplace.py` — `_parse_marketplace_html()` and surrounding helpers
