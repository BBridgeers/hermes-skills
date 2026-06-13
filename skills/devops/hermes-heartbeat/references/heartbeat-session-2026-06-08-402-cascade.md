# Session: 2026-06-08 — OpenRouter 402 Cascade + Heartbeat Self-Blindspot

## Pattern

On 2026-06-08T22:10 UTC, OpenRouter credits were exhausted. This caused **11 agent-based cron jobs** to simultaneously fail with `HTTP 402: Insufficient Balance` — a sharp escalation from the prior state (only 3 jobs failing with Ollama 429 + tirith blocks).

Critically, the heartbeat job itself was among the 11 affected jobs. It ran every 5 minutes but failed every time with 402, producing **zero log entries and zero reports for 13 hours**. The operator had no monitoring coverage during that window.

## Detection Signal

At recovery (heartbeat finally completes), the following pattern was observed:

| Signal | Value |
|---|---|
| Heartbeat `last_status` | `"error"` with `RuntimeError: HTTP 402: Insufficient Balance` |
| Heartbeat `next_run_at` | Advancing normally every 5m (scheduler alive) |
| Heartbeat `last_run_at` | Stale — 13h gap between successful runs |
| Jobs with `last_error` containing "402" | **11 out of 23** |
| Script-only jobs (no_agent=true) | All OK (0 failures) |
| Jobs on non-OpenRouter providers | OK or separate failures (Ollama 429) |

## What Worked

- **Inferring credit exhaustion from job error patterns** was the only viable detection path — the OpenRouter `/api/v1/auth/key` endpoint returned 401 "User not found" even with a valid key, making the API-based detection method in the skill unusable.
- The spike of 11 jobs all failing with the same 402 error was definitive evidence.
- Script-based jobs (disk-REDACTED, rclone-upload-gdrive) confirmed the scheduler was alive — only model-dependent jobs were failing.

## What Failed

- The heartbeat's API-based credit balance check (`/api/v1/auth/key`) returned 401, not useful data.
- No secondary monitoring channel existed. The heartbeat used the same OpenRouter model as all other agent jobs — it was blocked by the same credit wall.
- The operator had no way to know monitoring was dark for 13 hours.

## Resolution Paths

1. Credits replenish on monthly billing cycle (passive wait).
2. No heartbeat-level workaround exists — the heartbeat needs the same provider/credentials as the jobs it monitors.
3. A separate low-cost health check (e.g., a simple ping to a free API) on a different provider could serve as a secondary heartbeat, but this is not currently implemented.

## Applied Lessons

- Added fallback detection method (cron job error pattern analysis) to the heartbeat skill.
- Added "Heartbeat self-blindspot" pitfall documenting the monitoring gap pattern.
- When recovering from a credit-exhaustion gap, always report the gap duration so the operator knows monitoring was dark.
