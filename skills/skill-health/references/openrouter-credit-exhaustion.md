# OpenRouter Credit Exhaustion (HTTP 402)

## Pattern

When the OpenRouter credit balance falls below what's needed for a `qwen3.7-max` request (which requests `max_tokens: 65536`), the API returns:

```
Error code: 402 - {'error': {'message': 'This request requires more credits, or fewer max_tokens. You requested up to 65536 tokens, but can only afford 8500.', 'code': 402}}
```

## Detection

Grep agent.log for either pattern:
- `Error code: 402`
- `can only afford`

Count unique session prefixes to determine blast radius:
```bash
grep "402" ~/.hermes/logs/agent.log | grep -oP "cron_[a-f0-9]+_" | sort -u | wc -l
```

## Classification

This is a **SYSTEMIC** issue, not per-skill. All cron jobs using OpenRouter as primary provider are affected. Hermes' fallback mechanism (`qwen3.7-max → ollama-cloud/glm-5.1`) kicks in, so jobs complete successfully but with degraded model quality.

File a single `ISS-NNN` with `category: rate-limit` and list all affected skills in `affected_skills`.

## Resolution

1. **Immediate**: Top up OpenRouter credits at https://openrouter.ai/settings/credits
2. **Preventive**: Configure spending alerts in OpenRouter dashboard
3. **Optional**: Reduce `max_tokens` in config to lower per-request cost, allowing more requests per credit dollar

## Related Issues

- ISS-004: OpenRouter 402 credit exhaustion (2026-06-02)
- ISS-002: Ring-2.6-1T `:free` variant deprecated (2026-05-29, resolved 2026-06-01) — similar systemic provider issue but model-unavailability rather than credits