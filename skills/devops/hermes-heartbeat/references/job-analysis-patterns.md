# Job Analysis Patterns

## Healthy Patterns

### Normal Execution
- `last_status: "ok"` with recent `last_run_at`
- `next_run_at` advancing normally according to schedule
- `repeat.completed` incrementing with each run
- `state: "scheduled"` between executions

### First-Time Execution  
- `last_run_at: null` AND `repeat.completed: 0` AND `next_run_at` in future
- Normal for newly created jobs that haven't fired yet

## Problem Patterns

### Failed Jobs (P0)
- `last_status: "failed"` or `last_status: "error"`
- Check `last_error` field for specific failure reason
- Example: `"Blocked: prompt matches threat pattern 'exfil_curl_auth_header'"`

### Stuck Jobs (P0)
- `last_status: "running"` AND `last_run_at` >45 minutes ago
- `state: "running"` for >45 minutes
- Indicates job dispatched but never completed

### Dead Execution Loop (P0 DEGRADED)
- ANY job with `next_run_at` in past (>1 hour ago) AND 
- `last_run_at` is either null OR >48 hours stale
- Scheduler API layer alive but execution loop dead

### Toolsets Null Bug (P1 WATCH)
- `enabled_toolsets: null` AND 
- `next_run_at` advancing normally BUT
- `last_run_at` stagnant (not updating)
- Job silently skipped due to missing toolsets config

### Never-Run Sentinel (P1 WATCH)  
- `last_run_at: null` AND `repeat.completed: 0` AND
- Job created >24h ago AND `next_run_at` in future
- Doesn't prove dead loop but worth noting

## Session Search Patterns for Dedup

Use these `session_search` queries to check for recent duplicates:

```python
# Check for same job failure
session_search(query="external-feature-daily failed security scanner")

# Check for same SSH brute force IP  
session_search(query="103.230.153.91 SSH brute force")

# Check for systemic scheduler issues
session_search(query="cron day-of-week bug")

# Check for toolsets null issues
session_search(query="enabled_toolsets null")

# Check for specific error patterns
session_search(query="exfil_curl_auth_header")
```

## Recovery Patterns

### Genuine Recovery
- Previously failing job now shows `last_status: "ok"`
- `last_run_at` updated to recent timestamp
- `repeat.completed` incremented

### False Recovery (Dedup)
- Same error persists but within 48h dedup window
- Status changes from DEGRADED→OK due to dedup, not actual fix

## Priority Escalation Guide

| Pattern | Initial | Escalation |
|---------|---------|------------|
| Single job failure | P0 | P0 (remains) |
| Multiple job failures | P0 DEGRADED | P0 DEGRADED |
| Stuck job >45min | P0 | P0 (remains) |
| Dead execution loop | P0 DEGRADED | P0 DEGRADED |
| Toolsets null bug | P1 WATCH | P1→P0 if gap >24h |
| SSH brute force (known IP) | P1 | P1 (dedup if <48h) |
| SSH brute force (new IP) | P1 | P0 if >10 attempts/hour |

## Common Error Messages

- `"Blocked: prompt matches threat pattern 'exfil_curl_auth_header'"` - Security scanner block
- `"Tool not available"` - Missing toolset configuration
- `"Timeout after 300 seconds"` - Job execution timeout
- `"Connection refused"` - Service connectivity issues