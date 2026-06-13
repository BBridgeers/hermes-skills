---
name: fb-marketplace-stealth-scraper
description: Build a stealth browser scraper for Facebook Marketplace with a 5-strategy cascade (Stealth, Fresh, Scrapling, Apify Remote, Screenshot). Covers Playwright version pinning, concatenated-field parsing for FB's May 2026 layout change, 38-field vehicle extraction, Apify crawlerbros integration, session persistence, cookie injection, FastAPI wrapper, and Vercel integration.
version: 2.1.0
category: devops
---

# FB Marketplace Stealth Scraper

Build a bleeding-edge stealth browser scraper for Facebook Marketplace or any aggressively anti-bot site. Multi-strategy cascade: Stealth Browser → Fresh Browser → Scrapling CLI → Screenshot Fallback.

## When to Use

- Scraping Facebook Marketplace (login-walled, Cloudflare-protected, anti-bot)
- Any site that detects headless browsers and serves captchas
- Sites with obfuscated DOM that require content-based (regex) extraction
- Building a VPS-side scraping service that Vercel serverless functions call

## Pitfall: Playwright Node.js v24 Driver Bug

**The problem**: Playwright ≥1.49 bundles its own Node.js runtime. On many platforms this is Node v24, which has a breaking change in the MCP agent bundle (`import_mcpBundle.z` is `undefined`). This crashes Playwright on startup.

**The fix**: Pin to Playwright 1.48.0 (last version before the MCP agent code was added):

```bash
pip install "playwright==1.48.0" --break-system-packages
python -m playwright install chromium
```

Do NOT use `playwright>=1.49` or `patchright` (which ships Node v24). If you must use a newer version, the only reliable fix is to run inside a Docker container with Node 20 LTS.

## Pitfall: playwright-stealth v2 API Change

v1 API (deprecated): `from playwright_stealth import stealth_async` → `await stealth_async(page)`
v2 API (current): `from playwright_stealth import Stealth` → `await Stealth().apply_stealth_async(page)`

Always use the v2 API. The v1 import fails silently or throws `ImportError`.

## Architecture

```
veracar.co (Vercel)                  VPS (persistent service)
┌─────────────────────┐             ┌──────────────────────────────┐
│ /api/scrape/sweep   │──fetch────→│ FastAPI (port 8765)           │
│   POST {sources:    │             │                              │
│   ['facebook']}     │             │ fb_marketplace.py:           │
│                     │             │   Strategy 1: StealthBrowser │
│   stores in Redis   │←──JSON─────│   Strategy 2: FreshBrowser   │
└─────────────────────┘             │   Strategy 3: Scrapling CLI  │
                                    │   Strategy 4: Apify Remote ★ │
                                    │   Strategy 5: Screenshot     │
                                    │                              │
                                    │ SessionManager:              │
                                    │ ~/.fb_scraper_sessions/      │
                                    │   cookies.json + state.json  │
                                    └──────────────────────────────┘
```

## 5-Strategy Cascade

Always start with Strategy 1 and fall through on failure:

1. **Stealth Browser (primary)**: Playwright persistent context + playwright-stealth patches + saved FB cookies. This replays a known-good browser fingerprint and session, dramatically reducing detection.

2. **Fresh Browser (fallback 1)**: New incognito context, fresh fingerprint, no cookies. Less likely to succeed on FB but works on less aggressive sites.

3. **Scrapling CLI (escalation)**: `scrapling extract stealthy-fetch` with `--solve-cloudflare --block-webrtc --hide-canvas`. Heavy artillery for Cloudflare-protected pages. Runs as subprocess to bypass Python import issues.

4. **Apify Remote (production)**: crawlerbros/facebook-marketplace-scraper actor. $1/1K results, residential proxies, anti-detection built-in, no cookies needed. Detail enrichment (`includeListingDetails: true`) yields 70+ fields. This is the strategy that actually works at scale when DIY strategies are blocked by Facebook's anti-bot + device trust + datacenter IP detection.

5. **Screenshot Fallback (last resort)**: Basic navigation + screenshot. At minimum we get the page content as an image for later vision extraction.

## Session Persistence

FB detects fresh browsers and throws captchas/checkpoints. Replaying a known session is critical:

```python
class SessionManager:
    def save_cookies(self, session_id: str, cookies: list):
        path = self.session_path(session_id) / "cookies.json"
        path.write_text(json.dumps(cookies))

    def load_cookies(self, session_id: str) -> list:
        # Load saved cookies and replay them into new context

    def has_valid_session(self, session_id: str) -> bool:
        # Check if session has cookies and is <24h old
```

On every successful page load, save cookies. On next run, load and replay them. If the session is >24h old, treat it as expired and start fresh.

Use Playwright's `launch_persistent_context()` with a `user_data_dir` to maintain browser state across runs:

```python
context = await playwright.chromium.launch_persistent_context(
    user_data_dir=str(session_dir / "browser_data"),
    headless=True,
    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
)
```

## Pitfall: New FB Layout — Concatenated Field Extraction (May 2026)

FB changed their Marketplace listing cards — ALL fields are now concatenated into a single text blob with NO whitespace separators:

```
"$7,1002004 Toyota 4runner SR5 Premium Sport Utility 4DLewisville, TX158K miles"
```

Old regex patterns expecting `$7,100 2004 Toyota...` (whitespace-delimited) fail completely. The fix uses a multi-pass extraction pipeline:

### Step 1: Extract price from start of text
```python
price_match = re.search(r'\$(\d{1,3}(?:,\d{3})*)', text)
```
### Step 2: Find year concatenated right after price digits
```python
year_match = re.search(r'((?:19|20)\d{2})', text_after_price)
```
### Step 3: Known-make lookup (ordered by length for compound names)
```python
makes = ["Mercedes-Benz", "Land Rover", ..., "Toyota", "Honda", ..., "BMW"]
for make in makes:
    if re.search(rf'\b{re.escape(make)}\b', text, re.IGNORECASE):
        vl.make = make
        break
```
### Step 4: Model/trim split using trim-only regex
```python
trims_only = r'\b(?:i-force\s*max|SR5|TRD|Limited|Platinum|Sport|...)\b'
```
### Step 5: Known-cities location match
```python
r'\b(Dallas|Fort\s*Worth|Lewisville|Arlington|...).*?,\s*(?:TX)\b'
```
### Step 6: Mileage from "158K miles" suffix
```python
mile_match = re.search(r'(\d{2,3}(?:\.\d)?)K\s*(?:miles|mi)', text)
```

See `references/fb-layout-may-2026.md` for full test data and before/after examples.

## Content-Based Extraction (Regex, not CSS)

FB Marketplace uses obfuscated class names that change every deploy. CSS selectors break within days. Content-based extraction is the only reliable approach.

**⚠️ May 2026 Layout Change — Concatenated Fields**: FB removed ALL whitespace separators between listing card fields. The title text blob now looks like:
```
$7,1002004 Toyota 4runner SR5 Premium Sport Utility 4DLewisville, TX158K miles
```
No space between price↔year, trim↔location, location↔mileage. Old regex expecting `$7,100 2004 Toyota` fails. The fix: per-card DOM text extraction with known-make lookup tables, DFW city matchers, and concatenation-tolerant parsing.

### V2 Parser (Current — Handles Concatenated Fields)

The parser in `fb_marketplace.py` `_extract_from_dom()` uses a stepwise approach:

1. **Price**: Match leading `$X,XXX` without requiring trailing whitespace
2. **Year**: Find `(19|20)\d{2}` anywhere after price (handles `$7,1002004`)
3. **Make**: Known-make lookup table (43 makes, ordered by length for compound names)
4. **Model**: Text between make and trim/location markers
5. **Trim**: Trim-only regex (SR5, TRD Pro, Limited, i-force max, etc.) — does NOT include model names
6. **Location**: DFW city matcher (120+ cities) with state suffix
7. **Mileage**: `\d+K miles` suffix pattern

**Known Make Lookup Table** (in priority order):
```
Mercedes-Benz, Land Rover, Alfa Romeo, Aston Martin, Rolls-Royce, Lamborghini,
Maserati, Mitsubishi, Volkswagen, Chevrolet, Cadillac, Buick, Chrysler, Dodge,
Toyota, Honda, Nissan, Subaru, Mazda, Hyundai, Kia, Jeep, Ford, GMC, RAM, BMW,
Lexus, Acura, Audi, Volvo, Tesla, Mini, Fiat, Jaguar, Porsche, Infiniti, Lincoln,
Genesis, Scion, Saturn, Suzuki, Isuzu
```

**Trim-Only Regex** (excludes model names entirely):
```
i-force max, i-force, TRD Pro, TRD Off-Road, TRD Sport, Limited, Platinum, Sport,
Touring, XLE, XSE, SE, LE, LX, EX, SX, LT, LTZ, LS, GS, GT, Off-Road, Nightshade,
Premium, SR5, Hybrid, Plug-in, PHEV, EV
```

**DFW City Matcher**: Covers 120+ Dallas/Fort Worth metro area cities including Trophy Club, Southlake, Colleyville, Grapevine, Flower Mound, etc.

### Detail Scraper — ALL Images

The detail scraper now captures ALL listing images (not just og:image). Uses DOM query for `img[src*="fbcdn.net"]` filtering out profile/emoji images. Typically captures 8-12 photos per listing for vision analysis.

### Seller Rating Extraction

Parses FB's JSON data blobs for `marketplace_listing_seller` → extracts name and rating. Auto red-flags:
- Rating < 3.0: `CRITICAL: Very low seller rating: X/5`
- Rating < 3.5: `Low seller rating: X/5`

### Pitfall: Global Regex + Positional Indexing Breaks on Layout Changes

The original `_parse_marketplace_html` extracts data globally then matches by array position:

```python
prices[i] → mileage_patterns[i] → vehicle_patterns[i] → item_links[i]
```

**This breaks when FB changes HTML layout.** Prices may appear in a different count or order than listing cards — `prices[3]` might be the price for `item_links[1]`. All fields shift, landing on wrong listings or coming back null.

**Fix — Chunk-Based Extraction (per listing card):**
```python
# Find each listing card boundary by item ID
for item_id in unique_items:
    # Extract HTML chunk around this listing
    chunk_start = html.find(f'/marketplace/item/{item_id}/')
    chunk = html[max(0, chunk_start-500):chunk_start+3000]
    
    # Regex WITHIN this chunk only — no cross-contamination
    price_match = re.search(r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', chunk)
    if price_match:
        listing.price = int(price_match.group(1).replace(',',''))
    
    ym_match = re.search(r'((?:19|20)\d{2})\s+([A-Z][a-zA-Z-]+)\s+([A-Z][a-zA-Z-]+)', chunk)
    if ym_match:
        listing.year = int(ym_match.group(1))
        listing.make = ym_match.group(2)
        listing.model = ym_match.group(3)
```

**Alternative — JSON-LD First, Regex Fallback:**
FB sometimes embeds structured data. Check before regex:
```python
scripts = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html)
for script in scripts:
    try:
        data = json.loads(script)
        if data.get('@type') == 'Product':
            listing.price = data.get('offers', {}).get('price')
            listing.description = data.get('description', '')
    except: pass
```

**Alternative — Lean on Apify Harder:**
When DIY regex strategies return 0 results, automatically escalate to Apify instead of returning empty. Currently the cascade tries Stealth → Fresh → Scrapling → Apify → Screenshot. If Stealth/Fresh return 0 from failed regex, Apify should be the automatic fallback.

**Key patterns for 35 field extraction**:

```python
# Prices: $12,500 or $12,500.00
prices = re.findall(r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', html)

# Year/Make/Model: "2020 Toyota Camry XLE"
vehicle_patterns = re.findall(
    r'(19|20)\d{2}\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+'
    r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?(?:\s[A-Z]{2,})?)',
    html[:150000]
)

# Mileage: "85,000 miles"
mileage_patterns = re.findall(
    r'(?:mileage|miles|mi\.?|odometer|Odometer)[:\s]*([\d,]+)',
    html, re.IGNORECASE
)

# VIN (17-char, no I/O/Q)
vins = re.findall(r'\b([A-HJ-NPR-Z0-9]{17})\b', html)

# Body style
body_styles = re.findall(
    r'\b(Sedan|SUV|Truck|Coupe|Convertible|Wagon|Hatchback|Minivan)\b',
    html, re.IGNORECASE
)

# Transmission
trans = re.findall(r'\b(Automatic|Manual|CVT|Auto|Man)\b', html, re.IGNORECASE)

# Fuel type
fuels = re.findall(
    r'\b(Gasoline|Diesel|Hybrid|Electric|EV|Flex.Fuel|Gas)\b',
    html, re.IGNORECASE
)

# Drivetrain
drivetrains = re.findall(
    r'\b(FWD|RWD|AWD|4WD|4x4|Front.Wheel.Drive)\b',
    html, re.IGNORECASE
)

# Engine: "2.5L V6 Turbo"
engines = re.findall(
    r'\b(\d+\.\d+L\s*(?:V\d|I\d|H\d)?(?:\\s*(?:Turbo|Hybrid))?)\b',
    html
)

# Cylinders: "6-cylinder" or "6 cyl"
cyls = re.findall(r'\b(\d)\s*-?(?:cylinder|cyl)\b', html, re.IGNORECASE)

# MPG: "22 city / 30 highway"
mpgs = re.findall(
    r'(\d{1,2}\s*(?:city|hwy|highway|mpg|combined)[/\s]+\d{1,2}\s*(?:city|hwy|highway|mpg|combined)?)',
    html, re.IGNORECASE
)

# Colors
ext_colors = re.findall(
    r'(?:Exterior|Paint|Color)[:\s]*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)',
    html, re.IGNORECASE
)

# Title status: "clean title", "salvage title"
title_statuses = re.findall(
    r'\b(clean\s*title|salvage\s*title|rebuilt\s*title|lien)\b',
    html, re.IGNORECASE
)

# Seller
seller_names = re.findall(
    r'(?:seller|listed by|posted by)[:\s]*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)',
    html, re.IGNORECASE
)

# Posted date: "3 days ago", "May 3"
posted_dates = re.findall(
    r'(?:listed|posted)[:\s]*(\d+\s*(?:hours|hrs|days|weeks)\s*ago|'
    r'\d{1,2}/\d{1,2}/\d{2,4})',
    html, re.IGNORECASE
)

# Safety rating
safety = re.findall(
    r'(\d\s*(?:star|out of \d)\s*(?:safety|crash|nhtsa|iihs))',
    html, re.IGNORECASE
)
```

## VPS Deployment (systemd)

```ini
[Unit]
Description=FB Marketplace Stealth Scraper API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/vehicle-analyzer/scraper
Environment=SCRAPER_PORT=8765
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Vercel Integration

The Next.js app calls the VPS scraper via `fetch()`. Set `VPS_SCRAPER_URL` in Vercel environment variables:

```typescript
const VPS_SCRAPER_URL = process.env.VPS_SCRAPER_URL || 'http://localhost:8765';

async function scrapeFacebookMarketplace(params: {
  query?: string;
  location?: string;
  maxPrice?: number;
  minYear?: number;
  maxResults?: number;
}): Promise<any[]> {
  const resp = await fetch(`${VPS_SCRAPER_URL}/api/scrape/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
    signal: AbortSignal.timeout(60000),
  });
  const data = await resp.json();
  return data.listings || [];
}
```

## Full VehicleListing Schema

```python
@dataclass  
class VehicleListing:
    # Core (11 captured from search cards, all 24 from detail page)
    title, year, make, model, trim, price, mileage, vin, location, source_url, source
    
    # Detail-only (populated by /api/scrape/detail)
    description, posted_date, title_status, images  # images now grabs ALL photos
    body_style, transmission, fuel_type, drivetrain
    engine, cylinders, exterior_color, interior_color, seats, mpg
    num_owners, paid_off
    
    # Analysis-phase (filled by veracar.co, NOT the scraper)
    condition, condition_exterior, condition_interior, condition_mechanical
    safety_rating  # NHTSA API lookup by year/make/model
    
    # Seller intel (from FB JSON when available)
    seller_name, seller_responsiveness, seller_transparency
    seller_red_flags  # auto-set when seller rating < 3.5
    seller_quotes
```

### Image Pipeline
Detail scrape now grabs ALL listing images (filtered to fbcdn.net URLs, excluding profile/emoji images). These feed veracar.co's vision analysis for auto condition scoring.

### Seller Red Flags
Detail scrape extracts `marketplace_listing_seller` from FB JSON data. Rating thresholds:
- `< 3.0`: "CRITICAL: Very low seller rating"
- `< 3.5`: "Low seller rating"

## VPS Deployment (systemd)

## Files Created

- `scraper/fb_marketplace.py` — 1750+ lines, core engine with 5 strategies + SessionManager + concatenated-field extraction + all-images pipeline
- `scraper/server.py` — FastAPI REST server (health, search, detail, sessions endpoints)
- `scraper/Dockerfile` — Docker-ready with Playwright 1.48 pinned + chromium install
- `scraper/requirements.txt` — pinned deps
- `src/app/api/scrape/sweep/route.ts` — Vercel-side sweep endpoint

## Pitfall: `search()` Returns Dict, Not List

The `FBMarketplaceScraper.search()` method returns a **dict**, not a list of listings:

```python
result = await scraper.search(query="Toyota", location="dallas", max_price=6000)
# result = {"listings": [...], "strategy_used": "stealth_browser", 
#           "total_found": 20, "elapsed_seconds": 11.73, "search_url": "..."}

# CORRECT:
for listing in result["listings"]:
    print(listing["title"])

# WRONG:
for listing in result:  # iterates dict keys
```

Each listing in `result["listings"]` has these keys: `title`, `year`, `make`, `model`, `trim`, `price`, `mileage`, `vin`, `location`, `sourceUrl`, `source`, `scrapedAt`, `description`, `postedDate`, `titleStatus`, `images`.

## Reference Files (in this skill)

- `references/fb-layout-may-2026.md` — New FB layout: concatenated fields, before/after test data
- `references/field-coverage.md` — Which fields are captured where (search vs detail vs analysis)
- `references/vehicle-acquisition-analysis.md` — Full vehicle screening pipeline: CVT/catastrophic-failure database, Uber compliance rules, quality scoring algorithm, cookie injection reference

## Pitfall: FB New Layout — Concatenated Fields (May 2026)

FB changed their Marketplace listing cards to remove ALL whitespace separators between fields. Listing card text now appears as a single concatenated blob:

```
"$7,1002004 Toyota 4runner SR5 Premium Sport Utility 4DLewisville, TX158K miles"
```

Every regex that expects `\s+` between price↔year, year↔make, trim↔location, or location↔mileage BREAKS. The DOM-level extractor (`_extract_from_dom`) must parse concatenated fields.

### Concatenated-Field Parser Algorithm

1. **Price**: Extract leading `$X,XXX` from start of text `r'\$(\d{1,3}(?:,\d{3})*)'` — no `\s*` between `$` and digits
2. **Year**: Find `(19|20)\d{2}` immediately after price digits — NO whitespace expected between price and year
3. **Make**: Known-makes lookup list (ordered by length, compound names first: "Mercedes-Benz" before "Ford") scanned AFTER year extraction
4. **Model**: Text between make and trim/location, using known trim-only regex to split model from trim
5. **Trim**: Known trim list: `i-force max`, `SR5`, `TRD Pro`, `Limited`, `Platinum`, `XLE`, `XSE`, etc. — matched AFTER model extraction
6. **Location**: Known DFW/Texas city list + state suffix OR generic `City, ST` pattern
7. **Mileage**: `\d{2,3}K\s*miles` at end OR `\d{1,3}(,\d{3})*\s*miles`
8. **Body style**: `Sport Utility` → SUV, `Crew Cab` → Truck, or explicit style name

### Key difference from old regex

Old: `r'\$\s*(\d+)'` expecting optional whitespace
New: `r'\$(\d+)'` — price and year are concatenated: `$7,1002004`

Old: `r'((?:19|20)\d{2})\s+([A-Z][a-z]+...'` expecting whitespace before year
New: Year found anywhere after price, no whitespace expected

Old: positional array indexing (`prices[i]`, `vehicle_patterns[i]`)
New: per-card sequential parsing — price → year → make → model → trim → location → mileage

### DFW City List (included in parser)

100+ DFW Metroplex cities matched with `\s*` tolerance (Fort Worth = Fort\s*Worth) so FB's concatenation doesn't break city matching: Dallas, Fort Worth, Arlington, Plano, Irving, Garland, Mesquite, Carrollton, Frisco, Denton, McKinney, Richardson, Lewisville, Allen, Flower Mound, Grapevine, Southlake, Coppell, Keller, Colleyville, Hurst, Euless, Bedford, Addison, Trophy Club, Roanoke, Justin, Argyle, and 80+ more.

**The symptoms**: Sweep returns 0 results. Scraper logs show requests arriving but all 4 strategies hitting "Hit login/checkpoint wall" within seconds. The scraper IS working, but Facebook Marketplace requires an authenticated session — it redirects unauthenticated traffic to `facebook.com/login`.

**The fix**: Add credential-based login that runs when the login wall is detected:

```python
async def _attempt_fb_login(self, page: Page) -> bool:
    """Try to log into Facebook using FB_EMAIL/FB_PASSWORD env vars."""
    fb_email = os.environ.get("FB_EMAIL", "")
    fb_password = os.environ.get("FB_PASSWORD", "")

    if not fb_email or not fb_password:
        print("[FB-SCRAPER] No FB_EMAIL/FB_PASSWORD set — cannot log in")
        return False

    # Use mbasic.facebook.com — far less aggressive anti-bot
    await page.goto("https://mbasic.facebook.com/login", wait_until="domcontentloaded")
    await asyncio.sleep(3)

    # mbasic has simple form: email + pass on the same page
    email_input = await page.wait_for_selector('input[name="email"]', timeout=10000)
    if not email_input:
        return False
    await email_input.fill(fb_email)

    password_input = await page.wait_for_selector('input[name="pass"]', timeout=5000)
    if password_input:
        await password_input.fill(fb_password)
        await password_input.press("Enter")  # Submit via Enter — reliable on mbasic
    else:
        await email_input.press("Enter")

    await asyncio.sleep(5)

    # Check result — 2FA is a hard blocker
    if "checkpoint" in page.url.lower() or "two_factor" in page.url.lower():
        print("[FB-SCRAPER] 2FA/checkpoint detected — login blocked")
        return False

    # Success = redirected away from login page
    if "login" not in page.url.lower():
        # Save cookies so future runs skip login
        cookies = await self.context.cookies()
        self.sessions.save_cookies(self.session_id, cookies)
        return True

    return False
```

Then patch `_navigate_and_scrape` to attempt login when the wall is hit instead of immediately returning empty:

```python
if "login" in current_url.lower() or "checkpoint" in current_url.lower():
    self._log("Hit login/checkpoint wall — attempting login...")
    logged_in = await self._attempt_fb_login(self.page)
    if logged_in:
        self._log("Login succeeded, navigating to search URL...")
        await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)
        # Continue with normal extraction flow
    else:
        cookies = await self.context.cookies()
        self.sessions.save_cookies(self.session_id, cookies)
        return []  # True failure
```

Set the env vars on the VPS (add to systemd service or `.env`):
```
FB_EMAIL=your_fb_email@example.com
FB_PASSWORD=your_fb_password
```

**Important**: If the account has 2FA enabled, automated login will fail. Use a burner account without 2FA, or export session cookies from a browser where you're already logged in and place them at `~/.fb_scraper_sessions/default/cookies.json`.

## Pitfall: 2FA Page Persists Even After Disabling 2FA

Disabling two-factor authentication in Facebook settings does NOT always remove the `two_step_verification` page. Facebook may still serve this page for:

1. **New/unrecognized devices** — FB detects the VPS IP + headless browser fingerprint as a new device
2. **Device trust challenge** — "Was this you?" confirmation, not a 2FA code entry
3. **Propagation delay** — 2FA disablement can take hours to fully propagate

The `two_step_verification/authentication/` URL appears with an `encrypted_context` parameter. The page may NOT have dismissable "Not Now" or "Skip" buttons — those selectors failed to match in testing. Do NOT rely on dismissing this page.

**Diagnostic screenshot capture** (add to `_attempt_fb_login` 2FA block):

```python
if "checkpoint" in current_url.lower() or "two_step" in current_url.lower():
    try:
        ss_path = os.path.expanduser("~/.fb_scraper_sessions/2fa_page.png")
        await self.page.screenshot(path=ss_path, full_page=True)
        print(f"[FB-SCRAPER] 2FA screenshot saved: {ss_path}")
    except Exception as e:
        print(f"[FB-SCRAPER] Screenshot failed: {e}")
    return False  # 2FA = hard block, don't try dismiss tricks
```

## Pitfall: Python 3.12 `import os` Inside Functions Shadows Module-Level Import

**The symptom**: `[FB-SCRAPER] Login error: cannot access local variable 'os' where it is not associated with a value` — even though `import os` exists at the top of the file and the function body seems correct.

**Root cause**: Python 3.12's variable scoping treats ANY `import os` inside a function body as a LOCAL variable declaration for the ENTIRE function, shadowing the module-level `import os`. If the function uses `os` anywhere BEFORE the local `import os` line, Python raises `UnboundLocalError` with the message above.

**The fix**: NEVER put `import os` (or any import) inside a function body if that module is already imported at module level. Remove the redundant local import and use the module-level one:

```python
# BAD — breaks Python 3.12
async def _attempt_fb_login(self, page):
    fb_email = os.environ.get("FB_EMAIL", "")  # ← uses os BEFORE local import
    # ... 50 lines later ...
    if "two_step" in current_url:
        import os  # ← Python 3.12 marks os as LOCAL, shadowing module-level import
        os.path.expanduser("...")  # ← works here, but broke line 3 above

# GOOD — use module-level import only
async def _attempt_fb_login(self, page):
    fb_email = os.environ.get("FB_EMAIL", "")  # ← uses module-level os
    # ... 50 lines later ...
    if "two_step" in current_url:
        os.path.expanduser("...")  # ← also uses module-level os — no shadowing
```

## Pitfall: Fresh Browser Login Silently Fails (Even with Correct Credentials)

Even with correct credentials, playwright-stealth patches applied, and no 2FA on the account, Facebook's anti-bot detection catches Playwright on desktop login. The symptom: email + password are filled successfully, the login button is clicked, but the URL stays on `facebook.com/login` with no error message. Facebook silently rejects the automated login.

### mbaisic.facebook.com — Worth Trying, Still Not Reliable

Facebook's mobile basic site (`https://mbasic.facebook.com/login`) has a simpler form (email+password on one page) and is LESS aggressive with anti-bot detection than the desktop site. The form filling works reliably — use `input[name="email"]` and `input[name="pass"]`, then `password_input.press("Enter")` to submit. However, two blocker remain:

1. **Datacenter IP detection**: FB still flags datacenter IPs even on mbasic. Login may succeed only to be redirected back to `/login?__mmr=1&_rdr`.
2. **Device trust challenge**: If login reaches `two_step_verification/authentication/`, this is NOT dismissable via "Not Now" or "Skip" buttons — the selectors don't match on this page. Use screenshot capture to diagnose what FB is showing.

The mbasic approach is a useful diagnostic tool (form filling proves credentials are correct), but it is NOT a reliable production login strategy without residential proxies.

**The fix**: Do NOT rely on automated login as a primary strategy. Cookie injection from a real authenticated browser is the only reliable path.

## Pitfall: Facebook Removed Whitespace Between Fields (May 2026 Layout Change)

FB's new listing card layout concatenates ALL fields into one text blob with ZERO whitespace:

```
OLD: "$7,100 · 2004 Toyota 4Runner · Lewisville, TX · 158K miles"
NEW: "$7,1002004 Toyota 4runner SR5 Premium Sport Utility 4DLewisville, TX158K miles"
```

Every regex that expects `\s+` between fields breaks. Price runs into year, trim runs into location, location runs into mileage.

### The Fix: Field-by-Field Extraction with Known-Value Lookups

Abandon positional array matching. Extract each field independently from the concatenated text:

**1. Price**: Leading `$X,XXX` at start of text (no trailing whitespace anchor)
```python
price_match = re.search(r'\$(\d{1,3}(?:,\d{3})*)', text)
```

**2. Year**: First 4-digit `19xx`/`20xx` found (can be concatenated after price digits)
```python
year_match = re.search(r'((?:19|20)\d{2})', text_after_price)
```

**3. Make**: Known-make lookup table (43 makes, compound names first)
```python
makes = ["Mercedes-Benz", "Land Rover", ..., "Toyota", "Honda", ...]
for make in makes:
    if re.search(r'\b' + re.escape(make) + r'\b', text, re.IGNORECASE):
        vl.make = make
        break
```

**4. Model**: Text between make and next trim/location boundary
**5. Trim**: Known trim regex (SR5, TRD Pro, Limited, XLE, i-force max, etc.)
**6. Location**: DFW city lookup (120+ cities) + state pattern
**7. Mileage**: `\d+K miles` at end of text

Full implementation in the DOM extractor at `_extract_from_dom()` in fb_marketplace.py (~lines 730-880).

### All-Images Capture (Detail Page)

The detail scraper now grabs ALL listing images (not just og:image):
```python
all_imgs = await page.evaluate("""() => {
    const imgs = document.querySelectorAll('img');
    const urls = [];
    for (const img of imgs) {
        const src = img.src || img.getAttribute('data-src') || '';
        if (src && src.includes('fbcdn.net') && !src.includes('profile')) {
            urls.push(src);
        }
    }
    return urls;
}""")
```
This captures 10+ photos per listing for veracar.co vision analysis.

### Seller Rating Auto Red-Flag

Extract seller rating from FB JSON data and auto-flag:
```python
if '"marketplace_listing_seller"' in json_str:
    rating = extract_rating(json_str)
    if rating < 3.0:
        vl.seller_red_flags = f"CRITICAL: Very low seller rating: {rating}/5"
    elif rating < 3.5:
        vl.seller_red_flags = f"Low seller rating: {rating}/5"
```

### 2FA Kill-Chat Pattern (WebUI)

When the scraper hits a 2FA wall and needs the user to send a code:
1. Agent outputs `🔐 2FA REQUIRED — send code within 30 seconds`
2. Agent IMMEDIATELY kills the chat/halts — WebUI blocks user messages while agent is "working" (messages stuck at ~2% sending)
3. User sends code in NEW chat turn
4. Agent resumes fresh, reads code, completes 2FA flow

DO NOT stay in "working" state after signaling for 2FA — the user's message will never arrive.

## Cookie Injection — The Reliable Auth Path (Updated)

User can provide cookies in Playwright-compatible JSON format directly. Save to `~/.fb_scraper_sessions/default/cookies.json`:

```json
[{"name":"c_user","value":"1345871044","domain":".facebook.com","path":"/","secure":true,"httpOnly":false,"sameSite":"None"}]
```

Key auth cookies required: `c_user`, `xs`, `fr`, `datr`, `sb`. The scraper's `SessionManager.load_cookies()` will replay these on next search — FB sees the user's real authenticated session.

This is how professional scrapers bypass FB's entire login/2FA/anti-bot stack. Skip login entirely by injecting an existing authenticated session.

### Step 1: Export cookies from a real browser

Use a browser extension (EditThisCookie, cookies.txt) or Chrome DevTools → Application → Cookies → facebook.com. Export as JSON. The scraper now accepts Playwright-format JSON directly:

```json
[{"name":"c_user","value":"1345871044","domain":".facebook.com","path":"/","secure":true,"httpOnly":false,"sameSite":"None"}]
```

### Step 2: Save to session directory

```bash
# Save as ~/.fb_scraper_sessions/default/cookies.json
# The scraper's SessionManager.load_cookies() picks these up automatically
```

### Step 3: Verify

```bash
curl http://127.0.0.1:8765/api/scrape/sessions
# → "default": {"has_cookies": true, "cookie_count": 10}
```

### Required cookies for FB auth

| Cookie | Purpose |
|--------|---------|
| `c_user` | Your Facebook user ID |
| `xs` | Session token |
| `fr` | Browser fingerprint |
| `datr` | Device tracking |
| `sb` | Session boundary |
The user can provide cookies in TWO formats. Handle both:

### Format A: Browser `document.cookie` string (key=value; pairs)

On Chrome (Windows/Mac/Linux):
```
F12 → Application tab → Cookies → facebook.com
```

Or in Console:
```javascript
copy(document.cookie)
```

The result is a single-line string:
```
c_user=1000XXXXXXXXX; xs=XX%3AXXXXX; fr=XXXXXX; datr=XXXXX; sb=XXXXX
```

### Format B: Netscape HTTP Cookie File (tab-separated columns)

This is the standard format exported by browser extensions (EditThisCookie, cookies.txt) and `curl --cookie-jar`. Each line has 7 tab-separated fields:

```
domain  flag  path  secure  expiration  name  value
.facebook.com	TRUE	/	TRUE	1809354018	datr	IjXJaYxLs-sVvF5BlvUct4s9
.facebook.com	TRUE	/	TRUE	1809559653	c_user	1345871044
```

### Step 2: Convert to Playwright JSON cookie format

Both formats need conversion. Playwright's `context.add_cookies()` expects:
```json
[
  {
    "name": "c_user",
    "value": "1345871044",
    "domain": ".facebook.com",
    "path": "/",
    "expires": 1809559653,
    "secure": true,
    "httpOnly": true,
    "sameSite": "None"
  }
]
```

**Conversion script for Netscape format** (the more common export format):

```python
import json
from pathlib import Path

cookies_netscape = """[paste the Netscape cookie file content here]"""

cookies_pw = []
for line in cookies_netscape.strip().split('\n'):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    parts = line.split('\t')
    if len(parts) >= 7:
        domain = parts[0]
        secure = parts[3] == 'TRUE'
        expires = int(parts[4]) if parts[4] != '0' else -1
        name = parts[5]
        value = parts[6]
        
        cookie = {
            "name": name,
            "value": value,
            "domain": domain,
            "path": parts[2] or "/",
            "secure": secure,
            "httpOnly": name in ('datr', 'sb', 'xs', 'c_user', 'fr'),
        }
        if expires > 0:
            cookie["expires"] = expires
        # FB auth cookies need sameSite=None for cross-context use
        cookie["sameSite"] = "None" if name in ('c_user', 'xs', 'fr') else "Lax"
        cookies_pw.append(cookie)

session_dir = Path.home() / ".fb_scraper_sessions" / "default"
session_dir.mkdir(parents=True, exist_ok=True)
(session_dir / "cookies.json").write_text(json.dumps(cookies_pw, indent=2))
print(f"Saved {len(cookies_pw)} cookies")
```

**Conversion for `document.cookie` string format** (simpler):

```python
def convert_cookie_string(cookie_str: str) -> list[dict]:
    cookies = []
    for pair in cookie_str.split("; "):
        if "=" in pair:
            name, value = pair.split("=", 1)
            cookies.append({
                "name": name.strip(),
                "value": value.strip(),
                "domain": ".facebook.com",
                "path": "/",
                "httpOnly": False,
                "secure": True,
                "sameSite": "None",
            })
    return cookies
```

### Step 3: Use browser context (not page) to inject cookies

**Critical**: You CANNOT add cookies to a `browser.new_page()`. You must create a **browser context** first, add cookies to the context, then create pages from it:

```python
# ✅ CORRECT — context allows cookie injection
context = await browser.new_context(
    viewport={"width": 1920, "height": 1080},
    locale="en-US",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/131.0.0.0 Safari/537.36"
)
cookies = session_manager.load_cookies(session_id)
if cookies:
    await context.add_cookies(cookies)
page = await context.new_page()

# ❌ WRONG — direct new_page() can't accept cookies
page = await browser.new_page()
# (cookies are silently ignored or throw errors)
```

### Step 4: Scraper uses injected cookies

The existing `SessionManager.load_cookies()` will pick these up. On next search, the stealth browser strategy replays the cookies — FB sees the same session as the user's real browser and allows access. No login, no 2FA, no captcha.

After injection, verify with:
```bash
curl -X POST http://localhost:8765/api/scrape/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"Honda Civic","location":"dallas","max_results":1}'
```

Check logs for `[FB-SCRAPER] Loaded X saved cookies` — if it goes straight to marketplace results (not `/login`), the injection worked.

## Vercel REST API Env Var Management (When CLI Unavailable)

When `npx vercel` fails (permission issues, auth not set up) or the Vercel CLI is not installed, use the REST API directly:

**Prerequisites**: A Vercel access token from https://vercel.com/account/tokens

### List projects to find the project ID
```python
curl -H "Authorization: Bearer <TOKEN>" \
  "https://api.vercel.com/v9/projects?limit=10"
# → vehicle-analyzer (id=prj_MZTAfcT0OVs8ZdhNEKqv67i9oesu)
```

### Check existing env vars
```python
curl -H "Authorization: Bearer <TOKEN>" \
  "https://api.vercel.com/v9/projects/<PROJECT_ID>/env"
```

### Set a new env var
```python
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"key":"VPS_SCRAPER_URL","value":"http://VPS_IP_REDACTED:8765","type":"plain","target":["production","preview","development"]}' \
  "https://api.vercel.com/v9/projects/<PROJECT_ID>/env"
```

**Pitfall**: If the env var already exists, POST returns `HTTP 403 ENV_ALREADY_EXISTS`. You must PATCH instead:

```python
# First find the env var ID
envs = GET /v9/projects/<PROJECT_ID>/env
env_id = [e for e in envs if e["key"] == "VPS_SCRAPER_URL"][0]["id"]

# Then PATCH to update
curl -X PATCH -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"value":"http://VPS_IP_REDACTED:8765","type":"plain","target":["production","preview","development"]}' \
  "https://api.vercel.com/v9/projects/<PROJECT_ID>/env/<ENV_ID>"
```

### Trigger a production redeploy
```python
# First get the linked repo info
project = GET /v9/projects/<PROJECT_ID>
# → link.repo, link.repoId, link.productionBranch

# Then trigger deploy with FULL gitSource (repoId is REQUIRED, not optional)
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"vehicle-analyzer","project":"<PROJECT_ID>","target":"production","gitSource":{"type":"github","ref":"main","repoId":1159697116,"repo":"BBridgeers/vehicle-analyzer"}}' \
  "https://api.vercel.com/v13/deployments"
```

**Pitfall**: Omitting `repoId` from `gitSource` returns `HTTP 400 bad_request: gitSource missing required property repoId`. Always include all three fields: `repo`, `repoId`, and `ref`.

## Comma-Separated Multi-Query Search (Cross-Product Pattern)

For sweep/search endpoints that accept a single make/model string, add comma-separation to run multiple targeted searches:

```python
# Parse comma-separated makes and models
makes = (make or '').split(',').map(s => s.trim()).filter(Boolean)
models = (model or '').split(',').map(s => s.trim()).filter(Boolean)

# Build cross-product of all make×model combinations
queries = []
if makes.length > 0 && models.length > 0:
    for m of makes:
        for mo of models:
            queries.push(`${m} ${mo}`)
elif makes.length > 0:
    queries.push(...makes)        # "Toyota", "Honda"
elif models.length > 0:
    queries.push(...models)        # "Camry", "Civic"
else:
    queries.push('')              # broad search

# Execute in parallel — max 3 concurrent to avoid rate limits
chunkSize = 3
for i in range(0, queries.length, chunkSize):
    chunk = queries.slice(i, i + chunkSize)
    results = await Promise.allSettled(
        chunk.map(q => scrapeMarketplace({query: q, maxResults: ceil(20 / queries.length)}))
    )

# Merge and deduplicate by URL
seen = new Set()
for r of results:
    if r.status === 'fulfilled':
        for listing of r.value:
            if listing.sourceUrl && !seen.has(listing.sourceUrl):
                seen.add(listing.sourceUrl)
                merged.push(listing)
```

Update UI placeholders to show comma-separation is supported:
```tsx
placeholder="e.g. Toyota, Honda, Ford"
placeholder="e.g. Camry, Corolla, Civic"
```

## Debugging Failed Logins — Interactive Browser Testing

When the scraper logs show "Still on login page" or "login may have failed" with no other clues, the scraper is a black box. Use interactive browser tools to see exactly what Facebook is showing:

### Pattern: Replay the login flow manually in a real browser

```python
# Step 1: Navigate to where the scraper goes
browser_navigate("https://mbasic.facebook.com/login")
# → Watch the URL — if it redirects to /login?__mmr=1, FB detected the browser

# Step 2: Take a snapshot to see the actual form
browser_snapshot()
# → Shows element refs: textbox "Email" [@e33], textbox "Password" [@e34], button "Log In" [@e35]
# → Verifies selectors match reality: input[name="email"] vs aria-label differences

# Step 3: Fill and submit
browser_type(ref="e33", text="your@email.com")
browser_type(ref="e34", text="yourpassword")
browser_click(ref="e35")

# Step 4: Check result
browser_snapshot()
# → "Find your account and log in." → CREDENTIALS ARE WRONG
# → "two_step_verification" in URL → 2FA IS STILL ENABLED
# → Redirected to marketplace → LOGIN WORKS, scraper has a different problem
```

### What this reveals that logs can't

1. **Credential validity**: "Find your account and log in" means the email/password is wrong. No amount of stealth or proxy work will fix this.
2. **Form layout**: Whether FB is serving combined email+password form vs two-step flow, and actual element types (button vs div[role="button"]).
3. **Redirect behavior**: mbasic→desktop redirect proves User-Agent detection; `?__mmr=1&_rdr` proves datacenter IP flagging.
4. **2FA page content**: Screenshot + browser snapshot shows whether FB wants a code, device confirmation, or "save browser" prompt.

### Stack gap analysis format

When diagnosing "why isn't this working", compare your stack against the recommended scraping stack as a table:

```
COMPONENT              RECOMMENDED                    YOURS                        GAP
───────────────────────────────────────────────────────────────────────────────────
Browser Engine         Playwright                     Playwright ✅                None
Stealth Plugin         playwright-stealth             playwright-stealth ✅        None
Proxy Layer            Rotating Residential           Datacenter ❌                CRITICAL
Session Persistence    Save & reuse cookies           Session store ✅             None
Human-Like             Random scroll, mouse, timing   Basic only ⚠️                MEDIUM
Mobile UA              Mobile user agents             mbasic.facebook.com ✅       None
```

This quickly surfaces that proxies are the #1 blocker when everything else is in place. A datacenter IP will be flagged even with perfect stealth — residential proxies are not optional for Facebook scraping at scale.

## Apify Remote Strategy — The Production Solution

When all DIY strategies fail (common due to Facebook's anti-bot + device trust + datacenter IP detection), the crawlerbros/facebook-marketplace-scraper Apify actor is the reliable production fallback.

### Setup

```python
# apify_strategy.py — standalone module imported by fb_marketplace.py
APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
APIFY_ACTOR = "crawlerbros~facebook-marketplace-scraper"
APIFY_BASE = "https://api.apify.com/v2"

def _start_run(start_urls: list[str], results_per_url: int = 20,
               include_details: bool = True) -> str:
    """Start an Apify actor run. Returns run ID."""
    body = {
        "startUrls": [{"url": u} for u in start_urls],
        "resultsLimit": results_per_url,
        "includeListingDetails": include_details,
        "proxyConfiguration": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"]
        }
    }
    # POST to /v2/acts/{ACTOR}/runs?token={TOKEN}
```

### Cascade Integration

```python
# In fb_marketplace.py strategy list:
strategies = [
    STRATEGY_STEALTH,        # 1. DIY stealth browser
    STRATEGY_FRESH,          # 2. Fresh browser
    STRATEGY_SCRAPLING,      # 3. Scrapling CLI
    STRATEGY_APIFY,          # 4. Apify remote ← PRODUCTION
    STRATEGY_SCREENSHOT,     # 5. Screenshot fallback
]
```

### Cost Model

| Actor | Price | Rating | Users | Notes |
|-------|-------|--------|-------|-------|
| crawlerbros/facebook-marketplace | $1.00/1K results | 5.0★ | 44 | 70+ fields w/ detail enrichment |
| apify/facebook-marketplace | $2.60/1K results | 2.5★ | 6K | Official, mixed reviews |

Typical cost: ~$0.10 per search (~100 listings). Detail enrichment adds ~$0.02 extra.

### Pitfall: URL Double-Query-Param Bug

`_call_apify()` always appended `?token=` to the URL, but dataset endpoints already have `?format=json`:

```python
# BAD — produces ?format=json?token=X (second ? is treated as path)
url = f"{APIFY_BASE}/{endpoint}?token={APIFY_TOKEN}"

# GOOD — detect existing query params
sep = "&" if "?" in endpoint else "?"
url = f"{APIFY_BASE}/{endpoint}{sep}token={APIFY_TOKEN}"
```

Without this fix, `_get_dataset()` returns empty because the token never reaches Apify.

### Pitfall: redacted_description Is a Dict, Not a String

When `includeListingDetails: true`, Apify returns `redacted_description` as `{"text": "seller description here..."}` not a plain string. Calling `.lower()` on it crashes:

```python
# BAD — crashes with 'dict' object has no attribute 'lower'
description = item.get("redacted_description", "")

# GOOD — handle both forms
raw_desc = item.get("redacted_description", "")
description = ""
if isinstance(raw_desc, dict):
    description = raw_desc.get("text", "")
elif isinstance(raw_desc, str):
    description = raw_desc
```

### Apify → VehicleListing Field Mapping

When `includeListingDetails: true`, Apify provides vehicle-specific enriched fields. Map them with fallbacks:

| VehicleListing Field | Apify Source (best first) |
|---------------------|--------------------------|
| make | `vehicle_make_display_name` → parse from title |
| model | `vehicle_model_display_name` → parse from title |
| mileage | `vehicle_odometer_data.value` (dict, int) → parse from subtitles |
| price | `listing_price.amount` (string dollars) |
| fuel_type | `vehicle_fuel_type` → description parsing |
| transmission | `vehicle_transmission_type` → description parsing |
| exterior_color | `vehicle_exterior_color` → `exterior_color` → `attribute_data` |
| interior_color | `vehicle_interior_color` → `attribute_data` |
| condition | `vehicle_condition` → `condition` (root) → `attribute_data` |
| description | `redacted_description.text` (dict) |
| posted_date | `creation_time` (Unix timestamp int) |
| source_url | `listingUrl` → `share_uri` |
| location | `location.reverse_geocode.city` + `.state` |
| seller_name | `marketplace_listing_seller.name` → `vehicle_seller_type` |

**Key quirk**: `listing_price.amount_with_offset_in_currency` is in CENTS (e.g., 600000 = $6,000). Prefer `amount` (dollars) unless you need exact cents.

**Inconsistency warning**: Vehicle enrichment fields (`vehicle_*`) are NOT present on every run. Some runs return only basic fields (title, price, location, subtitles). The mapper must gracefully degrade — parse year/make/model/mileage from title and subtitles when vehicle_ fields are absent.

### Timeout Tuning

Detail enrichment runs take 80-110 seconds. Set `_wait_for_run(timeout_sec=180)` to avoid false timeouts. The FastAPI endpoint wrapping the scraper also needs a generous timeout (200s).

### Systemd Env Var Propagation

Adding `Environment=APIFY_API_TOKEN=...` to `/etc/systemd/system/fb-scraper.service` does NOT take effect until:

```bash
systemctl daemon-reload
systemctl restart fb-scraper
```

Verify with:
```bash
cat /proc/$(systemctl show --property=MainPID --value fb-scraper)/environ 2>/dev/null | tr '\0' '\n' | grep APIFY
```

### Individual Listing Detail Scraping (Dual-Strategy)

When the user pastes a single FB Marketplace listing URL (e.g., `https://www.facebook.com/marketplace/item/1524800349061845/?ref=browse_tab&referral_code=...&tracking=%7B...`), the `scrape_listing_detail()` function handles it with two strategies:

### Strategy 1: Playwright + Session Cookies (free, fast, ~10s)

```python
async def scrape_listing_detail(listing_url: str, session_id: str = "default") -> dict:
    # Step 1: Clean the URL — strip tracking bloat
    cleaned_url = listing_url
    item_match = re.search(r'(facebook\.com/marketplace/item/\d+)', listing_url)
    if item_match:
        cleaned_url = f"https://www.{item_match.group(1)}/"
    # → https://www.facebook.com/marketplace/item/1524800349061845/

    # Step 2: Launch stealth browser with session cookies
    scraper = FBMarketplaceScraper(session_id=session_id, debug=True)
    cookies = scraper.sessions.get(session_id)
    if cookies:
        await scraper.context.add_cookies(cookies)

    # Step 3: Navigate — try network idle first, fall back to domcontentloaded
    try:
        await scraper.page.goto(cleaned_url, wait_until="networkidle", timeout=45000)
    except:
        await scraper.page.goto(cleaned_url, wait_until="domcontentloaded", timeout=30000)

    # Step 4: Check for login wall
    if "login" in scraper.page.url.lower() or "checkpoint" in scraper.page.url.lower():
        raise Exception("FB redirected to login — need authenticated session")

    # Step 5: Extract — try JSON-LD first, fall back to regex
    ld_match = re.search(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    if ld_match:
        ld = json.loads(ld_match.group(1))
        description = ld.get("description", "")
        images = ld.get("image", [])
```

### Strategy 2: Apify Fallback (costs ~$0.01/listing, always succeeds)

If Playwright hits login wall or times out, fall through to Apify:

```python
    except Exception as e:
        print(f"[DETAIL] Playwright strategy failed: {e}", flush=True)

    # Apify fallback
    from apify_strategy import apify_search, map_apify_to_vehicle
    listings = await apify_search(cleaned_url, max_results=1)
    if listings:
        vl = listings[0]
        return {
            "title": vl.title, "price": vl.price, "year": vl.year,
            "make": vl.make, "model": vl.model, "trim": vl.trim,
            "mileage": vl.mileage, "vin": vl.vin,
            "bodyStyle": vl.body_style, "transmission": vl.transmission,
            "fuelType": vl.fuel_type,  # ... all 35+ fields
        }
```

### Pitfall: URL Tracking Blobs

FB Marketplace URLs are typically 500-2000 characters with tracking parameters (`?ref=browse_tab&referral_code=...&tracking=%7B...`). These cause navigation issues. Always clean to just `https://www.facebook.com/marketplace/item/{ID}/` before scraping.

### Pitfall: Non-Vehicle Listings

The detail scraper works for ANY FB Marketplace listing — houses, furniture, etc. It'll extract `title`, `price`, `location`, and `images` regardless. But `year`, `make`, `model`, `mileage` will be null for non-vehicle listings. The scraper returns success even for non-vehicle items — the caller should check for vehicle-specific fields.

### Pitfall: Year Regex Captures Partial Year

When parsing "2017 Kia Sorento", the regex `(19|20)\d{2}` captures ONLY "20" in group(1), not the full "2017". Fix by wrapping the century in a non-capturing group:

```python
# ❌ WRONG — group(1) = "20" not "2017"
ym_match = re.search(r'(19|20)\d{2}\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)', title)
year = int(ym_match.group(1))  # → 20

# ✅ CORRECT — group(1) = "2017"
ym_match = re.search(r'((?:19|20)\d{2})\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)', title)
year = int(ym_match.group(1))  # → 2017
```

### Pitfall: Facebook Branding in og:title and Trim

FB's meta tags include branding suffixes that pollute extracted fields:

- og:title = `"Marketplace - 2017 Kia Sorento · LX Sport Utility 4D | Facebook"`
- og:description is often empty on detail pages
- Trim parsed from title may include `" | Facebook"`

Clean both:
```python
title = re.sub(r'^Marketplace\s*[-–—]\s*', '', title)     # strip prefix
title = re.sub(r'\s*\|\s*Facebook\s*$', '', title).strip() # strip suffix

trim = re.sub(r'\s*\|\s*Facebook\s*$', '', trim).strip()   # also on trim
```

## Pitfall: FB Listing Data Visible Behind Login Popup — Meta Tags Have Everything

**Symptom**: Scraper's `scrape_listing_detail` hits FB, detects login wall (page title "Facebook"), attempts mbasic login (which may fail), and returns `"Could not extract listing data — Facebook may require login for this listing"` — even though the page HTML contains ALL the listing data.

**Root cause**: Facebook Marketplace serves listing data in meta tags AND renders it in the visible page body BEHIND the login popup overlay. The scraper gives up after failed login instead of parsing what it already has. The og:title, og:description, twitter:title/description, and page body `.innerText` all contain the full listing — even for non-logged-in users.

**What data is available WITHOUT login**:
- `document.title` — e.g. "2004 Nissan Pathfinder · XL - Cars & Trucks - Denton, Texas | Facebook Marketplace | Facebook"
- `og:title` — "2004 Nissan Pathfinder · XL"
- `og:description` / `description` — Full seller text with price, mileage, features
- `og:image` — Primary listing photo URL
- `og:url` — Clean listing URL
- Page `body.innerText` — renders ALL listing fields behind the popup: price, mileage, transmission, fuel, exterior/interior color, seller description, location

**Fix — always extract meta tags + body text FIRST, login is optional enhancement**:
```python
# Extract from meta tags (works WITHOUT login)
page_title = await page.title()  # "2004 Nissan Pathfinder · XL - Cars & Trucks - Denton, Texas"
og_title = await page.evaluate("document.querySelector('meta[property=\"og:title\"]')?.content")
og_desc = await page.evaluate("document.querySelector('meta[property=\"og:description\"]')?.content")
meta_desc = await page.evaluate("document.querySelector('meta[name=\"description\"]')?.content")

# Parse visible body text — listing data renders behind login popup
body_text = await page.evaluate("document.body.innerText")
# → "$4,750\nListed 4 days ago in Denton, TX\nDriven 120,000 miles\nAutomatic transmission\nExterior color: Gold · Interior color: Black\nFuel type: Gasoline\n1 owner\nThis vehicle is paid off..." 

# Parse structured fields from body text with regex
price_match = re.search(r'\$([\d,]+)', body_text)
mileage_match = re.search(r'(\d{2,3}(?:,\d{3})*)\s*miles', body_text, re.IGNORECASE)
trans_match = re.search(r'(Automatic|Manual|CVT)\s*transmission', body_text, re.IGNORECASE)
color_match = re.search(r'Exterior color:\s*(\w+)\s*·\s*Interior color:\s*(\w+)', body_text)
fuel_match = re.search(r'Fuel type:\s*(\w+)', body_text, re.IGNORECASE)
```

**Pattern**: Always extract meta tags AND body text FIRST. Only attempt login if the body text is EMPTY (truly gated content). The popup overlay does NOT block text extraction — it's a visual overlay, not a DOM restriction.

See `references/meta-tag-extraction-behind-login-popup.md` for a full extraction example from today's session showing exactly what FB serves to non-logged-in browsers.

## Pitfall: Stale Session Cookies — Login Wall Not Detected (June 2026)

**Symptom**: Every scrape/screenshot returns the same result — the scraper keeps returning empty data (`title: "Facebook"`, no make/model/year/price) even though cookies exist and the `has_valid_session()` check passes.

**Root cause**: Session cookies can be **expired but still present on disk**. The scraper's `SessionManager.has_valid_session()` only checks if cookies exist and are <24h old — it doesn't validate whether the cookies actually authenticate to Facebook. FB Cookies can expire after ~7-10 days of inactivity even if the file timestamp is recent.

When expired cookies are loaded, Facebook does NOT redirect to `/login` — it serves a **generic logged-out homepage** with `title: "Facebook"` and no vehicle data. The login detection in `_navigate_and_scrape` only triggers on `"login" in current_url.lower() or "checkpoint" in current_url.lower()`, which misses this case entirely.

**Detection signal**: The scraper log shows "Landed on: https://www.facebook.com/" (not marketplace, not login) — this is the generic homepage served to expired sessions.

**Fix — two approaches**:

**A) Nuke stale session (immediate)**: Delete the cookies file so the scraper falls through to fresh browser + login strategies:
```bash
rm ~/.fb_scraper_sessions/default/cookies.json
```

**After cookie injection, RESTART the scraper process**: The scraper is a long-running FastAPI service. It loads cookies at startup via `SessionManager`. Simply writing a new `cookies.json` to disk while the scraper is running does NOT take effect — the in-memory cookie state is stale. The process must be killed and restarted:

```bash
kill $(ss -tlnp | grep 8765 | grep -oP 'pid=\K\d+')
cd /root/vehicle-analyzer/scraper
# Export FB credentials for login fallback
export FB_EMAIL=$(grep FB_EMAIL /root/vehicle-analyzer/.env.local | cut -d= -f2)
export FB_PASSWORD=$(grep FB_PASSWORD /root/vehicle-analyzer/.env.local | cut -d= -f2)
python3 server.py &
```

**Verify env vars made it into the new process**:
```bash
cat /proc/$(ss -tlnp | grep 8765 | grep -oP 'pid=\K\d+')/environ | tr '\0' '\n' | grep FB_
```

**Also clear stale __pycache__ on restart**: The scraper imports Python modules that may have been patched. Stale bytecode in `__pycache__` directories will cause old code to run even after source changes:
```bash
find /root/vehicle-analyzer/scraper -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null
```

**B) Patch `_navigate_and_scrape` login detection (permanent)**: Add a check for the generic homepage:
```python
if "login" in current_url.lower() or "checkpoint" in current_url.lower() or \
   "facebook.com/" == current_url.rstrip("/") or \
   "facebook.com/?" in current_url:
    self._log("Detected logged-out state — attempting login...")
    logged_in = await self._attempt_fb_login(self.page, two_factor_code=None)
```

**C) Validate cookies at load time (defense)**: After loading cookies, do a quick `auth_test()` — navigate to `https://www.facebook.com/` and check if the resulting page has `c_user` context:
```python
async def _cookies_are_valid(self) -> bool:
    await self.page.goto("https://www.facebook.com/", wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(2)
    # If cookies are valid, FB redirects to home feed, not generic page
    content = await self.page.content()
    return "c_user" in content or "home" in content.lower()
```

## Verification

```bash
# Test Apify directly
curl -X POST http://localhost:8765/api/scrape/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"Toyota Camry","location":"dallas","max_price":10000,"max_results":5,"prefer_strategy":"apify_remote"}' \
  --max-time 200

# Check logs
journalctl -u fb-scraper --since '2 minutes ago' | grep APIFY
# Expected: [APIFY] Searching: ... → [APIFY] Run started: ... → [APIFY] Got 5 raw items
```

## Pitfall: Images Dropped in Vercel BulkImport/Sweep Pipeline

**Symptom**: Scraper returns 10+ images per listing, but fleet dashboard shows no photos.

**Root cause**: Two gaps in the Vercel-side code:

1. **BulkImport.tsx** — `mappedVehicle` object did not include `images` field. The scraper returned images but the mapping dropped them.
2. **MarketSweepPanel.tsx** — `SweepResult` interface had no `images` field and `handleImportAllToFleet` only sent basic fields.

**Fix**: Add `images` to BulkImport mapping and SweepResult interface. Pass all 35 fields through to fleet API. Fleet API (`...vehicle` spread) stores everything automatically.

**Verification after fix**: Fleet dashboard VehicleCard now renders first image as thumbnail (40h, hover-scale, graceful fallback if image fails).

## End-to-End Workflow

See `references/car-buyer-workflow.md` for the full 5-phase pipeline:
SCRAPE → ANALYZE → FLEET → REVIEW → DECIDE
