# Photo-Based Vehicle Analysis Pipeline

## Overview

Three analysis flows that automatically extract vehicle data from photos:

1. **Photo-only detection** — Upload photos → click "Run AI Analysis" → VERA identifies make/model/year from photos, THEN runs full analysis
2. **Screenshot + photos combined** — Paste listing screenshot while photos are uploaded → everything analyzed together
3. **Condition extraction** — Both flows now extract detailed condition data (exterior, interior, mechanical) from photos

## API Endpoints

### `/api/analyze-photos` (NEW — 2026-05-26)

Takes multiple vehicle photos, returns vehicle identity + condition assessment.

**Request**: `POST multipart/form-data`
- `photo0`, `photo1`, ... `photoN` — vehicle image files
- Can send up to 10+ photos

**Response**: JSON with identity fields + condition fields
```json
{
  "success": true,
  "vehicle": {
    "year": 2018,
    "make": "Toyota",
    "model": "Camry",
    "trim": "XLE",
    "bodyStyle": "Sedan",
    "exteriorColor": "Silver",
    "interiorColor": "Black",
    "confidence": "high",
    "notes": "Identified by front grille design and rear badging",
    "conditionExterior": "Minor scratches on hood...",
    "conditionInterior": "Driver seat bolster shows wear...",
    "conditionMechanical": "Engine bay clean, no visible leaks...",
    "notableDamage": "Small dent on passenger door",
    "overallImpression": "Good"
  }
}
```

**Prompt strategy**: The vision model is asked to do BOTH identification and condition assessment in one call. The prompt has two clearly separated parts (PART 1: Identification, PART 2: Condition) with specific, detailed instructions for what to look for in each condition category.

### `/api/extract-listing` (MODIFIED — 2026-05-26)

Now accepts additional `photo0`, `photo1`, ... fields alongside the `image` (screenshot) field. If photos are present:
- They're appended to the vision model request after the screenshot
- The prompt is enhanced with "ADDITIONAL VEHICLE PHOTOS" instructions
- The model is told to analyze photos for conditionExterior, conditionInterior, conditionMechanical, notableDamage, overallImpression
- `buildImageContents()` helper builds the combined image array

## Frontend Flow

### Auto-detect from photos (page.tsx `handleRunAnalysis`)

```typescript
// If no make/model but photos exist → detect first
if ((!currentMake || !currentModel) && photos.length > 0) {
  // Send photos to /api/analyze-photos
  // Populate form with detected make/model/year/trim/colors
  // ALSO populate condition fields: exteriorCondition, interiorCondition, mechanicalCondition
  // Then continue with full analysis using detected data
}
```

### Screenshot + photos combined (page.tsx `processScreenshot`)

```typescript
// When sending screenshot to /api/extract-listing
photos.forEach((p, i) => formData.append(`photo${i}`, p.file));
// Vision model receives ALL images and analyzes everything together
```

### Button disabled logic (VehicleForm.tsx)

Changed from requiring make+model+year to only requiring those if no photos are present:
```tsx
disabled={isLoading || (!form.year && !form.make && !form.model && !hasPhotos) || !form.price}
```

## Condition Field Mapping

The API responses use camelCase field names, which are mapped to form field names in the frontend:

| API Field | Form Field |
|---|---|
| `conditionExterior` | `exteriorCondition` |
| `conditionInterior` | `interiorCondition` |
| `conditionMechanical` | `mechanicalCondition` |
| `notableDamage` | `notableDamage` |
| `overallImpression` | `overallImpression` |

These populate the condition text boxes in the main evaluation form and feed into the vehicle score.

## Files Modified (2026-05-26)

| File | Change |
|---|---|
| `src/app/api/analyze-photos/route.ts` | NEW — photo-based vehicle identification + condition |
| `src/app/api/extract-listing/route.ts` | Added photo collection, `buildImageContents()`, enhanced prompt |
| `src/components/VehicleForm.tsx` | Added `hasPhotos` prop, relaxed button disabled logic |
| `src/app/page.tsx` | Auto-detect flow in `handleRunAnalysis`, photos in `processScreenshot`, condition field mapping |
