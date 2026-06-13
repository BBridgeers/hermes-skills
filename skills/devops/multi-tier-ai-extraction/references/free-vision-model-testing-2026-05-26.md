# Free Vision Model Testing — 2026-05-26

## Test Results

Tested on OpenRouter free tier with a 1x1 red PNG and JSON output prompt.

| Model ID | Status | Content | Verdict |
|---|---|---|---|
| `nvidia/nemotron-nano-12b-v2-vl:free` | 200 | `{"make":"toyota","model":"camry","year":2020,"color":"red"}` | ✅ WORKS — returns valid JSON, vision-capable |
| `google/gemini-2.5-flash-lite:free` | 404 | (empty) | ❌ GONE — no longer on free tier |
| `qwen/qwen2.5-vl-7b-instruct:free` | 400 | (empty) | ❌ FAILED — bad request |
| `openrouter/free` | 200 | routed to `google/gemma-4-26b-a4b-it:free` (non-vision) | ❌ UNRELIABLE — does not filter for vision capability |

## openrouter/free Router Behavior

The `openrouter/free` router was tested twice:
1. First call → `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` (reasoning model, no vision)
2. Second call → `google/gemma-4-26b-a4b-it:free` (text-only)

**Conclusion**: The free router does NOT reliably detect image payloads and route to vision-capable models. Use a specific model ID instead.

## Actual User Errors Observed

When `openrouter/free` was primary:
- "Bad control character in string literal in JSON at position 62" — unescaped control chars from LLM output
- "Unexpected token '<', \"<html> <h\"... is not valid JSON" — model returned HTML error page instead of JSON
- 404 from Gemini Flash Lite — model removed from free tier without notice
- 401 from Groq — API key expired (`invalid_api_key`)

## Fix Applied

- Primary: `nvidia/nemotron-nano-12b-v2-vl:free` (confirmed working)
- Fallback: `openrouter/free` with HTML guard
- Tertiary: Groq (if key works)
- Last resort: Ollama local
- All `JSON.parse` calls wrapped with `sanitizeJson()` helper (control chars + HTML guard)
