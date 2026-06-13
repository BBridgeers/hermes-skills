# Provider API Key Audit — Lightweight Health Check

## Pattern

Systematically test every provider API key with a minimal call to verify validity, credit status, and rate limits. One script, all providers, immediate results.

## Protocol

```python
import json, os, urllib.request, urllib.error

def test_key(name, key, url, headers_extra=None, body=None, method="GET"):
    try:
        req_headers = headers_extra or {}
        data = json.dumps(body).encode() if body else None
        if body: req_headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        resp = urllib.request.urlopen(req, timeout=15)
        return True, resp.getcode(), "OK"
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()[:300]
        return False, e.code, body_text
    except Exception as e:
        return False, 0, str(e)[:200]
```

## Provider Test Endpoints

| Provider | Test URL | Auth Header | Method |
|----------|----------|-------------|--------|
| OpenRouter | `https://openrouter.ai/api/v1/models` | `Bearer $KEY` | GET |
| DeepSeek | `https://api.deepseek.com/models` | `Bearer $KEY` | GET |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/models?key=$KEY` | (in URL) | GET |
| Ollama Cloud | `https://ollama.com/v1/models` | `Bearer $KEY` | GET |
| OpenCode Zen | `https://api.opencode.ai/zen/v1/models` | `Bearer $KEY` | GET |
| GLM/z.ai | `https://api.z.ai/api/paas/v4/chat/completions` | `Bearer $KEY` | POST (small body) |

## Interpreting Results

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Key valid, credits available | ✅ Good |
| 401 | Key invalid/revoked | ❌ Regenerate immediately |
| 402 | Insufficient credits (OpenRouter) | ⚠️ Add credits or disable provider |
| 403 | Key forbidden/expired (OpenCode Zen error 1010) | ❌ Regenerate |
| 429 | Rate limited or no balance (GLM 1113 = "Insufficient balance") | ⚠️ Key works but can't make calls |

## GLM/z.ai Specifics

GLM returns 429 for BOTH rate limits AND insufficient balance. Error code `1113` = "Insufficient balance or no resource package." The key is valid but the account has $0. Error code `1211` = "Unknown Model" (wrong model name in test body).

Valid GLM model names (June 2026): `glm-4.5`, `glm-4.5-air`, `glm-4.6`, `glm-4.7`. Try `glm-4.5` for a lightweight test call.

## Session Drain Diagnostic

When OpenRouter credits vanish, pull the activity CSV:
1. Go to https://openrouter.ai/activity
2. Export as CSV
3. Analyze: total cost, model breakdown, hourly spend, top 10 most expensive calls
4. Check app_name column — if it says "Hermes Agent" and the user wasn't on their computer, something is running autonomously (check cron jobs, tmux sessions, workspace)

Key metrics: calls per hour, avg prompt tokens, cost per call, finish_reason (tool_calls vs stop), app_name.
