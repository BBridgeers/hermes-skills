# Veracar.co — Bulk Import Photo Gap

## Current State

The VPS scraper returns images in detail responses (10+ photos per listing). But the veracar.co frontend drops them at two points:

### Gap 1: BulkImport.tsx (line 98-120)
`/api/import-url` → `FacebookMarketplaceScraper.scrape()` → returns images ✓
`BulkImport.handleUrlImport()` → maps to Vehicle → **drops images** ✗

The `mappedVehicle` object has no `images` field.

### Gap 2: MarketSweepPanel.tsx (line 137-167)
`handleImportAllToFleet()` iterates results one-by-one, sending only:
```json
{"name","year","make","model","price","miles","sourceUrl","source","location","status"}
```
No images. No batch processing. Each vehicle is a separate POST to `/api/fleet`.

### Gap 3: SweepResult Interface (line 6-16)
```typescript
interface SweepResult {
  source: string; title: string; price: number | null;
  mileage: number | null; year?: number; make?: string;
  model?: string; location?: string; url: string; scraped_at: string;
}
```
No `images` field — images are lost before they reach the sweep pipeline.

## Fix Needed

1. Add `images` to `SweepResult` interface
2. Pass images through sweep pipeline to results
3. Add `images` to `BulkImport` mappedVehicle
4. Send images with fleet POST requests
5. Batch fleet imports instead of one-at-a-time loop
