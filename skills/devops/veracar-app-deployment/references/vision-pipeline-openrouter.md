# Vision Pipeline — Model Routing Behavior

## OpenRouter `openrouter/free` Router

The free router auto-selects from available free models based on request payload. When an image is included, it prefers vision-capable models but does NOT guarantee vision — it may route to reasoning/text models that ignore the image.

### Test Results (2026-05-26)

| Model Called | Actually Routed To | Vision Result |
|---|---|---|
| `openrouter/free` (1st attempt) | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | ❌ No response (model ignored image) |
| `openrouter/free` (2nd attempt) | `nvidia/nemotron-nano-12b-v2-vl:free` | ✅ Correctly identified red pixel |
| `google/gemini-2.5-flash-lite` | `google/gemini-2.5-flash-lite` | ✅ Responded, confused about color |
| `openrouter/free` (text-only) | `openai/gpt-oss-120b:free` | ✅ Correct (4) |

### Recommendation

Use `openrouter/free` as primary with Groq as fallback. The router usually picks a vision-capable model on retry. For production reliability, a specific model like `google/gemini-2.5-flash-lite` is more deterministic but `openrouter/free` provides free tier resilience across multiple providers.

## Files Modified (2026-05-26)

| File | Change |
|---|---|
| `src/app/api/extract-listing/route.ts` | OpenRouter primary, Groq secondary |
| `scraper/vision_extractor.py` | Added `extract_with_openrouter_vision()`, `_call_openrouter_api()`, `_call_openrouter_text()` |
| `scraper/fb_marketplace.py` | OpenRouter first, Groq fallback |
| `src/lib/vision-engine.ts` | Added `OpenRouterVisionEngine` class |
| `scripts/fb_subagent.ts` + `at_subagent.ts` | Pass `openRouterKey` to VisionManager |
| `.env.local` | Added `OPENROUTER_API_KEY` |

## Required Environment Variables

```
OPENROUTER_API_KEY=sk-or-v1-...    # Primary vision provider
GROQ_API_KEY=gsk_...               # Optional legacy fallback
```

## API Endpoints

- **OpenRouter**: `https://openrouter.ai/api/v1/chat/completions`
  - Headers: `Authorization: Bearer <key>`, `HTTP-Referer: https://www.veracar.co`, `X-Title: Vehicle Analyzer Pro`
  - Model: `openrouter/free`
- **Groq (fallback)**: `https://api.groq.com/openai/v1/chat/completions`
  - Model: `meta-llama/llama-4-scout-17b-16e-instruct` (vision), `llama-3.3-70b-versatile` (text)
