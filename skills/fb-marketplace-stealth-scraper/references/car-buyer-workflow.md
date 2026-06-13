# Car Buyer — Complete Workflow Reference

## End-to-End Pipeline

```
SCRAPE → ANALYZE → FLEET → REVIEW → DECIDE
  ↓         ↓         ↓        ↓        ↓
Find all  Auto-run  All land  Delete   Get in car
listings  veracar   in dash   or keep  tomorrow
```

## Phase 1 — Scrape (VPS)

### Search (listing cards — 11 fields)
```bash
curl -X POST http://127.0.0.1:8765/api/scrape/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"Toyota 4Runner, Honda Pilot","location":"dallas","max_price":15000,"max_results":20}'
```
Captures: price, year, make, model, trim, mileage, location, bodyStyle, sourceUrl, first image, source

### Detail (single listing — 24 fields + all photos)
```bash
curl -X POST http://127.0.0.1:8765/api/scrape/detail \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://www.facebook.com/marketplace/item/<ID>/","session_id":"default"}'
```
Captures: ALL above + description, postedDate, titleStatus, ALL 10+ images, transmission, fuelType, drivetrain, engine, cylinders, exteriorColor, interiorColor, seats, mpg, sellerName, numOwners, paidOff, seller rating → red flags

## Phase 2 — Analyze (veracar.co Auto)

Every scraped listing auto-processes through veracar:
1. Vision analysis on all listing photos (exterior/interior/mechanical condition)
2. Market valuation vs KBB/NADA
3. NHTSA safety rating lookup
4. Red flag scan (salvage title, frame damage, seller rating < 3.5)

## Phase 3 — Fleet Dashboard

All results land at veracar.co/fleet with:
- Photo thumbnail on each card
- Price, mileage, location, score
- Delete button for quick rejection
- Compare mode for side-by-side

## Delete Immediately If
- Price > budget ceiling
- Mileage > your threshold
- Red flags: salvage, frame damage, "needs work"
- Wrong: not 4WD when you need 4WD
- Gut feel: something's off

## Key Commands
```bash
systemctl restart veracar-scraper    # restart scraper
journalctl -u veracar-scraper -n 30  # view scraper logs
systemctl restart veracar-app        # restart veracar
curl http://127.0.0.1:8765/api/scrape/health     # health check
curl http://127.0.0.1:8765/api/scrape/sessions   # cookie status
```

## Key Files
| Path | Purpose |
|------|---------|
| /root/vehicle-analyzer/scraper/fb_marketplace.py | Core scraper (1862 lines, v2 parser) |
| /root/vehicle-analyzer/scraper/server.py | FastAPI server |
| /root/vehicle-analyzer/src/components/BulkImport.tsx | URL import + fleet ingest |
| /root/vehicle-analyzer/src/components/MarketSweepPanel.tsx | Sweep panel + bulk import |
| ~/.fb_scraper_sessions/default/cookies.json | FB auth cookies |
