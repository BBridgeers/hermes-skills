# Dedup Pattern Examples for Heartbeat Analysis

These examples show common dedup patterns that should result in `[SILENT]` responses when running as cron jobs.

## Example 1: Security Scanner Block (Known Issue)

**Job**: `external-feature-daily`
**Error**: "Blocked: prompt matches threat pattern 'exfil_curl_auth_header'"
**Status**: Known recurring issue, within 48h dedup window
**Response**: `[SILENT]`

## Example 2: Cron Day-of-Week Dispatch Bug

**Pattern**: Multiple weekly jobs never firing due to scheduler bug
**Jobs**: cost-report-weekly, weekly-review, skill-leaderboard, skill-update-check, vuln-scanner, security-audit
**Status**: Known bug since May 4, within 48h dedup window  
**Response**: `[SILENT]`

## Example 3: SSH Brute Force from Known IP

**IP**: 103.230.153.91
**Pattern**: 20+ failed attempts in 2-minute window
**Timing**: Over 24 hours ago, within 48h dedup window
**Response**: `[SILENT]`

## Example 4: Internal IP SSH Attempts (Testing/Automation)

**IP**: 172.16.0.3 (internal network)
**Pattern**: 4 failed attempts
**Classification**: P2 WATCH (testing/automation, not external attack)
**Response**: `[SILENT]`

## Example 5: Recovered Job

**Job**: `slack-context-sync`
**Previous Status**: Gap of 10+ hours, enabled_toolsets=null bug
**Current Status**: Running normally, recovered
**Response**: `[SILENT]` (note recovery but don't alert)

## Non-Dedup Examples (Warrant Full Reporting)

### New P0 Issue
**Job**: Any job with `last_status: "failed"` that hasn't been reported in 48h
**Response**: Full report with details

### New Security Alert  
**Pattern**: SSH brute force from new external IP (>5 attempts in last hour)
**Response**: Full report with IP details

### Service Degradation
**Service**: Gateway, dashboard, or workspace down
**Response**: Full report with service status

### Configuration Drift
**Change**: Model/provider mismatch from expected primary
**Response**: Full report with configuration details