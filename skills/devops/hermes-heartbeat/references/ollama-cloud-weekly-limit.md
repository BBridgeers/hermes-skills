# Ollama Cloud Weekly Usage Limit (HTTP 429)

## Detection Pattern

Multiple jobs failing simultaneously with:
```
RuntimeError: HTTP 429: Error code: 429 - {'error': 'you (bbridgers) have reached your weekly usage limit, upgrade for higher limits: https://ollama.com/upgrade or add extra usage: https://ollama.com/settings (ref: <uuid>)'}
```

## Key Indicators

- **Mass failure**: 8-15+ jobs all error in the same cycle with identical HTTP 429 message
- **User string**: `bbridgers` (configurable — check who runs the Ollama Cloud account)
- **Scope**: only agent-dispatched jobs (jobs with a prompt that spawn an agent loop). Script-only jobs (`enabled_toolsets: null`, `no_agent: true`) using simple bash/python scripts do NOT consume Ollama quota and continue to succeed.
- **Provider-specific**: jobs routed to OpenRouter (model override or different default) are unaffected during the outage.

## Distinguishing from OpenRouter 402

| Signal | Ollama 429 | OpenRouter 402 |
|---|---|---|
| Error phrase | "weekly usage limit" | "insufficient credits" / HTTP 402 |
| Reset cadence | weekly (Monday/Tuesday UTC) | monthly (billing cycle) |
| Recovery | wait or switch provider | wait or top up credits |
| Affected scope | all jobs using Ollama provider | all jobs using OpenRouter default |

## Typical Impact (2026-06-05 incident)

12 of 20 jobs failed:
- hermes-heartbeat (every 5m)
- context-loss-recovery (hourly)
- Inbox Triage (twice daily)
- Job Pipeline Follow-Up Decay (daily 17:00)
- Housing Sprint Morning Search (daily 08:00)
- self-improve-every-2d (bi-daily 08:00)
- github-trending-daily (daily 07:00)
- vibecoding-digest-daily (daily 07:00)
- Job Search Daily Discovery (daily 07:00)
- skill-health-daily (daily 06:00)
- skill-update-check-weekly (Wed 07:00)
- vuln-scanner-twice-weekly (Wed/Sat 05:00)

Unaffected (continued succeeding the same heartbeat):
- rclone-upload-gdrive (script-only, no agent)
- disk-REDACTED (script-only, no agent)
- slack-context-sync (runs via OpenRouter provider path)
- rclone-torrent-upload (agent job, but failed for separate tirith block — unrelated)

## Recovery Actions

1. **Passive**: wait for weekly limit reset. Check `https://ollama.com/settings` for reset timestamp. Limit typically resets Monday/Tuesday UTC.
2. **Active**: switch cron default provider to OpenRouter for the remainder of the week:
   ```
   hermes config set model.provider openrouter
   ```
   Jobs with explicit model overrides to Ollama will still fail; jobs with `model: null` (inheriting default) will flip to OpenRouter.
3. **Per-job override**: for critical jobs only (e.g., heartbeat), set explicit `provider: openrouter` in the job definition so they don't depend on the default.

## Do NOT

- Do not disable jobs — they self-recover when the quota resets.
- Do not report as "new" every 5 minutes — dedup aggressively. Once flagged as P0 DEGRADED for Ollama 429, treat subsequent heartbeat runs as unchanged until jobs start recovering (last_status flips from "error" back to "ok").

## First Encounter

2026-06-05T17:44Z — 12 jobs simultaneously failing; identified as Ollama Cloud free-tier weekly quota exhaustion. Resolved via reporting (auto-delivery heartbeat) and noting OpenRouter as available fallback.
