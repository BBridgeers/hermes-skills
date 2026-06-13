# Heartbeat Log Analysis Patterns

## Purpose

This document captures session-specific details about the heartbeat log format, dedup patterns, and how to interpret consecutive heartbeat runs.

## Log Format

```
HEARTBEAT_{STATUS} {ISO_TIMESTAMP} | CPU:{pct} Disk:{pct} Mem:{pct} | Native:{services_status} | Cron:{count} jobs, {failed} failed, {stuck} stuck, {never_run} never-run | Config:{status} | Model:{model}/{provider} | Status:{OK|WATCH|DEGRADED} | {findings summary}
```

## Status Indicators

| Status | Trigger | Action Required |
|--------|---------|-----------------|
| OK | No P0/P1/P2 flags | None (auto-log only) |
| WATCH | Any P1 or P2 flag | Investigate |
| DEGRADED | Any P0 flag | Immediate attention |

## Dedup Patterns

### Consecutive Identical Runs (DUP counter)

When a heartbeat session produces no *new* findings relative to the last run, it returns `[SILENT]` to suppress delivery. The log still records the timestamp and continues incrementing its internal DUP counter.

Example:
```
HEARTBEAT_OK 2026-05-24T12:14:48+00:00 | ... | Status:OK | DUP: 151st consecutive run with identical findings. Zero SSH failures. All services healthy. Execution loop alive. No P0/P1 issues.
HEARTBEAT_OK 2026-05-24T11:39:57+00:00 | ... | Status:OK | DUP: 150th consecutive run with identical findings.
```

### Switching to New Findings

When new findings emerge (e.g., disk usage spikes, SSH failures appear), the next heartbeat will produce a full report (not `[SILENT]`) and the DUP counter resets. The log will show two consecutive lines, with the first being old and the second containing *new* findings.

### State Change Detection

A heartbeat run is considered to produce "state change" when:
1. A service transitions from `active` → `inactive` or vice versa
2. A job transitions from `ok` → `failed`/`error` or `error` → `ok`
3. Resource thresholds cross a redline (CPU >90%, disk >85%, mem >90%)
4. A new SSH brute force pattern emerges (>5 failures in last hour)
5. Config drift is detected (different model/provider than expected)

If a heartbeat run detects a state change, it produces a full report regardless of dedup. `[SILENT]` is only used when *all* findings are duplicates of the previous run.

## Session-Specific Findings (Today's Session)

This session (2026-05-24T12:26) confirmed:
- Gateway, dashboard, and workspace all `active` and healthy
- Zero SSH failures in auth.log (no external or internal)
- Jobs.json shows 19 cron jobs: 1 known error (external-feature-daily), 4 never-run (weeklies not due yet), 0 stuck
- Config parse: valid YAML
- Model/provider: qwen3-coder-next/ollama-cloud (no drift detected)
- Disk usage: 70% (no trending concern)
- Zombie process detected: `bash` defunct (PID 3962809) — status 1 (Zombie); this is a benign shell cleanup zombie, not a service hang

## Known Recurring Patterns

| Pattern | Status | Notes |
|---------|--------|-------|
| external-feature-daily job fails | Known recurring | Trigger: blocked by tirith security scanner (`exfil_curl_auth_header`) |
| State.db not readable | Instrumentation | Handled by using read_file, not treating as error |

## Dedup Decision Matrix

| Scenario | Dedup | Output |
|----------|-------|--------|
| All findings identical to last run | `[SILENT]` | No delivery |
| Any new finding since last run | Full report | Delivery with findings |
| recovered jobs (error → ok) | Full report | First time back to ok |
| service restoration (inactive → active) | Full report | First run after recovery |
