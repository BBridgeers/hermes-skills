# Provider Credit Exhaustion — Detection Reference

Diagnosing HTTP 402 "Insufficient Balance" from any AI provider. This is provider-agnostic — same pattern, different billing systems.

## Detection commands

### Count total 402 errors
```bash
grep -c 'HTTP 402\|Insufficient Balance' ~/.hermes/logs/errors.log
```

### Identify which provider(s) are affected
```bash
grep 'HTTP 402' ~/.hermes/logs/errors.log | grep -oP 'provider=\K\w+' | sort | uniq -c | sort -rn
```

### Identify affected cron sessions (unique prefixes)
```bash
grep 'HTTP 402' ~/.hermes/logs/errors.log | grep -oP 'cron_\w+' | sort -u
```

### Map cron session prefixes to job names
Run `hermes cron list` and match the hash prefix from `cron_<hash>_<timestamp>` against the job ID column.

## Provider-specific patterns

| Provider | Base URL | 402 Error Signature | Resolution |
|---|---|---|---|
| OpenRouter | `openrouter.ai/api` | `"can only afford N tokens"` or `Error code: 402` | Top up at openrouter.ai/credits. Jobs silently fall back to secondary provider until resolved. |
| DeepSeek | `api.deepseek.com` | `HTTP 402: Insufficient Balance` or `Error code: 402 - {'error': {'message': 'Insufficient Balance'...}}` | Top up at platform.deepseek.com. Hard failure — no fallback. |
| Ollama Cloud | `ollama.com/v1` | Uses 429 (rate limit), not 402 | Weekly usage limit — see Ollama 429 systemic pattern |

## Why agent.log is misleading for 402

`grep -c 'Error code: 402' ~/.hermes/logs/agent.log` returns 0 when there are real 402 errors. Reason: agent.log contains lines like:
```
API call #92: ... in=111019 out=402 total=111421
```
The `out=402` is an output token count (402 tokens generated), NOT an HTTP error code. Real 402 errors appear in `errors.log` with full error signatures.

## Classification

- **≥2 unique cron session prefixes** sharing the same provider with 402 → SYSTEMIC. File one ISS.
- **1 affected job** → per-skill WARNING (may be transient).
- **Provider matches a previously resolved ISS** → new ISS with `related: ISS-NNN` (e.g., OpenRouter 402 → DeepSeek 402 are DIFFERENT providers; do not conflate).
