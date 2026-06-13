# Multi-Source Lead CSV Enrichment & Scoring

Pattern for taking 2+ existing lead data files (hit lists, scraped data, enriched exports) and assembling them into a single master CSV with deduplication, computed columns, and priority scoring.

## When to Use

- You have leads in multiple files/CSVs and need one master list
- You need to cross-reference which businesses appear in multiple lists
- You need to enrich leads with computed fields (website_status from rationale text, priority scores)
- One list contains data another is missing (e.g., cities added in a later run)

## Pattern

### Step 1: Normalize & deduplicate each source

Use Python DictReader. Lowercase business names for dedup keys. When a source has duplicate rows for the same business (common in scraped data where one row has `Unknown` phone and another has the real number), read ALL rows first, collect the best phone, then dedup:

```python
# BAD: dedup on first-seen (may capture Unknown phone)
if key in seen: continue
seen.add(key)

# GOOD: pre-scan for best phone, then dedup
phones = {}
for row in all_rows:
    if row['phone'] and row['phone'] != 'Unknown':
        phones[key] = row['phone']

# Then use phones[key] when writing the deduped master record
```

### Step 2: Cross-reference across sources

Compute set intersections to understand overlap:

```python
all_a = set(source_a.keys())
all_b = set(source_b.keys())
shared = all_a & all_b
only_a = all_a - all_b
only_b = all_b - all_a
```

If two sources are the SAME list (e.g., 65/67 overlap), use the richer one as primary and merge non-overlapping entries from the other.

### Step 3: Add computed columns

Derive columns from existing text fields. Example — `website_status` from rationale:

```python
if 'Ghost' in list_type or 'no website' in rationale.lower():
    website_status = 'Ghost'
elif 'Renovation' in list_type or 'outdated' in rationale.lower():
    website_status = 'Has Website (Needs Renovation)'
elif 'no online' in rationale or 'no booking' in rationale:
    website_status = 'Ghost'
else:
    website_status = 'Unknown'
```

And `confidence_level` from source trustworthiness:

```python
if list_type.startswith('List A') or list_type.startswith('List B'):
    confidence = 'High (Verified Ghost)'
elif owner_found == 'Yes':
    confidence = 'High (Owner Enriched)'
else:
    confidence = 'Medium (Phone Verified)'
```

### Step 4: Compute a priority/promise score

Weighted multi-factor scoring to surface the most promising leads. Define an affinity dictionary (e.g., city_affluence mapping) and add/subtract for each factor:

```python
affluent_cities = {'Westlake': 10, 'Southlake': 9, 'Trophy Club': 8, ...}

score = 0
if has_phone:     score += 20
if is_ghost:      score += 15
if city in affluent_cities: score += affluent_cities[city] * 2
if industry in emergency_trades: score += 10
if 'emergency' in name or '24/7' in name: score += 15
if 'List A' in list_type or 'List B' in list_type: score += 10
```

### Step 5: Sort by score and write master CSV

```python
sorted_master = sorted(master.items(), key=lambda x: x[1]['score'], reverse=True)
with open('MASTER_ENRICHED.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'phone', 'city', 'industry', 'website_status',
                     'owner_name', 'owner_found', 'confidence_level', 'promise_score'])
    for k, v in sorted_master:
        writer.writerow([v['name'], v['phone'], v['city'], v['industry'],
                         v['website_status'], v['owner_name'], v['owner_found'],
                         v['confidence_level'], v['promise_score']])
```

### Step 6: Handle enrichment failures gracefully

When owner name lookups fail (all search providers down), do NOT hold up the CSV. Flag with `owner_found = "No (search unavailable)"` and create the file. The column acts as a retry queue for a follow-up run.

## Pitfalls

- **First-row Unknown phone**: Scraped CSVs often have `Unknown` in the first row and the real number in later rows for the same business. Always pre-scan for the best available phone before dedup.
- **Name normalization mismatches**: `"24/7 Emergency Plumbing DFW"` vs `"Emergency Plumbing DFW"` — lowercase and strip is usually enough, but check `monday_not_enriched` and `enriched_not_monday` sets for edge cases.
- **Over-deletion**: Don't drop a source just because it overlaps heavily. Non-overlapping entries still need to be merged.
