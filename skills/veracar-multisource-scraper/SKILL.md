---
name: veracar-multisource-scraper
description: "Add a new marketplace scraper source to veracar.co: Vercel-side scraper class, plugin registry registration, field mapping from external API to ScrapedVehicle, dual-path wiring (single-listing detail + bulk sweep), and UI auto-scrape from query params."
category: devops
tags: [veracar, scraper, registry, nextjs, marketplace]
---

# Adding a New Marketplace Scraper to veracar.co

When adding a new scraper source (Facebook, Craigslist, AutoTempest, etc.) to veracar.co, you touch four layers. Follow this checklist in order.

## 1. Vercel-side scraper class (src/lib/scrapers/)

Create `src/lib/scrapers/<source>.ts` implementing the `Scraper` interface:

```typescript
import { Scraper, ScrapedVehicle } from './types';

export class FacebookMarketplaceScraper implements Scraper {
    canHandle(url: string): boolean {
        // Regex to detect this source's URLs
        return /facebook\.com\/marketplace\/item\/\d+/i.test(url);
    }

    async scrape(url: string): Promise<ScrapedVehicle> {
        // Delegate to VPS scraper (or inline logic for Craigslist/AutoTempest)
        const resp = await fetch(`${VPS_SCRAPER_URL}/api/scrape/detail`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, session_id: 'default' }),
            signal: AbortSignal.timeout(45000), // 45s — FB pages are heavy
        });

        const data = await resp.json();
        if (!data.success || !data.listing) {
            throw new Error(data.error || 'Scraper returned empty result');
        }

        // Map external fields (snake_case from Python VPS) → ScrapedVehicle (camelCase)
        const L = data.listing;
        return {
            title: L.title || '',
            year: L.year ? Number(L.year) : undefined,
            make: L.make || '',
            model: L.model || '',
            trim: L.trim || '',
            price: L.price ? Number(L.price) : undefined,
            mileage: L.mileage ? Number(L.mileage) : undefined,
            vin: L.vin || undefined,
            location: L.location || '',
            sourceUrl: L.sourceUrl || url,
            source: 'facebook',
            description: L.description || '',
            postedDate: L.postedDate || '',
            titleStatus: L.titleStatus || '',
            images: L.images || [],
            bodyStyle: L.bodyStyle || '',
            transmission: L.transmission || '',
            fuelType: L.fuelType || '',
            drivetrain: L.drivetrain || '',
            engine: L.engine || '',
            cylinders: L.cylinders ? Number(L.cylinders) : undefined,
            exteriorColor: L.exteriorColor || '',
            interiorColor: L.interiorColor || '',
            condition: L.condition || '',
            conditionExterior: L.conditionExterior || '',
            conditionInterior: L.conditionInterior || '',
            conditionMechanical: L.conditionMechanical || '',
            safetyRating: L.safetyRating || '',
            numOwners: L.numOwners ? Number(L.numOwners) : undefined,
            paidOff: L.paidOff || false,
            sellerName: L.sellerName || '',
            sellerRedFlags: L.sellerRedFlags || '',
            sellerQuotes: L.sellerQuotes || '',
        };
    }
}
```

Key: `canHandle(url)` returns true for this source's URLs. `scrape(url)` calls the appropriate backend (VPS for JS-heavy sites, inline logic for static ones) and maps ALL 35+ fields.

## 2. Register in the scraper registry

In `src/lib/scrapers/index.ts`, import your scraper and add to the array:

```typescript
import { FacebookMarketplaceScraper } from './facebook';

const scrapers: Scraper[] = [
    new CraigslistScraper(),
    new AutoTempestScraper(),
    new FacebookMarketplaceScraper(),  // <-- add here
];
```

The existing `scrapeVehicle(url)` function iterates `scrapers.find(s => s.canHandle(url))` — zero changes needed elsewhere.

## 3. Update types (if new fields added)

In `src/lib/scrapers/types.ts`, add any new fields to `ScrapedVehicle`. All fields are optional except `title`, `price`, `mileage`, `description`, `images`, `sourceUrl`.

## 4. Enable in MarketSweepPanel UI (if bulk search supported)

In `src/components/MarketSweepPanel.tsx`:

- **Enable the source checkbox**: Remove `disabled: true` from the `SOURCE_OPTIONS` entry.
- **Wire the sweep route**: The existing `/api/scrape/sweep` already calls `VPS_SCRAPER_URL/api/scrape/search` for `source === 'facebook'`. No route changes needed — just ensure the source key matches.

## 5. Cross-page data flow: sweep → analyze

When a user clicks "Analyze" on a sweep result, navigate to the main page with the listing URL:

```typescript
const handleAnalyzeVehicle = (url: string) => {
    window.location.href = `/?url=${encodeURIComponent(url)}`;
};
```

On the main page (`src/app/page.tsx`), detect `?url=` and auto-trigger scrape:

```typescript
// In the App component:
const [urlParamHandled, setUrlParamHandled] = useState(false);
useEffect(() => {
    if (urlParamHandled || typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    const listingUrl = params.get('url');
    if (listingUrl) {
        setForm((prev) => ({ ...prev, listingUrl }));
        setUrlParamHandled(true);
    }
}, [urlParamHandled]);

// In QuickImportSection — auto-scrape when listingUrl is pre-filled:
const hasAutoScraped = useRef(false);
useEffect(() => {
    if (hasAutoScraped.current || !listingUrl.trim() || isScraping) return;
    hasAutoScraped.current = true;
    setTimeout(() => handleScrape(), 100); // let component mount first
}, [listingUrl]);
```

## 6. Multi-make/model comma-separated sweep\n\nWhen users enter multiple makes/models separated by commas (e.g., \"Toyota, Honda\"), the sweep route should run parallel searches and deduplicate. In `/api/scrape/sweep/route.ts`, replace the single-query FB search with:\n\n```typescript\n// Parse comma-separated makes and models for multi-search\nconst makes = (make || '').split(',').map((s: string) => s.trim()).filter(Boolean);\nconst models = (model || '').split(',').map((s: string) => s.trim()).filter(Boolean);\n\n// Build query combinations — all make×model cross-product\nconst queries: string[] = [];\nif (makes.length > 0 && models.length > 0) {\n  for (const m of makes) {\n    for (const mo of models) {\n      queries.push(`${m} ${mo}`);\n    }\n  }\n} else if (makes.length > 0) {\n  queries.push(...makes);\n} else if (models.length > 0) {\n  queries.push(...models);\n}\nif (queries.length === 0) queries.push('');\n\n// Run in parallel — max 3 concurrent to avoid FB rate limits\nconst chunkSize = 3;\nfor (let i = 0; i < queries.length; i += chunkSize) {\n  const chunk = queries.slice(i, i + chunkSize);\n  const chunkResults = await Promise.allSettled(\n    chunk.map(q =>\n      scrapeFacebookMarketplace({\n        query: q,\n        location: region,\n        maxPrice,\n        maxResults: Math.ceil(20 / queries.length) || 10,\n      })\n    )\n  );\n  // Collect results, deduplicate by URL\n  for (const r of chunkResults) {\n    if (r.status === 'fulfilled' && Array.isArray(r.value)) {\n      for (const listing of r.value) {\n        const url = listing.sourceUrl || listing.url;\n        if (url && seenUrls.has(url)) continue;\n        if (url) seenUrls.add(url);\n        allFbResults.push(listing);\n      }\n    }\n  }\n}\n```\n\nKey behaviors:\n- `make=\"Toyota, Honda\"` + `model=\"Camry, Civic\"` → 4 searches: Toyota Camry, Toyota Civic, Honda Camry, Honda Civic\n- `make=\"Toyota, Honda\"` + no model → 2 searches: Toyota, Honda\n- Results deduplicated by URL across all sub-searches\n- Result budget split evenly: `maxResults/n` per query\n- Chunked at 3 concurrent to avoid Facebook rate limiting\n\nUpdate the UI labels to hint at comma-separation:\n```tsx\n<label>Make (comma-separated)</label>\n<input placeholder=\"e.g. Toyota, Honda, Ford\" />\n<label>Model (comma-separated)</label>\n<input placeholder=\"e.g. Camry, Corolla, Civic\" />\n```\n\n## 7. Batch import to Fleet

Add an "Import All to Fleet" button that POSTs each result to `/api/fleet`:

```typescript
for (const r of results) {
    await fetch('/api/fleet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: r.title || `${r.make} ${r.model}`,
            year: r.year, make: r.make, model: r.model,
            price: r.price, miles: r.mileage,
            sourceUrl: r.url, source: r.source,
            location: r.location, status: 'pending_analysis',
        }),
    });
}
window.location.href = '/fleet';
```

## Craigslist Dynamic Search (JSON-LD Based)

Craigslist embeds structured JSON-LD data in search results pages. This can be scraped with plain HTTP — NO browser, NO Playwright, NO proxies needed. The approach works for any Craigslist city and any category.

### VPS Endpoint: POST /api/scrape/craigslist/search

New file: `scraper/craigslist_search.py` — standalone module imported by server.py

```python
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
    # Build CL search URL
    search_url = f"https://{city}.craigslist.org/search/cta"
    params = {"query": query, "min_price": min_price, ...}
    
    # Fetch HTML (no JS needed)
    html = urllib.request.urlopen(search_url_with_params).read().decode()
    
    # Extract JSON-LD: <script id="ld_searchpage_results" type="application/ld+json">
    script_match = re.search(
        r'<script[^>]*id="ld_searchpage_results"[^>]*>(.*?)</script>',
        html, re.DOTALL
    )
    data = json.loads(script_match.group(1))
    # data["itemListElement"] → array of Product objects with:
    #   - name → title (e.g., "2009 Toyota Camry LE")
    #   - offers.price → price
    #   - offers.availableAtOrFrom.geo → latitude, longitude
    #   - offers.availableAtOrFrom.address → city, state
    #   - image[] → photos
    
    # Extract listing URLs from HTML hrefs
    urls = re.findall(
        rf'https://{city}\.craigslist\.org/[\w]+/cto/d/[\w-]+/[\d]+\.html',
        html
    )
    
    # Parse year/make/model from title
    for item in data["itemListElement"]:
        title = item["name"]
        year, make, model = _parse_title(title)
        # Build VehicleListing dict with 35 fields
```

### Speed: 0.24 seconds (vs 30-100s for FB scraping)

The entire search + parse cycle takes under 1 second because there's no browser, no JavaScript rendering, no anti-bot circumvention. Just one HTTP request + JSON parse.

### Wiring into Vercel Sweep Route

In `src/app/api/scrape/sweep/route.ts`:

1. **Clear the static SOURCE_URLS for craigslist** (now uses dynamic endpoint):
```typescript
const SOURCE_URLS: Record<string, string[]> = {
  craigslist: [],  // now uses dynamic VPS scraper
  facebook: [],
  autotempest: [],
};
```

2. **Add scrapeCraigslistMarketplace function**:
```typescript
async function scrapeCraigslistMarketplace(params: {
  query?: string; city?: string; maxPrice?: number;
  minYear?: number; maxMileage?: number; maxResults?: number;
}): Promise<any[]> {
  const resp = await fetch(`${VPS_SCRAPER_URL}/api/scrape/craigslist/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
    signal: AbortSignal.timeout(30000),
  });
  const data = await resp.json();
  return data.listings || [];
}
```

3. **Add CL branch in dynamic scraper section** (same pattern as FB):
```typescript
} else if (source === 'craigslist') {
  const makes = (make || '').split(',').map(s => s.trim()).filter(Boolean);
  const models = (model || '').split(',').map(s => s.trim()).filter(Boolean);
  // Build cross-product queries
  for (const q of queries) {
    const listings = await scrapeCraigslistMarketplace({
      query: q, city: region, maxPrice, minYear, maxMileage, maxResults: 25,
    });
    // Deduplicate by URL
  }
}
```

4. **Field mapping: snake_case (Python CL) → camelCase (Vercel)**:
```typescript
const record = {
  source_url → url,           posted_date → postedDate,
  title_status → titleStatus, body_style → bodyStyle,
  fuel_type → fuelType,       exterior_color → exteriorColor,
  interior_color → interiorColor, safety_rating → safetyRating,
  num_owners → numOwners,     paid_off → paidOff,
  seller_name → sellerName,   seller_responsiveness → sellerResponsiveness,
  seller_transparency → sellerTransparency,
  seller_red_flags → sellerRedFlags, seller_quotes → sellerQuotes,
};
```

### Pitfall: CL JSON-LD Lacks Mileage/Transmission/VIN

Craigslist search results give title, price, location, coordinates, images. They do NOT include mileage, transmission, fuel type, VIN, or description. Those fields require visiting the individual listing page. The CL search scraper returns what's available and leaves detail fields null.

### Pitfall: Listing URLs Not in JSON-LD

Craigslist's JSON-LD `itemListElement` objects don't include listing URLs. Extract them separately from HTML `<a>` tags with regex. Match full URLs like:
```
https://dallas.craigslist.org/dal/cto/d/garland-2009-toyota-camry-le-4d-its/7932168835.html
```

When the VPS scraper's headless browser strategies fail (FB anti-bot, datacenter IP detection, 2FA challenges), fall through to Apify's crawlerbros actor as a remote strategy. This costs ~$0.10/search but reliably returns 100+ listings with residential proxy support — no cookies or login needed.

### Adding Apify to the Python strategy cascade

In `scraper/fb_marketplace.py`:

1. **Add strategy constant:**
```python
STRATEGY_APIFY = "apify_remote"
```

2. **Add to cascade list** (before screenshot fallback):
```python
strategies = [prefer_strategy] if prefer_strategy else [
    self.STRATEGY_STEALTH,
    self.STRATEGY_FRESH,
    self.STRATEGY_SCRAPLING,
    self.STRATEGY_APIFY,          # <-- new
    self.STRATEGY_SCREENSHOT,
]
```

3. **Add the strategy method:**
```python
async def _strategy_apify(self, search_url: str) -> list[VehicleListing]:
    self._log("Strategy 4: Apify Remote")
    try:
        from apify_strategy import apify_search
        max_results = getattr(self, '_max_results', 20)
        return await apify_search(search_url, max_results)
    except ImportError as e:
        self._log(f"Apify strategy not available: {e}")
        return []
    except Exception as e:
        self._log(f"Apify strategy failed: {e}")
        return []
```

4. **Set `self._max_results` before cascade loop** so the strategy can access it:
```python
self._max_results = max_results
```

### Apify adapter file (scraper/apify_strategy.py)

Create a dedicated adapter file that handles:
- Starting Apify actor runs via REST API
- Polling for completion
- Fetching dataset results
- Mapping Apify's output to VehicleListing (all 38 fields)

**Critical URL construction bug:** When calling Apify API endpoints that already have query params (e.g., `datasets/{id}/items?format=json`), do NOT append `?token=` — use `&token=` instead:

```python
def _call_apify(endpoint: str, method: str = "GET", body: dict = None) -> dict:
    sep = "&" if "?" in endpoint else "?"
    url = f"{APIFY_BASE}/{endpoint}{sep}token={APIFY_TOKEN}"
```

Without this fix, the URL becomes `...items?format=json?token=...` which silently fails and returns 0 items.

**redacted_description is a DICT, not a string:** With `includeListingDetails: true`, Apify returns `redacted_description` as `{"text": "actual description..."}`, not a plain string. Calling `.lower()` on it crashes:

```python
# WRONG:
description = item.get("redacted_description", "")
desc_lower = description.lower()  # crashes if dict

# FIX:
raw_desc = item.get("redacted_description", "")
description = ""
if isinstance(raw_desc, dict):
    description = raw_desc.get("text", "")
elif isinstance(raw_desc, str):
    description = raw_desc
```

### Field mapping: Apify enriched output → VehicleListing

When `includeListingDetails: true` is enabled, Apify returns vehicle-specific fields that are richer than the basic listing fields. Prefer these over title parsing:

| Apify field | VehicleListing | Notes |
|---|---|---|
| `vehicle_make_display_name` | `make` | More reliable than parsing title |
| `vehicle_model_display_name` | `model` | More reliable than parsing title |
| `vehicle_odometer_data.value` | `mileage` | Dict `{"unit":"MILES","value":143000}` |
| `vehicle_fuel_type` | `fuel_type` | "GASOLINE", "DIESEL", etc. |
| `vehicle_transmission_type` | `transmission` | "AUTOMATIC", "MANUAL" |
| `vehicle_condition` | `condition` | "VERY_GOOD", "GOOD", etc. |
| `vehicle_exterior_color` | `exterior_color` | Fallback: top-level `exterior_color` |
| `vehicle_interior_color` | `interior_color` |  |
| `creation_time` | `posted_date` | Unix timestamp → ISO format |
| `vehicle_seller_type` | `seller_name` | When `marketplace_listing_seller.name` is empty |
| `share_uri` | `source_url` | Fallback when `listingUrl` is missing |

**Always provide fallbacks:** Not all Apify runs get enriched vehicle fields. Always fall back to title parsing (`_parse_year_make_model`), subtitle parsing (`_parse_mileage`), and description regex for each field. The `condition` field should try: `vehicle_condition` → `attribute_data.condition` → top-level `condition`.

### Environment setup

1. **systemd service** (`/etc/systemd/system/fb-scraper.service`):
```
Environment=APIFY_API_TOKEN=apify_api_...
```

2. **Must reload + restart** after adding env vars to systemd:
```bash
systemctl daemon-reload && systemctl restart fb-scraper
```

Verify the token is in the running process:
```bash
cat /proc/$(systemctl show --property=MainPID --value fb-scraper)/environ | tr '\0' '\n' | grep APIFY
```

### Timeout tuning

Detail enrichment runs take 80-110 seconds. The internal `_wait_for_run` timeout must be ≥180s to allow for Apify's residential proxy rotation + detail page visits. In the adapter:

```python
status = _wait_for_run(run_id, timeout_sec=180)  # was 120 — too short
```

The Vercel-side sweep route's `scrapeFacebookMarketplace()` also needs a generous `AbortSignal.timeout()` — at least 120000ms (2 min) to accommodate Apify.

## Debugging Silent Failures (Vercel → VPS)

The most common failure mode: sweep returns `totalResults: 0` with no visible error. This is a **Vercel silent failure** — the route falls back to `localhost:8765` which doesn't exist on Vercel serverless infra, and the `fetch()` silently fails or returns empty.

**Diagnostic flow:**

1. **Check VPS scraper logs for incoming requests:**
   ```bash
   journalctl -u fb-scraper --no-pager -n 20
   ```
   If logs show ONLY health checks (`GET /api/scrape/health`) and ZERO search requests (`POST /api/scrape/search` or `/api/scrape/detail`), Vercel is NOT reaching the VPS. The request never leaves Vercel.

2. **Confirm the env var trap:**
   ```typescript
   const VPS_SCRAPER_URL = process.env.VPS_SCRAPER_URL || 'http://localhost:8765';
   ```
   When `VPS_SCRAPER_URL` is unset, the fallback is `localhost:8765`. On Vercel serverless, there's no localhost:8765. The fetch silently fails (connection refused, empty response, or timeout). The route catches it and returns `totalResults: 0`.

3. **Verify the env var on Vercel:**
   Go to Vercel dashboard → Project Settings → Environment Variables → check `VPS_SCRAPER_URL` exists and equals `http://<VPS_IP>:8765` (e.g., `http://VPS_IP_REDACTED:8765`)

4. **Verify firewall allows Vercel:**
   ```bash
   iptables -L INPUT -n | grep 8765
   ufw status | grep 8765
   ```
   Port 8765 must be open to all IPs (bound to `0.0.0.0` in server.py).

**Root cause pattern**: If `totalResults === 0` AND scraper logs show zero search requests → VPS_SCRAPER_URL env var is the culprit. This is NOT a scraper bug — it's a deployment configuration issue.

## Pitfalls

- **VPS_SCRAPER_URL env var — silent failure trap**: Must be set in Vercel dashboard to `http://<VPS_IP>:8765`. The `|| 'http://localhost:8765'` fallback works for local dev but causes silent `totalResults: 0` on Vercel serverless. Always check `journalctl -u fb-scraper` first when sweep returns zero results — if zero search requests appear, the env var is missing (see Debugging section above).
- **Field name mismatch**: The VPS scraper (Python) uses `source_url` and `posted_date` (snake_case), but the Vercel scraper class maps to `sourceUrl` and `postedDate` (camelCase). The route `/api/import-url` returns `data.vehicle` directly — so the scraper class IS the mapping layer.
- **Timeout**: FB pages can take 30-45s. Set AbortSignal timeout to 45s. Vercel serverless functions have a 60s hard limit.
- **Never `[skip ci]` in commits**: Vercel skips deploy. Always push clean commits.

## Verification

After deploy:
1. Paste a FB Marketplace URL in veracar.co Quick Import → Scrape → form auto-fills
2. Go to /sweeps → enable Facebook → Start Sweep → results appear
3. Click "Analyze" on a result → main page opens with listing pre-populated
4. Click "Import All to Fleet" → fleet page shows all vehicles
