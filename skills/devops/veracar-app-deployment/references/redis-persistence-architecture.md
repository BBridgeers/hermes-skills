# Redis Persistence Architecture — veracar.co (2026-05-27)

## Hard Rule: ALL State Goes Through Upstash Redis

The user was emphatic: "EVERYTHING SHOULD PERSIST, EVERYTHING SHOULD BE WIRED TO REDIS... everything is wired to upstash Redis everything persists everything is reclaimable." Nothing lives in `localStorage`. Nothing lives only in React state. Redis is the universal persistence layer.

## Redis Keys (user-scoped: `{userId}:*`)

| Key | Content | API Route |
|---|---|---|
| `{userId}:fleet` | Fleet array with vehicles + nested analysis | `/api/fleet` |
| `{userId}:analysis` | Latest analysis result `{vehicle, result, timestamp}` | `/api/analysis` |
| `{userId}:last_form` | Last form state for restoration | `/api/analysis/form` |

## Form Persistence (Replaced localStorage)

Before this session, form state was saved to `localStorage.setItem('vera_last_form', ...)`. This was wrong — localStorage doesn't survive across devices, can't be shared with the chatbot, and violates the Redis rule.

Now: `/api/analysis/form` (GET/POST) stores form state in Redis under `{userId}:last_form`. On page mount, if `form.make` is empty, the form restores from Redis.

## History Click → Full Repopulation

When clicking a vehicle in the sidebar "Analysis History":
1. `handleHistoryClick(idx)` fetches `/api/fleet` (Redis)
2. Finds `fleet[idx]` — all vehicle fields + nested `.analysis`
3. Calls `setForm()` with ALL fields mapped from the fleet entry
4. Calls `setAnalysisResult()` to populate the right panel
5. Calls `setChatMessages()` to notify VERA

This makes the entire evaluation page reclaimable from Redis alone.

## Data Flow: Scraper → Form → Analysis → Fleet

```
FB Scraper (VPS :8765)
  ↓ POST /api/import-url
QuickImportSection.setForm()
  ↓ form.images = v.images (three-point chain)
onRunAnalysis()
  ↓ builds Vehicle with images: form.images || []
  ↓ POST /api/analysis (saves {vehicle, result} to Redis)
  ↓ POST /api/analysis/form (saves form to Redis)
  ↓ router.push('/analysis')
Analysis Page
  ↓ GET /api/analysis (reads from Redis)
  ↓ "Add to Fleet" → POST /api/fleet (saves vehicle + analysis to Redis)
  ↓ GET /api/fleet (history sidebar reads from Redis)
```
