# Known Recurring Patterns - External-Feature-Daily Job

## Job Details
- **Job ID**: 1f1e541dd9ca
- **Job Name**: external-feature-daily
- **Schedule**: 0 4 * * * (daily at 04:00 UTC)

## Recurring Issue
This job frequently triggers security scanner blocks with the pattern:
```
## Root Cause
The job's prompt contains patterns that match security scanner heuristics for potential credential exfiltration, but this is a false positive.

## Status
- **Classification**: Known false positive
- **Priority**: P1 (but should be deduplicated after initial reporting)
- **Response**: Monitor but don't alert repeatedly

## Dedup Guidelines
- First occurrence: Report as P1 STALLED
- Subsequent occurrences within 48h: Dedup and mark as "known"
- After 48h: Re-evaluate if pattern persists

## Session History
- 2026-05-20 04:00: First blocked execution
- Multiple heartbeats show this as recurring pattern
- Consistently classified as "known issue" after initial reporting

---

# Known Recurring Patterns - External-Feature-Daily RuntimeException Wrapper

## Job Details
- **Job ID**: 1f1e541dd9ca
- **Job Name**: external-feature-daily
- **Schedule**: 0 4 * * * (daily at 04:00 UTC)

## Pattern
This job shows `last_status: "error"` in jobs.json, but the `last_error` field contains the full successful output of the job (e.g., a PR creation summary) wrapped in a `RuntimeError`. The agent completed its task successfully — created a PR, documented results — but the scheduler marks the session as "error" because the agent's final output was treated as an error by the runtime.

## Example
```
last_status: "error"
last_error: "RuntimeError: ## External Feature — 2026-06-01 Complete\n\n**Repo:** aaronjmars/aeon\n**PR:** https://github.com/aaronjmars/aeon/pull/309\n**What:** Added 71 unit tests..."
```

The error text IS the success report — the job worked correctly, but the runtime wrapping makes it appear failed.

## Classification
- **Priority**: P3 INFO — not a real failure
- **Dedup**: Flag once as "P3 INFO: external-feature-daily last_status=error but content is success (PR #309) — false-positive RuntimeException wrapper"
- **Subsequent heartbeats**: Include in log line but do NOT treat as a new finding requiring notification

## Root Cause
The Hermes cron scheduler wraps certain agent outputs in a `RuntimeError` when the agent's response format doesn't match the scheduler's expected success envelope. The underlying work (PR creation, file edits) completed successfully.

## Session History
- First observed: 2026-05-28 (heartbeat flagged as P0 Ring-2.6-1T paywall session)
- Confirmed recurring: Every heartbeat from 2026-05-28 through 2026-06-01
- Current status: Ongoing P3 INFO flag, no action needed
- 2026-05-20 04:00: First blocked execution
- Multiple heartbeats show this as recurring pattern
- Consistently classified as "known issue" after initial reporting

---

# Known Recurring Patterns - Fb-Scraper Container Created (Port Bind Conflict)

## Job/Container Details
- **Container**: fb-scraper
- **Status**: Created (never started)
- **Co-tenant**: Yes, not Hermes-managed

## Recurring Issue
The `fb-scraper` Docker container persistently shows `Created` status because port 8765 is already in use by another process. This is a co-tenant misconfiguration — the container was created but `docker start` fails due to the port conflict.

```
docker inspect fb-scraper --format '{{.State.Status}} {{.State.Error}}'
→ created failed to set up container networking: driver failed programming external connectivity on endpoint fb-scraper: failed to bind host port 0.0.0.0:8765/tcp: address already in use
```

## Classification
- **Priority**: P2 WATCH (co-tenant, not Hermes-managed, no auto-fix)
- **Dedup**: Flag once as "P2 WATCH: fb-scraper container Created (port bind conflict, co-tenant)" and include in recurring log entries but do NOT treat each heartbeat as a new finding
- **Action**: None — this is not Hermes' responsibility. Do NOT auto-fix co-tenant containers.

## Session History
- Observed in every heartbeat from at least 2026-05-30 through 2026-06-02
- Consistently classified as P2 WATCH (co-tenant)
- No action taken or needed
- 2026-06-05: Container removed — resolved

---

# Known Recurring Patterns — Ollama Cloud Weekly Usage Limit (HTTP 429)

## Pattern
Multiple cron jobs simultaneously fail with `HTTP 429: you (bbridgers) have reached your weekly usage limit`. The Ollama Cloud free-tier weekly quota is exhausted for user `bbridgers`, blocking all agent-dispatched jobs that route through the Ollama provider.

## Detection
- Count jobs with `last_error` containing `HTTP 429` AND `weekly usage limit`
- 8-15+ jobs failing in the same cycle window
- Script-only jobs (disk-REDACTED, rclone-upload-gdrive) and non-Ollama-provider jobs continue succeeding

## Classification
- **Priority**: P0 DEGRADED (mass systemic failure)
- **Dedup**: Report once as `HEARTBEAT_DEGRADED ... 12 failed (12 Ollama 429)`. Subsequent heartbeats while limit is still exhausted: include in log line but do NOT re-notify.
- **Recovery signal**: when jobs start returning `last_status: "ok"`, the limit has reset. Downgrade to OK.

## Recovery Options
1. Wait for Ollama Cloud weekly reset (typically Mon/Tue UTC, check ollama.com/settings)
2. Switch provider: `hermes config set model.provider openrouter`
3. Per-job override for critical jobs only

## Session History
- 2026-06-05T17:44Z: First occurrence — 12 of 20 jobs simultaneously failing
- Affected: all agent-dispatched cron jobs using default Ollama provider
- Unaffected: script-only jobs + slack-context-sync (using OpenRouter)
- First encounter reference: `references/ollama-cloud-weekly-limit.md`

---

# Known Recurring Patterns — state.db Growth (Disk Pressure)

## Pattern
`/root/.hermes/state.db` (SQLite session/state database) grows continuously. Known sizes:
- 2026-05-30: ~815MB
- 2026-06-05: ~2.2GB

## Classification
- **Priority**: P2 WATCH (once it exceeds 1GB threshold; P1 if disk usage crosses 85%)
- **Dedup**: Log current size each heartbeat. Only notify on significant growth (>200MB since last logged check).
- **Action**: Consider `VACUUM INTO` on a copy, or periodic cleanup. Never `VACUUM` in-place on a live DB.

## Session History
- 2026-05-30: First flagged at 815MB
- 2026-06-05: Flagged again at 2.2GB (2.7x growth in 6 days)
- No action taken yet — needs operator decision on cleanup strategy

---

# Known Recurring Patterns — Weekly-Review-Sunday Ghost Job

## Job Details
- **Job ID**: 232fb347147d
- **Job Name**: weekly-review-sunday
- **Schedule**: 0 10 * * 0 (Sundays 10:00 UTC)
- **Created**: 2026-05-04T21:52:13Z
- **State**: scheduled, `last_run_at: null`, `repeat.completed: 0`

## Pattern
Job exists but never executes despite the schedule window having elapsed multiple times. As of 2026-06-05, 4 Sundays (05-11, 05-18, 05-25, 06-01) have passed with 0 completions. This is a "ghost job" — the scheduler has it registered but never dispatches it.

## Classification
- **Priority**: P1 WATCH (scheduling issue, not a crash)
- **Dedup**: Report once per 48h window with count of missed opportunities
- **Investigation**: Check scheduler dispatch logic for this job type. May have a model/toolset configuration issue preventing dispatch.

## Session History
- 2026-06-01: First flagged as "never-run sentinel" (1 missed Sunday)
- 2026-06-05: Reclassified as ghost job (4 missed Sundays confirmed)
- No action taken yet — needs scheduler investigation