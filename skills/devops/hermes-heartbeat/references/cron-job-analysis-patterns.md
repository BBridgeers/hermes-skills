# Cron Job Analysis Patterns

## Job State Analysis

### Failed Jobs (P0)
- `last_status: "failed"` OR `last_status: "error"`
- Check `last_error` field for specific failure details
- **Known recurring failures**: external-feature-daily security scanner blocks

### Stuck Jobs (P0)
- `last_status: "running"` AND `last_run_at` > 45 minutes ago
- `state: "running"` (not "scheduled") for >45 minutes
- Indicates hung execution that never completed

### Never-Run Jobs Analysis
- `last_run_at: null` AND `repeat.completed: 0` AND creation >24h ago
- **Day-of-week bug**: Weekly cron jobs (e.g., "0 4 * * 1") that never fire due to scheduler issues
- **Toolsets null bug**: Jobs with `enabled_toolsets: null` may be silently skipped

### Recovery Patterns
- Jobs that show `last_status: "error"` → `last_status: "ok"` with recent successful runs
- These indicate transient problems that self-resolved

## Scheduler Health Signals

### Dead Execution Loop Indicators
- ANY job has `next_run_at` in past (>1 hour ago) 
- AND `last_run_at` is either null OR >48 hours stale
- Scheduler API accepts commands but execution loop not dispatching

### Silent Skip Patterns
- Jobs with `enabled_toolsets: null` may advance `next_run_at` normally
- But `last_run_at` remains stagnant — job silently skipped by scheduler
- Compare against job creation dates and expected fire windows

## Common Patterns

### Weekly Job Day-of-Week Bug
- **Pattern**: 6+ weekly jobs never running despite being due
- **Example**: cost-report-weekly, weekly-review-sunday, skill-leaderboard-weekly, etc.
- **Root cause**: Scheduler cron expression parsing issue for weekly schedules
- **Status**: Known issue, should be P2 CONFIG rather than P0 FAILED

### Security Scanner False Positives
- **Pattern**: external-feature-daily job blocked with "exfil_curl_auth_header"
- **Frequency**: Daily recurrence
- **Classification**: P3 INFO after initial reporting

## Priority Guidelines
- **P0**: Active failures, stuck executions, dead scheduler loops
- **P1**: Security issues (SSH brute force), resource constraints
- **P2**: Configuration drift, never-run jobs with known patterns
- **P3**: Recurring known issues, self-resolved transient failures