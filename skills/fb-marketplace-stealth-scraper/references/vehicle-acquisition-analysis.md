# Vehicle Acquisition Analysis Framework

Reference for the vehicle screening and ranking pipeline used in used-car acquisition workflows. Use this when evaluating vehicle listings against a budget + Uber-compliance + reliability profile.

## Data Sources

Two sources feed the pipeline:

1. **Facebook Marketplace** — via `FBMarketplaceScraper.search()`. Returns `dict` with keys:
   - `listings`: list of vehicle dicts with `title`, `year`, `make`, `model`, `trim`, `price`, `mileage`, `vin`, `location`, `sourceUrl`, `source`, `scrapedAt`, `description`, `postedDate`, `titleStatus`, `images`
   - `strategy_used`: which cascade strategy succeeded (e.g., `stealth_browser`)
   - `total_found`, `elapsed_seconds`, `search_url`
   - **PITFALL**: `search()` returns a **dict**, not a list. Access listings via `result["listings"]`.

2. **Craigslist** — via JSON-LD parser. Returns `list` of dicts with `title`, `price`, `year`, `make`, `model`, `location`, `source_url`, `images`.
   - JSON-LD format changed June 2026 — items now wrapped in `ListItem` objects. Use `product = item.get("item", item)` to unwrap.

## Screening Pipeline

### Phase 1 — Initial Filter

Apply hard rejection rules FIRST before scoring:

1. **CVT Transmission** — auto reject:
   - `("nissan", "rogue")`, `("nissan", "sentra")`, `("nissan", "versa")`, `("nissan", "altima")` (2013-2018), `("nissan", "juke")`
   - `("jeep", "compass")`, `("jeep", "patriot")`
   - `("dodge", "caliber")`
   - `("subaru", "impreza")`, `("subaru", "legacy")`, `("subaru", "forester")`, `("subaru", "outback")`
   - `("mitsubishi", "outlander")` — check trim, some CVT

2. **Catastrophic failure platforms** — reject UNLESS documented preemptive fix:

| Make | Model | Years | Failure |
|------|-------|-------|---------|
| Ford | Explorer | 2002-2010 | 4.0L SOHC timing chain cassette failure — $3K+ repair |
| Ford | Expedition | 2003-2008 | 5.4L 3V Triton — cam phaser failure, spark plug breakage |
| Ford | F-150 | 2004-2010 | 5.4L 3V Triton — cam phaser/spark plug issues |
| Nissan | Pathfinder | 2005-2010 | SMOD — radiator/transmission cross-contamination |
| Nissan | Xterra | 2005-2010 | SMOD — radiator/transmission cross-contamination |
| Chevrolet | Equinox | 2010-2017 | 2.4L Ecotec — oil consumption, timing chain failure |
| Chevrolet | Traverse | 2009-2017 | 3.6L timing chain stretch, water pump, transmission |
| GMC | Acadia | 2009-2017 | Same 3.6L as Traverse |
| Buick | Enclave | 2009-2017 | Same 3.6L as Traverse |
| Kia | Sorento | 2011-2013 | 2.4L Theta II — connecting rod bearing failure |
| Hyundai | Santa Fe | 2010-2014 | 2.4L Theta II — connecting rod bearing failure |
| Hyundai | Sonata | 2011-2014 | 2.4L Theta II — connecting rod bearing failure |
| Kia | Optima | 2011-2014 | 2.4L Theta II — connecting rod bearing failure |

3. **Uber compliance** — flag, don't reject:
   - Clean title + 2012 or newer = UBER-COMPLIANT
   - Rebuilt/salvage = NON-UBER (salvage/rebuilt)
   - Older than 2012 = NON-UBER (<2012)

### Phase 2 — Quality Scoring

Score each viable vehicle on a 0-100 scale:

```python
score = 0

# Year bonus
if year >= 2015: score += 30
elif year >= 2012: score += 20
elif year >= 2008: score += 10
elif year >= 2006: score += 5

# Price bonus (lower = better)
if price <= 3000: score += 20
elif price <= 4000: score += 15
elif price <= 5000: score += 10
elif price <= 6000: score += 5

# SUV bonus
if model in SUV_KEYWORDS: score += 10

# Brand reliability bonus
if make in ("toyota", "honda", "lexus", "acura"): score += 15
elif make in ("ford", "chevrolet", "gmc", "mazda", "subaru"): score += 5

# Uber compliance bonus
if uber_compliant: score += 20

# Data completeness bonus
if title_status_known: score += 5
```

### Phase 3 — Deep Evaluation

For top-scoring candidates, evaluate:
- Powertrain-specific reliability (engine + transmission combo)
- Dog-friendliness (leather vs cloth, rear seat space)
- Seller transparency (title status, VIN availability)
- Negotiation headroom (market value vs asking price)
- Real entry cost (asking + immediate maintenance)

## FB Cookie Injection

The reliable auth path for FB Marketplace scraping:

1. **Extract cookies** from a browser where FB is already logged in
2. **Required cookies**: `c_user`, `xs`, `fr`, `datr`, `sb`
3. **Save** to `~/.fb_scraper_sessions/default/cookies.json` in Playwright JSON format
4. The stealth browser strategy replays these cookies — no login needed

**Playwright JSON format:**
```json
[{"name":"c_user","value":"1345871044","domain":".facebook.com","path":"/","secure":true,"httpOnly":false,"sameSite":"None"}]
```

**Netscape → Playwright conversion**: Parse tab-separated Netscape cookie files (7-column format) and map to Playwright's cookie schema. FB auth cookies need `sameSite: "None"` for cross-context use.
