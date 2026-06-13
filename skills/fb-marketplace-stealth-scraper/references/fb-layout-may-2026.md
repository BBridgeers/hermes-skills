# FB Marketplace Layout Change — May 2026

## What Changed

FB Marketplace listing cards now serve ALL fields concatenated into a single text blob with ZERO whitespace separators between fields.

## Before (old layout — separated fields)
```
$7,100  2004  Toyota  4runner  SR5 Premium  Lewisville, TX  158K miles
```
Each field in its own DOM element, regex could match individually.

## After (new layout — concatenated)
```
$7,1002004 Toyota 4runner SR5 Premium Sport Utility 4DLewisville, TX158K miles
```

## Test Data (live scrapes from May 26-27, 2026)

```
"$7,1002004 Toyota 4runner SR5 Premium Sport Utility 4DLewisville, TX158K miles"
"$7,7882025 Toyota 4runner i-force max trd pro 4x4Dallas, TX5.2K miles"
"$2,500$3,0002002 Toyota 4runner SR5 Sport Utility 4DDallas, TX301K miles"
"$12,5002015 Toyota 4runner SR5 Premium Sport Utility 4DDallas, TX119K miles"
"$5,0002024 Toyota 4runner Limited Sport Utility 4DDallas, TX21K miles"
```

## Extraction Results (before fix → after fix)

| Field | Before | After |
|-------|--------|-------|
| price | 0 | 7100 |
| year | None | 2004 |
| make | "" | Toyota |
| model | "" | 4runner |
| trim | "" | SR5 |
| mileage | None | 158000 |
| location | "" | Lewisville, TX |
| bodyStyle | "" | SUV |

## Key Observations

1. **Dual prices**: Some listings show "$2,500$3,000" — original + reduced price
2. **Trim→Location concatenation**: "4DLewisville" — "4D" is the body style suffix, runs into city name
3. **Location→Mileage concatenation**: "TX158K" — state code runs into mileage
4. **"5.2K miles"**: Some listings use decimal K notation instead of raw numbers
5. **"i-force max"**: Toyota's hybrid trim appears before TRD Pro in text

## Seller Rating Extraction

FB embeds seller data in `application/json` script tags under `marketplace_listing_seller`:

```json
{"marketplace_listing_seller": {"name": "John D.", "rating": 4.8}}
```

Auto red-flag thresholds:
- rating < 3.0: "CRITICAL: Very low seller rating"
- rating < 3.5: "Low seller rating"
