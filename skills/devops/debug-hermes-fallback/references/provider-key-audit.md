# Provider Key Audit — Endpoints & Error Codes

Last updated: 2026-06-05

Systematic key validation for all Hermes-configured providers. Run this when fallback chain collapses or after key rotation.

## Test Endpoints

| Provider | Test URL | Method | Auth Header | Success Code | Failure Patterns |
|----------|---------|--------|-------------|--------------|-----------------|
| OpenRouter | `https://openrouter.ai/api/v1/models` | GET | `Bearer $KEY` | 200 | 402=credits, 401=revoked |
| DeepSeek | `https://api.deepseek.com/v1/chat/completions` | POST | `Bearer $KEY` | 200 | 401=revoked, 402=balance |

**DeepSeek auth**: The `/v1/models` endpoint on DeepSeek also requires a valid key. A 401 from either endpoint means the key is dead. Test with a minimal chat completion (`model: deepseek-chat, max_tokens: 10`) to confirm the key works for production traffic, not just model listing.
| Google | `https://generativelanguage.googleapis.com/v1beta/models?key=$KEY` | GET | Query param | 200 | 400=bad key, 429=rate |
| Ollama Cloud | `https://ollama.com/v1/chat/completions` | POST | `Bearer $KEY` | 200 | 429=weekly limit, 401=revoked |

**Ollama Cloud auth caveat**: `/v1/models` and `/api/tags` return 200 WITHOUT any auth key — they are public endpoints. Never use model-list success as evidence the key is valid. Only `/v1/chat/completions` actually validates the key. A 200 from models + 401 from chat/completions = revoked key. This is the #1 diagnostic false positive: you test models, get 200, assume key is fine, waste time debugging config when the key is actually dead.

## Chat Completion Test Endpoints (Key Validation)
| OpenCode Zen | `https://api.opencode.ai/zen/v1/models` | GET | `Bearer $KEY` | 200 | 403/1010=revoked key |
| GLM/z.ai | `https://api.z.ai/api/paas/v4/chat/completions` | POST | `Bearer $KEY` | 200 | 429/1113=no balance, 400/1211=bad model |

## Python Test Script

```python
import json, urllib.request, urllib.error

def test_key(name, key, url, headers_extra=None, body=None, method="GET"):
    req_headers = headers_extra or {}
    data = json.dumps(body).encode() if body else None
    if body:
        req_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return True, resp.getcode(), "OK"
    except urllib.error.HTTPError as e:
        return False, e.code, e.read().decode()[:200]

# Usage:
# valid, code, detail = test_key("OpenRouter", os.getenv("OPENROUTER_API_KEY"),
#     "https://openrouter.ai/api/v1/models", {"Authorization": f"Bearer {key}"})
```

## Results from 2026-06-05 Audit

| Provider | Status | Code | Detail |
|----------|--------|------|--------|
| OpenRouter | ✅ | 200 | OK (but later drained to 402) |
| DeepSeek | ✅ | 200 | OK |
| Google | ✅ | 200 | OK |
| Ollama Cloud | ✅ | 200 | OK (but later hit 429 weekly limit) |
| OpenCode Zen | ❌ | 403 | Error 1010 — key revoked/expired |
| GLM/z.ai | ⚠️ | 429 | Error 1113 — insufficient balance |

## Simultaneous Drain Pattern

When OpenRouter (402 credits) and Ollama Cloud (429 weekly limit) fail simultaneously, the entire fallback chain collapses. Hermes retries each provider 3 times before moving on. The user sees spam from both providers in the same call chain but the real issue is both accounts are exhausted at the same time.

### Recovery Steps
1. Audit keys with this script
2. Switch primary to a working provider
3. Rewrite fallback chain to use only working providers
4. Fix auxiliary services (compression, MCP, delegation)
5. Restart gateway
