# Free Vision Model Migration — OpenRouter

When a provider API key (Groq, OpenAI, etc.) dies and the app depends on vision/image extraction, swap to a free OpenRouter model without changing the extraction logic.

## Discovery

Query OpenRouter's models API and filter for free + vision-capable:

```bash
curl -s https://openrouter.ai/api/v1/models | python3 -c "
import sys, json
models = json.load(sys.stdin).get('data', [])
for m in models:
    pricing = m.get('pricing', {})
    prompt_p = float(str(pricing.get('prompt','0')).replace('\$',''))
    comp_p = float(str(pricing.get('completion','0')).replace('\$',''))
    is_free = prompt_p == 0 and comp_p == 0
    arch = m.get('architecture', {})
    inputs = arch.get('input_modalities', []) or []
    has_vision = 'image' in str(inputs).lower() or 'vision' in str(inputs).lower()
    if is_free and has_vision:
        print(f\"{m['id']} | inputs: {inputs} | ctx: {m.get('context_length','?')}\")
"
```

## Free vision models (2026-06-12)

| Model ID | Params | Context | Notes |
|---|---|---|---|
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 30B MoE | 256K | Best all-around: vision+reasoning, omni-modal (text/audio/image/video), NVIDIA |
| `google/gemma-4-31b-it:free` | 31B | 262K | Google — user explicitly hates Google/Gemini. DO NOT USE. |
| `google/gemma-4-26b-a4b-it:free` | 26B MoE | 262K | Google — same restriction. |
| `nvidia/nemotron-nano-12b-v2-vl:free` | 12B | 128K | Smaller, NVIDIA, vision+video. Fallback if 30B is slow. |
| `nex-agi/nex-n2-pro:free` | ? | 262K | Unknown quality. Test before relying on. |
| `openrouter/free` | router | 200K | Auto-routes to best free model. May not always pick vision-capable. |

## Code Swap Pattern

Replace Groq API call with OpenRouter:

```typescript
// BEFORE (Groq — dead key)
const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    headers: { 'Authorization': `Bearer ${groqKey}` },
    body: JSON.stringify({
        model: 'meta-llama/llama-4-scout-17b-16e-instruct',
        messages: [...],
        max_tokens: 2048,
    }),
});

// AFTER (OpenRouter — free model)
const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    headers: {
        'Authorization': `Bearer ${orKey}`,
        'HTTP-Referer': 'https://veracar.co',  // REQUIRED by OpenRouter
        'X-Title': 'veracar.co Vehicle Analyzer',  // Appears in dashboard
    },
    body: JSON.stringify({
        model: 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free',
        messages: [...],  // Same structure — no change needed
        max_tokens: 2048,
    }),
});
```

**Key differences:**
- URL: `api.groq.com` → `openrouter.ai/api/v1/chat/completions`
- Headers: Add `HTTP-Referer` and `X-Title` (OpenRouter requirement)
- Model: Same Llama 4 Scout or any OpenRouter model
- Messages format: Identical — image_url content blocks work the same

## Pitfalls

- **OWL Alpha is text-only**: `openrouter/owl-alpha` has `input_modalities: ['text']` — no vision. Don't use for image extraction.
- **Google models banned**: User explicitly forbids Google/Gemini models. Never select them even if free.
- **OpenRouter free models sometimes slow**: Cold starts can take 5-15s. Set generous timeouts.
- **`HTTP-Referer` header is mandatory**: OpenRouter rejects requests without it with opaque "User not found" errors.
