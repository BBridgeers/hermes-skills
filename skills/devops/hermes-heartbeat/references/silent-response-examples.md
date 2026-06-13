# Silent Response Guidelines

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

Remember: `[SILENT]` suppresses ALL delivery — use only when genuinely no new actionable issues exist.