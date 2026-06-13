# Vision Provider Swap — Groq ↔ OpenRouter

Both providers serve `meta-llama/llama-4-scout-17b-16e-instruct` with identical
OpenAI-compatible APIs. When one key dies, swap to the other with minimal changes.

## Affected Files

| File | Endpoint |
|---|---|
| `src/app/api/extract-listing/route.ts` | Screenshot extraction (primary) |
| `src/app/api/analyze-photos/route.ts` | Photo-based vehicle identification |

## Swap Pattern (Groq → OpenRouter)

In each endpoint, change three things:

### 1. API URL
```
Groq:     https://api.groq.com/openai/v1/chat/completions
OpenRouter: https://openrouter.ai/api/v1/chat/completions
```

### 2. Auth Header + OpenRouter Headers
```typescript
// Groq:
headers: {
    'Authorization': `Bearer ${groqKey}`,
    'Content-Type': 'application/json',
}

// OpenRouter:
headers: {
    'Authorization': `Bearer ${orKey}`,
    'Content-Type': 'application/json',
    'HTTP-Referer': 'https://veracar.co',
    'X-Title': 'veracar.co Vehicle Analyzer',
}
```

### 3. Key Variable
```typescript
// Groq:
const groqKey = process.env.GROQ_API_KEY;

// OpenRouter:
const orKey = process.env.OPENROUTER_API_KEY;
```

Everything else stays the same — model ID, temperature, max_tokens, message format.

## Reverting (OpenRouter → Groq)

Same changes in reverse. No structural diffs.

## Provider Health Check

```bash
# Groq
curl -s https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer *** >&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print('DEAD' if 'error' in d else f'LIVE: {len(d.get(\"data\",[]))} models')"

# OpenRouter
curl -s https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer *** >&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print('LIVE' if 'data' in d else 'DEAD')"
```

## Session Example (2026-06-12)

Both Groq keys returned `"Invalid API Key"`. Swapped to OpenRouter in both endpoints.
Build passed. User provided new Groq key — reverted code and restored Groq as primary.
The swap was clean both ways because the model is identical across providers.

## Ollama Fallback

When both cloud providers fail, the Ollama fallback (`OllamaVisionEngine`) attempts
local extraction. This requires Ollama to be running on the VPS — it typically is not.
The fallback exists as a placeholder but has never been used in production.
