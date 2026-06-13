---
name: multi-tier-ai-extraction
description: Multi-tier data extraction pipeline using DOM parsing, vision AI, and text enrichment with merge priority rules. Use when building web scrapers that need AI to fill gaps left by HTML parsing.
version: 1.0.0
---

# Multi-Tier AI Extraction Pipeline

## When to Use

- Building scrapers that extract structured data from web pages
- Pages where HTML/DOM parsing only gets ~30% of desired fields
- Need to fill specification gaps (drivetrain, engine, MPG, etc.) from AI
- Merging data from multiple extraction sources with clear priority rules

## The 3-Tier Architecture

```
Tier 1: DOM / HTML Parsing (meta-tags, JSON-LD, regex)
  fills: title, price, year, make, model, location, images
  priority: HIGHEST - structural data is most reliable from DOM
Tier 2: Vision AI Extraction (screenshot to Groq/OpenAI vision model)
  fills: transmission, fuelType, exteriorColor, bodyStyle, condition*
  priority: MEDIUM - vision can see what DOM can't, but may hallucinate
Tier 3: Text Model Enrichment (year/make/model to known vehicle specs)
  fills: drivetrain, engine, cylinders, MPG, seats
  priority: LOWEST - never overrides data from Tiers 1 or 2
```

## Merge Priority Rules

### `priority_basic` set (Tier 1 fields that DOM is authoritative for):
```python
{"price", "year", "make", "model", "trim", "location",
 "title", "description", "sourceUrl", "source", "scrapedAt", "images"}
```

### Merge logic:
1. Start with Tier 2 (vision) as base
2. Tier 1 overrides: any basic field with a value wins over vision
3. Tier 3 (enrichment) only fills gaps: sets field only if current value is empty/0

### Enrichment mode implementation:
```python
def merge_extraction(basic, vision, is_enrichment=False):
    if is_enrichment:
        # Only fill gaps, never override
        for key, value in vision.items():
            if value and value != 0 and value != "":
                existing = merged.get(key)
                if not existing or existing == "" or existing == 0:
                    merged[key] = value
    else:
        # Vision as base, basic overrides
        merged.update(vision)
        for key, value in basic.items():
            if value and (value != 0 or key == "price"):
                merged[key] = value
```

## Resource Lifecycle: Capture BEFORE Cleanup

**CRITICAL ORDERING RULE:** Any step that uses browser resources must happen BEFORE `_cleanup()`.

```
WRONG:
  html = await page.content()
  await scraper._cleanup()        # browser closed here
  screenshot = await page.screenshot()  # FAILS: page is None

RIGHT:
  html = await page.content()
  screenshot = await page.screenshot()  # capture first
  await scraper._cleanup()              # then close
```

## AI Model Selection

### CRITICAL: `openrouter/free` does NOT reliably filter for vision

As of 2026-05-26, OpenRouter's `openrouter/free` router does NOT consistently route images to vision-capable models. Despite claims that it "detects image payloads," it has been observed routing to `google/gemma-4-26b-a4b-it` (text-only) and returning HTML garbage instead of JSON. Free tier models also appear and disappear without notice (e.g., `google/gemini-2.5-flash-lite` returned 404).

**DO NOT use `openrouter/free` as primary for vision tasks.** Use a specific free vision model ID instead. Keep `openrouter/free` as a secondary fallback with HTML guards.

### Vision models (Tier 2):
| Provider | Model | Notes |
|----------|-------|-------|
| Groq | `meta-llama/llama-4-scout-17b-16e-instruct` | **RECOMMENDED PRIMARY** — 17B vision-capable model on Groq LPUs (hyper-fast). Supports **key pooling**: put multiple API keys in `GROQ_API_KEY_POOL` env var (comma-separated). The pipeline iterates through them in a `for key of keys` loop — if one key returns 401, it tries the next. See `model-provider-intel` skill's `references/groq-key-pool-pattern.md`. |
| OpenRouter | `nex-agi/nex-n2-pro:free` | 262K context, vision-capable. Free tier. Good secondary in cascade when Groq key is depleted. Returns structured JSON. |
| OpenRouter | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 30B MoE, 256K context, vision+reasoning. FREE. Best free-tier vision model from the NVIDIA Nemotron family. Use as the FIRST free-model fallback when Groq is down. |
| OpenRouter | `nvidia/nemotron-nano-12b-v2-vl:free` | Free tier 12B vision-language model, returns clean JSON. Use as third fallback when Groq and the 30B model are both unavailable. The "vl" suffix means vision-language. |
| Anthropic (native) | `claude-fable-5` | Early-access Claude Fable via native Anthropic API. Available for free until June 27-29 2026, then paid credits. Requires `ANTHROPIC_API_KEY` env var + `providers.anthropic` block in `config.yaml`. Access via `/ermie-fable` or `/model claude-fable-5`. |
| OpenRouter | `openrouter/free` | **DO NOT USE FOR VISION** — does NOT filter for vision-capable models. Routed to `google/gemma-4-26b-a4b-it` (text-only) and returned HTML instead of JSON. Use only as last-resort with HTML guard. |
| Ollama | `llama3.2-vision` | Local, no cost. Last-resort fallback. |

### Text enrichment models (Tier 3):
| Provider | Model | Notes |
|----------|-------|-------|
| OpenRouter | `nvidia/nemotron-nano-12b-v2-vl:free` | Same model works for text-only enrichment too. Free. |
| Groq | `llama-3.3-70b-versatile` | Free tier, good for specs. Fallback only. |

### Provider fallback chain (preferred order):
```
Groq Llama 4 Scout (primary, LPU-fast) → Nemotron VL (OpenRouter free) → Ollama (local)
```

### Groq model discovery & pitfalls:
- **Llama 3.2 vision models (`llama-3.2-90b-vision-preview`, `llama-3.2-11b-vision-preview`) were DECOMMISSIONED** — they return "model_decommissioned" errors if still referenced
- **Llama 4 Scout (`meta-llama/llama-4-scout-17b-16e-instruct`) is currently the ONLY vision model on Groq** — it supports images but is not labeled with "vision" in the model ID. Test with a real image to confirm vision support.
- To discover currently-available Groq vision models: `curl -s https://api.groq.com/openai/v1/models -H "Authorization: Bearer $GROQ_API_KEY" | python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin).get('data',[]) if m.get('active')]"` — filter for vision-capable ones. See `references/groq-vision-model-discovery.md`.
- Groq model IDs require `meta-llama/` prefix for Llama models
- Groq API keys can expire — test a key with a simple text request before deploying vision pipeline changes

### Testing vision models before deploying:
ALWAYS test a model with a known image and structured JSON output before wiring it into production. Free tier models change frequently — decommissioning, rate limiting, and model swaps happen without notice. See `references/groq-vision-model-discovery.md` for the Groq-specific test pattern.

Free tier models change frequently. Test candidates with a known image and JSON output requirement (see `references/free-vision-model-testing-2026-05-26.md` for results from the last testing session).

```python
import os, asyncio, json, aiohttp, base64

# 1x1 red PNG for testing
TEST_PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==')

async def test_model(model_id, label):
    KEY = os.environ.get('OPENROUTER_API_KEY', '')
    b64 = base64.b64encode(TEST_PNG).decode()
    payload = {
        'model': model_id,
        'messages': [{'role': 'user', 'content': [
            {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{b64}'}},
            {'type': 'text', 'text': 'Return ONLY JSON: {"make":"toyota","model":"camry","year":2020}'}
        ]}],
        'temperature': 0.1, 'max_tokens': 200,
    }
    headers = {'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'HTTP-Referer': 'https://example.com'}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        async with session.post('https://openrouter.ai/api/v1/chat/completions', json=payload, headers=headers) as resp:
            data = await resp.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            actual_model = data.get('model', '?')
            is_html = content.strip().startswith('<')
            is_json = content.strip().startswith('{')
            print(f'{label:25s} -> status={resp.status} | html={is_html} | json={is_json} | model={actual_model}')
            return is_json and not is_html
```

Run against candidates: `nvidia/nemotron-nano-12b-v2-vl:free`, `openrouter/free`, `google/gemini-2.5-flash-lite:free`, `qwen/qwen2.5-vl-7b-instruct:free`, etc. Pick the one that returns 200 + JSON.

### Groq → OpenRouter migration pattern:
When Groq API keys die (common — they expire or get rate-limited), the fix is to flip the pipeline:
1. Add `OPENROUTER_API_KEY` to `.env.local` / systemd EnvironmentFile
2. Make a specific free vision model the primary (NOT `openrouter/free` — see above)
3. Keep Groq as tertiary fallback — don't remove it, just demote
4. Add `HTTP-Referer` and `X-Title` headers to OpenRouter calls (required by their API ToS)

### Common pitfalls:
- Groq model IDs require `meta-llama/` prefix
- Llama models don't consistently support `response_format: { type: "json_object" }` — rely on prompt instructions instead
- Missing `aiohttp` dependency: `pip3 install aiohttp --break-system-packages`
- `openrouter/free` does NOT reliably filter for vision-capable models — use a specific free vision model ID
- Free tier models disappear without notice — test candidates before deploying
- OpenRouter API requires `HTTP-Referer` and `X-Title` headers on requests — missing headers don't cause auth errors but are a ToS violation

### Free model cascade pattern:
Don't rely on a single free vision model. Free models go down without notice (rate limits, decommissioning, temporary outages). Always try 3+ in sequence. Break out on first success. Log which model succeeded:

```typescript
const FREE_VISION_MODELS = [
  'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free',
  'nvidia/nemotron-nano-12b-v2-vl:free',
  'nex-agi/nex-n2-pro:free',
];
for (const model of FREE_VISION_MODELS) {
  try {
    const res = await fetch('https://openrouter.ai/api/v1/chat/completions', { ... });
    if (res.ok) { /* extract, break */ }
  } catch (e) { /* log, continue */ }
}
```

### Form clearing on extraction failure:
When extraction returns empty/null data, ALWAYS clear the frontend form state. Otherwise stale vehicle data silently persists — user sees the old vehicle even after pasting a different URL. The `setForm((f) => ({...f, ...v}))` pattern preserves old values when `v` has empty fields:

```typescript
// BAD — old values persist when v is empty
setForm((f: any) => ({ ...f, ...v }));

// GOOD — explicitly clear on failure
if (!v.make && !v.model && !v.price && !v.year) {
  setForm((f: any) => ({ ...f, make: '', model: '', year: '', price: '', mileage: '', vin: '' }));
  setError('Could not extract vehicle data');
  return;
}
```

## Frontend Field Mapping Discipline

**WHEN API returns new fields, the frontend MUST explicitly map them to form state.**

Every handler that calls an extraction API needs a field-to-form mapping block:
```typescript
setForm((f: any) => ({
  ...f,
  ...v,                          // spread all API fields
  // Explicit remaps with fallbacks:
  price: v.price ? String(v.price) : f.price,
  mileage: v.mileage ? String(v.mileage) : f.mileage,
  exteriorCondition: v.conditionExterior || v.exteriorCondition || f.exteriorCondition,
  mechanicalCondition: v.conditionMechanical || v.mechanicalCondition || f.mechanicalCondition,
  notableDamage: v.notableDamage || f.notableDamage,
  // ... every API field that maps to a form field
}));
```

### Anti-pattern to watch for:
```typescript
// BUG: API returns { success: true, vehicle: { exteriorCondition: "..." } }
// but component reads:
const data = await res.json();
allExtractions.push(data);  // data is { success, vehicle }
// Later:
if (extraction.exteriorCondition) ...  // undefined! Should be extraction.vehicle.exteriorCondition
```

**Check the actual API response shape before writing the consumer.** The `vehicle` key wrapping is easy to miss because nothing errors — fields just silently don't populate.

## Prompt Engineering for Extraction

### DO use empty/zero defaults (prevents model from copying placeholder text):
```json
{ "transmission": "", "fuelType": "", "drivetrain": "", "engine": "" }
```
NOT: `{ "transmission": "Automatic, Manual, or CVT", ... }` — model may copy the hint text.

### DO strip markdown code fences AND control characters AND guard against HTML:

```typescript
// sanitizeJson helper — call BEFORE JSON.parse on any LLM response
const sanitizeJson = (raw: string): string => {
    let s = raw.trim();
    // 1. Strip markdown code fences
    s = s.replace(/```(?:json)?\s*/g, '').replace(/```/g, '');
    // 2. Strip bad ASCII control characters that break JSON.parse
    //    (keeps \n=0x0A, \r=0x0D, \t=0x09 — valid in JSON)
    s = s.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '');
    return s.trim();
};

// 3. Guard against HTML responses (free tier models sometimes return error pages)
if (content && !content.trim().startsWith('<')) {
    const parsed = JSON.parse(sanitizeJson(content));
    // ... use parsed
} else if (content) {
    // Model returned HTML — treat as failure, fall to next strategy
    lastError = 'Model returned HTML/error response';
}
```

**Why this is necessary**: Free tier models sometimes return unescaped control characters inside JSON strings (e.g., raw newlines, tabs, null bytes from internal tokenization) that cause `JSON.parse` to throw. Worse, some free router models don't support vision at all and return HTML error pages. Both failures are silent — the JSON parse error message is cryptic without sanitization. The HTML guard prevents HTML from being fed to `JSON.parse` (produces "Unexpected token '<'" errors).

Python equivalent:
```python
import re

def sanitize_json(raw: str) -> str:
    s = raw.strip()
    # Strip markdown fences
    s = s.replace('```json', '').replace('```', '')
    # Strip bad control characters (keep \n, \r, \t)
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)
    return s.strip()

# HTML guard
if content and not content.strip().startswith('<'):
    parsed = json.loads(sanitize_json(content))
elif content:
    print('[VISION] Model returned HTML/error response')
```

### DO NOT use `response_format: json_object` with Llama models — not consistently supported.

### DO strip markdown code fences from response:
```python
content = content.strip()
if content.startswith("```"):
    content = content.split("\n", 1)[1] if "\n" in content else content[3:]
    if content.endswith("```"):
        content = content[:-3]
```

## Verification Checklist

After building a multi-tier pipeline, verify:
- [ ] Tier 1 (DOM) populates structural fields (title, price, year, make, model)
- [ ] Tier 2 (vision) populates visible specs (transmission, fuelType, color)
- [ ] Tier 3 (enrichment) fills known gaps (drivetrain, engine, MPG, seats)
- [ ] Enrichment never overrides vision or DOM data
- [ ] Frontend maps ALL fields with `||` fallback chains
- [ ] Browser resources captured before `_cleanup()`
- [ ] No `response_format: json_object` with Llama models
- [ ] Model names have correct provider prefix
