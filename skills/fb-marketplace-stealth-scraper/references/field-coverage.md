# FB Marketplace — Field Coverage Report (May 2026)

## Search Cards (regex/DOM parser)
11/35 fields captured from listing card text blobs:
- title, year, make, model, trim, price, mileage, location, source_url, body_style, images

## Detail Page (meta tags + JSON + DOM)
24/35 fields captured from individual listing detail scrape:
All search card fields + description, posted_date, title_status, transmission, fuel_type, drivetrain, engine, cylinders, exterior_color, interior_color, seats, mpg, num_owners, paid_off

ALL listing images (fbcdn.net) captured — not just og:image.

## Never Captured (filled by veracar.co analysis phase)
- condition, condition_exterior, condition_interior, condition_mechanical → Vision AI from photos
- safety_rating → NHTSA API lookup by year/make/model
- vin → Not in FB listings (privacy-redacted)
- seller_name, seller_responsiveness, seller_transparency → May be available in seller JSON
- seller_red_flags → Auto-set when seller rating extracted and < 3.5
- seller_quotes → Manual/LLM analysis of description text

## Separation of Concerns
| Phase | System | Fields |
|-------|--------|--------|
| Data pipe | fb_marketplace.py scraper | All FB-available fields + all photos |
| Analysis | veracar.co | Vision condition scoring, NHTSA safety, seller intel |
