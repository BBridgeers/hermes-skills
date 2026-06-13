---
name: craigslist-jsonld-scraper
description: Scrape Craigslist search results via embedded JSON-LD structured data. No browser, no proxies, no anti-bot needed — just HTTP + JSON parse. Works for any city/category. Returns 0.2s response times with price, location, GPS coordinates, and images.
category: devops
tags: [craigslist, scraping, json-ld, structured-data, vehicles]
---

# Craigslist JSON-LD Scraper

Scrape Craigslist by parsing the structured `<script type="application/ld+json" id="ld_searchpage_results">` data that Craigslist embeds in every search results page. No browser, no JavaScript rendering, no anti-bot circumvention needed.

## When to Use

- Building a Craigslist search aggregator for any category (vehicles, housing, jobs, etc.)
- Need fast (~0.2s) Craigslist search results with price, location, images, GPS
- Want to avoid the overhead of Playwright/Selenium for a server-side-rendered site
- Need a reliable Craigslist data pipeline that won't break on DOM changes

## How It Works

Craigslist embeds an `ItemList` schema in every search results page:

```html
<script id="ld_searchpage_results" type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "itemListElement": [
    {
      "@type": "Product",
      "name": "2009 Toyota Camry LE",
      "offers": {
        "@type": "Offer",
        "price": "3650",
        "priceCurrency": "USD",
        "availableAtOrFrom": {
          "@type": "Place",
          "geo": {
            "@type": "GeoCoordinates",
            "latitude": 32.9227,
            "longitude": -96.6248
          },
          "address": {
            "@type": "PostalAddress",
            "addressLocality": "Garland",
            "addressRegion": "TX"
          }
        }
      },
      "image": [
        "https://images.craigslist.org/01616_lSaEKdrcOWa_600x450.jpg",
        ...
      ]
    }
  ]
}
</script>
```

This is valid JSON-LD with Product schema — the same structure Google uses for rich search results. Parse it as JSON, no HTML scraping needed.

## Implementation

```python
import json
import re
import urllib.request
import urllib.parse
from typing import Optional

def search_craigslist(
    city: str = "dallas",
    query: str = "",
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    max_mileage: Optional[int] = None,
    max_results: int = 30,
) -> list[dict]:
    """Search Craigslist and return parsed listings."""
    
    # Build URL
    # Category: cta = cars+trucks by owner (auto_title_status=1 = clean title)
    search_url = f"https://{city}.craigslist.org/search/cta"
    params = {}
    if query:
        params["query"] = query
    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price
    if min_year is not None:
        params["min_auto_year"] = min_year
    if max_year is not None:
        params["max_auto_year"] = max_year
    if max_mileage is not None:
        params["max_auto_miles"] = max_mileage
    
    if params:
        search_url += "?" + urllib.parse.urlencode(params)
    
    # Fetch HTML — no JavaScript needed
    req = urllib.request.Request(search_url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; CraigslistScraper/1.0)"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode()
    
    # Extract JSON-LD
    script_match = re.search(
        r'<script[^>]*id="ld_searchpage_results"[^>]*>(.*?)</script>',
        html, re.DOTALL
    )
    if not script_match:
        return []
    
    data = json.loads(script_match.group(1))
    items = data.get("itemListElement", [])
    
    # Extract listing URLs (not in JSON-LD — parse from hrefs)
    urls = re.findall(
        rf'https://{re.escape(city)}\.craigslist\.org/[\w]+/cto/d/[\w-]+/[\d]+\.html',
        html
    )
    
    results = []
    for i, item in enumerate(items[:max_results]):
        listing = {
            "title": item.get("name", ""),
            "price": _extract_price(item),
            "location": _extract_location(item),
            "latitude": _extract_geo(item, "latitude"),
            "longitude": _extract_geo(item, "longitude"),
            "images": item.get("image", []) if isinstance(item.get("image"), list) else [],
            "source_url": urls[i] if i < len(urls) else "",
            "source": "craigslist",
        }
        results.append(listing)
    
    return results


def _extract_price(item: dict) -> int:
    try:
        return int(float(item.get("offers", {}).get("price", "0")))
    except (ValueError, TypeError):
        return 0

def _extract_location(item: dict) -> str:
    addr = item.get("offers", {}).get("availableAtOrFrom", {}).get("address", {})
    city = addr.get("addressLocality", "")
    state = addr.get("addressRegion", "")
    return f"{city}, {state}" if city else ""

def _extract_geo(item: dict, field: str) -> Optional[float]:
    return item.get("offers", {}).get("availableAtOrFrom", {}).get("geo", {}).get(field)
```

## Title Parsing (Year/Make/Model)

The `name` field in JSON-LD is the listing title (e.g., "2009 Toyota Camry LE"). Parse it:

```python
KNOWN_MAKES = {
    "toyota", "honda", "ford", "chevrolet", "chevy", "nissan", "bmw",
    "mercedes", "mercedes-benz", "audi", "lexus", "acura", "subaru",
    "volkswagen", "vw", "hyundai", "kia", "mazda", "jeep", "dodge",
    "ram", "gmc", "cadillac", "buick", "chrysler", "tesla", "volvo",
    "land rover", "jaguar", "porsche", "infiniti", "lincoln",
    "mitsubishi", "mini", "fiat", "genesis", "scion", "saturn",
    "pontiac", "oldsmobile", "suzuki", "isuzu",
}

NON_MODEL_WORDS = {
    "it's", "its", "runs", "running", "good", "great", "drives",
    "clean", "nice", "sale", "for", "cash", "firm", "obo", "needs",
    "work", "runs", "low", "miles", "mile", "mi", "new", "used",
    "title", "salvage", "rwd", "fwd", "awd", "4wd", "automatic",
    "manual", "cvt", "gas", "diesel", "hybrid", "electric",
}

def parse_title(title: str) -> tuple[Optional[int], str, str]:
    """Extract year, make, model from title."""
    parts = title.strip().split()
    year = None
    ym = re.match(r'(19\d{2}|20[0-2]\d)\b', parts[0]) if parts else None
    if ym:
        year = int(ym.group(1))
        parts = parts[1:]
    
    make = ""
    model = ""
    for i, word in enumerate(parts):
        word_lower = word.lower().strip(",.!-")
        if word_lower in KNOWN_MAKES:
            make = word
            model_parts = []
            for mp in parts[i+1:]:
                if mp.lower().strip(",.!-") in NON_MODEL_WORDS:
                    break
                model_parts.append(mp)
                if len(model_parts) >= 3:  # Cap at 3 tokens
                    break
            model = " ".join(model_parts)
            break
        # Check two-word makes
        if i + 1 < len(parts):
            two_word = f"{word_lower} {parts[i+1].lower().strip(',.!-')}"
            if two_word in KNOWN_MAKES:
                make = f"{word} {parts[i+1]}"
                model_parts = parts[i+2:i+5]
                model = " ".join(mp for mp in model_parts if mp.lower().strip(",.!-") not in NON_MODEL_WORDS)
                break
    
    return year, make, model
```

## Category Codes

| Code | Category |
|------|----------|
| `cta` | Cars+Trucks - all |
| `cto` | Cars+Trucks - by owner |
| `ctd` | Cars+Trucks - by dealer |
| `mca` | Motorcycles |
| `apa` | Apartments |
| `rea` | Real Estate |
| `apa` | Housing |
| `jjj` | Jobs |
| `ela` | Electronics |

## URL Parameters

| Param | Effect |
|-------|--------|
| `query=` | Keyword search |
| `min_price=` | Minimum price (integer dollars) |
| `max_price=` | Maximum price (integer dollars) |
| `min_auto_year=` | Minimum vehicle year |
| `max_auto_year=` | Maximum vehicle year |
| `min_auto_miles=` | Minimum mileage |
| `max_auto_miles=` | Maximum mileage |
| `auto_title_status=1` | Clean title only |
| `purveyor=owner` | By owner only |
| `purveyor=dealer` | By dealer only |
| `auto_transmission=1` | Automatic |
| `auto_transmission=2` | Manual |

## Pitfalls

### JSON-LD is Only on Search Pages

Individual listing detail pages do NOT embed JSON-LD in the same format. The search results page has `ld_searchpage_results` but the detail page has different (or no) structured data. Use this approach for search/discovery only. For full detail (description, VIN, specs), you must scrape the individual listing page.

### Listing URLs Not in JSON-LD

The `itemListElement` objects don't include the listing URL. Extract them separately from `<a href>` tags in the HTML. Pattern: `https://{city}.craigslist.org/{subdomain}/cto/d/{slug}/{id}.html`

### No Mileage/VIN/Transmission in Search Results

The JSON-LD gives you title, price, location, coordinates, and images. It does NOT include mileage, transmission, fuel type, VIN, condition, or description. Those require scraping the individual listing detail page.

### City-Specific Subdomains

Craigslist search results mix listings from sub-regions: `dallas`, `dal`, `mdf`, `ndf` are all in the Dallas metro area. When building listing URLs from the search page, extract the full URL (including subdomain) rather than reconstructing.

### June 2026 JSON-LD Format Change — `ListItem` Wrapper

As of June 2026, Craigslist changed the JSON-LD structure. Each `itemListElement` is now a Schema.org `ListItem` with the actual product data nested one level deeper:

**OLD format (pre-2026):**
```json
{
  "@type": "Product",
  "name": "2009 Toyota Camry LE",
  "offers": { "price": "3650", ... }
}
```

**NEW format (June 2026+):**
```json
{
  "position": "0",
  "@type": "ListItem",
  "item": {
    "@type": "Product",
    "name": "2009 Toyota Camry LE",
    "offers": { "price": "3650", ... }
  }
}
```

**Fix — unwrap the `ListItem` before accessing product fields:**
```python
for i, item in enumerate(items[:max_results]):
    # NEW: unwrap ListItem to get the actual Product
    product = item.get("item", item)  # Falls back to item itself for old format
    title = product.get("name", "")
    offers = product.get("offers", {})
    price = offers.get("price", "0")
```

This backwards-compatible pattern (`item.get("item", item)`) handles both the old flat format and the new nested format.

### Page Changes

Craigslist rarely changes its HTML structure. The `ld_searchpage_results` ID has been stable for years. However, if Craigslist stops embedding JSON-LD, fall back to HTML parsing of the `.cl-search-result` container (though this is much more fragile and less likely to be needed).

## Verification

```bash
# Test from VPS
curl -s -X POST http://localhost:8765/api/scrape/craigslist/search \
  -H 'Content-Type: application/json' \
  -d '{"city":"dallas","query":"Toyota Camry","max_price":7000,"min_year":2006,"max_results":3}'

# Expected: JSON with success=true, total_found=N, listings array with
# title, price, year, make, model, location, latitude, longitude,
# source_url, images — all from a single HTTP request, under 1 second
```
