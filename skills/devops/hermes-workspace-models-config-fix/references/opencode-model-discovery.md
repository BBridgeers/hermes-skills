# OpenCode Model Discovery — Pricing & Deprecation Reference

Last updated: May 2026. Source: opencode.ai/docs/zen and opencode.ai/docs/go

## OpenCode Zen (Pay-as-you-go)

Curated models tested for coding agents. Add $20 balance, auto-reloads at $5.
API endpoint: `https://opencode.ai/zen/v1/models`

| Model | Input $/Mtok | Output $/Mtok | Status |
|-------|-------------|---------------|--------|
| gpt-5.5 (≤272K) | $5.00 | $30.00 | Current |
| gpt-5.5 (>272K) | $10.00 | $45.00 | Current |
| gpt-5.5-pro | $30.00 | $180.00 | Current |
| gpt-5.4 (≤272K) | $2.50 | $15.00 | Current |
| gpt-5.4 (>272K) | $5.00 | $22.50 | Current |
| gpt-5.4-pro | $30.00 | $180.00 | Current |
| gpt-5.4-mini | $0.75 | $4.50 | Current |
| gpt-5.4-nano | $0.20 | $1.25 | Current |
| gpt-5.3-codex-spark | $1.75 | $14.00 | Current |
| gpt-5.3-codex | $1.75 | $14.00 | Current |
| gpt-5.2 | $1.75 | $14.00 | Current |
| gpt-5.2-codex | $1.75 | $14.00 | ⚠ Deprecated July 23 2026 |
| gpt-5.1 | $1.07 | $8.50 | Current |
| gpt-5.1-codex-max | $1.25 | $10.00 | ⚠ Deprecated July 23 2026 |
| gpt-5.1-codex | $1.07 | $8.50 | ⚠ Deprecated July 23 2026 |
| gpt-5.1-codex-mini | $0.25 | $2.00 | ⚠ Deprecated July 23 2026 |
| gpt-5 | $1.07 | $8.50 | Current |
| gpt-5-codex | $1.07 | $8.50 | ⚠ Deprecated July 23 2026 |
| gpt-5-nano | $0.05 | $0.40 | Current |
| claude-opus-4-7 | $5.00 | $25.00 | Current |
| claude-opus-4-6 | $5.00 | $25.00 | Current |
| claude-opus-4-5 | $5.00 | $25.00 | Current |
| claude-opus-4-1 | $15.00 | $75.00 | Current (expensive!) |
| claude-sonnet-4-6 | $3.00 | $15.00 | Current |
| claude-sonnet-4-5 (≤200K) | $3.00 | $15.00 | Current |
| claude-sonnet-4-5 (>200K) | $6.00 | $22.50 | Current |
| claude-sonnet-4 | $3.00 | $15.00 | ⚠ Deprecated June 15 2026 |
| claude-haiku-4-5 | $1.00 | $5.00 | Current |
| gemini-3.1-pro (≤200K) | $2.00 | $12.00 | Current |
| gemini-3.1-pro (>200K) | $4.00 | $18.00 | Current |
| gemini-3-flash | $0.50 | $3.00 | Current |
| qwen3.6-plus | $0.50 | $3.00 | Current |
| qwen3.5-plus | $0.20 | $1.20 | Current |
| minimax-m2.7 | $0.30 | $1.20 | Current |
| minimax-m2.5 | $0.30 | $1.20 | Current |
| glm-5.1 | $1.40 | $4.40 | Current |
| glm-5 | $1.00 | $3.20 | ⚠ Deprecated May 14 2026 |
| kimi-k2.6 | $0.95 | $4.00 | Current |
| kimi-k2.5 | $0.60 | $3.00 | Current |
| big-pickle | Free | Free | Stealth, limited time |
| deepseek-v4-flash-free | Free | Free | Limited time |
| minimax-m2.5-free | Free | Free | Limited time |
| nemotron-3-super-free | Free | Free | NVIDIA trial |

Free model caveats: Big Pickle, DeepSeek V4 Flash Free, and MiniMax M2.5 Free may use your data to improve models during the free period. Nemotron 3 Super Free follows NVIDIA API Trial Terms — prompts/outputs logged by NVIDIA, not for production/sensitive data.

## OpenCode Go ($10/month)

Flat subscription for open coding models. $5 first month, $10/mo. $60/mo cap.
API endpoint: `https://opencode.ai/zen/go/v1/models`

| Model | Est. req/5hr | Notes |
|-------|-------------|-------|
| glm-5.1 | 880 | Bilingual CN/EN, agent-centric |
| glm-5 | 1,150 | Previous Zhipu |
| kimi-k2.6 | 1,150 | Latest Moonshot reasoning |
| kimi-k2.5 | 1,850 | Previous Kimi, good value |
| deepseek-v4-pro | 3,450 | Flagship 1M ctx reasoning |
| deepseek-v4-flash | 31,650 | Fast variant, best Go value |
| minimax-m2.7 | 3,400 | Multilingual, creative |
| minimax-m2.5 | 6,300 | Solid general purpose |
| qwen3.6-plus | 3,300 | Latest Qwen coding |
| qwen3.5-plus | 10,200 | Best Go value for coding |
| mimo-v2.5 | 2,150 | Xiaomi base |
| mimo-v2.5-pro | 1,290 | Xiaomi improved |

Go models may also include additional models visible only via API (hy3-preview, mimo-v2-pro, mimo-v2-omni). The sync script fetches from the live API to keep the list current.

## OpenRouter Free Models

Key free models on OpenRouter as of May 2026 (fetched dynamically by sync script):

**Stealth/Beta:**
- `openrouter/owl-alpha` — High-performance foundation model, 1M ctx, agentic workloads, tool use native. Widely believed to be a Grok variant. Currently free.

**Production Free:**
- `nvidia/nemotron-3-super-120b-a12b:free` — 1M ctx, 120B MoE
- `deepseek/deepseek-v4-flash:free` — 1M ctx
- `qwen/qwen3-coder:free` — 1M ctx, code-specialized
- `google/gemma-4-31b-it:free` — 262K ctx
- `meta-llama/llama-3.3-70b-instruct:free` — 131K ctx
- `nousresearch/hermes-3-llama-3.1-405b:free` — 131K ctx

**Preview/Experimental:**
- `google/lyria-3-pro-preview` — Music generation, free
- `google/lyria-3-clip-preview` — Music clips, free

The sync script auto-discovers all free models by checking pricing=0 via the API.

## OpenCode Local Cache

The OpenCode CLI maintains a local model cache at `/root/.cache/opencode/models.json`
(typically 117+ models). This file has a nested structure — providers as top-level
keys, each with a `models` object containing detailed model entries with pricing,
context windows, capabilities, and deprecation notices.

**Structure:**
```json
{
  "deepseek": {
    "models": {
      "deepseek-v4-pro": {
        "id": "deepseek-v4-pro",
        "name": "DeepSeek V4 Pro",
        "cost": {"input": 0.28, "output": 1.10},
        "limit": {"context": 1048576, "output": 16384},
        ...
      }
    }
  },
  "openrouter": { ... },
  "perplexity": { ... },
  ...
}
```

This cache is **NOT** automatically synced to the workspace's `models.json`.
The workspace reads from `~/.hermes/models.json` (flat array), not from the
OpenCode cache. However, the cache is useful as a reference when populating
or cross-checking the workspace model list.
