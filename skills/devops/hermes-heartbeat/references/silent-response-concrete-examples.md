# Silent Response: Concrete Examples & Verification

## When to Use `[SILENT]`

Respond with exactly `[SILENT]` (and nothing else) when:

1. **All findings are within 48-hour dedup window** - Issues already reported in recent heartbeats
2. **Only known recurring patterns detected** - External-feature-daily security scanner blocks, cron day-of-week bugs, etc.
3. **System is genuinely healthy** - No P0/P1 issues, all services operational
4. **Resource usage within normal bounds** - CPU < 90%, disk < 85%, memory < 90%

## Examples of `[SILENT]` Scenarios

### Scenario 1: All findings deduplicated
```
External-feature-daily: security scanner block (known)
SSH brute force: 103.230.153.91 (within 48h dedup)
Cron day-of-week bug: 6 weekly jobs never-run (known)
All services: gateway/dashboard/workspace up
Resources: CPU 0%, Disk 74%, Mem 25%
→ [SILENT]
```

### Scenario 2: System healthy
```
No failed jobs
No stuck jobs  
No SSH attacks
All services operational
Resources normal
→ [SILENT]
```

### Scenario 3: Known patterns only
```
External-feature-daily: security scanner block "exfil_curl_auth_header" (known)
Slack-context-sync: enabled_toolsets=null gap (known)
Weekly jobs: day-of-week dispatch bug (known)
→ [SILENT]
```

## When NOT to Use `[SILENT]`

- **New P0 issues** - Failed jobs, stuck processes, dead services
- **New P1 issues** - SSH brute force from new external IPs, resource alerts
- **Configuration drift** - Model/provider mismatch, missing env vars
- **Service degradation** - Any service not "active" or returning errors

## Dedup Verification Process

1. Check `~/.hermes/heartbeat.log` for identical findings within 48 hours
2. Use `session_search(query="job-name failed")` for cron job failures
3. Verify SSH IP patterns against known recurring attackers
4. Confirm service status patterns match previous reports

## Batch Deduplication Rule

If the last **N consecutive heartbeat entries (N ≥ 2)** are identical, the current run MUST output exactly `[SILENT]` to suppress delivery — otherwise the system will redeliver the same notification repeatedly.

**Example**: If the last 5 heartbeat entries were `HEARTBEAT_OK ... CPU:4.5% Disk:64% ... Status:OK`, the 6th run must output `[SILENT]` only, not `[SILENT] ... CPU:4.5% ...`.

This pattern was learned in the 162nd consecutive run where identical findings triggered `[SILENT]` — the session correctly suppressed delivery. The log now shows 161st/162nd consecutive OK runs — the dedup mechanism is working as designed and `[SILENT]` is the correct behavior.

## Session-Specific: 2026-05-25T16:30:52+00:00

- External-feature-daily error: blocked by "exfil_curl_auth_header" pattern (known, dedup)
- All 12 cron jobs healthy (1 error within 48h dedup window)
- Services: gateway/dashboard/workspace all "active"
- Resources: CPU 4.5%, disk 64%, mem 53% — all within normal bounds
- No SSH failures in 24h
- Model/provider config stable: qwen3-coder-next / ollama-cloud

→ `[SILENT]` is the correct output — no actionable new issues, dedup applies.
