# Dedup Concrete Examples - Session Patterns

## Example 1: External-feature-daily Security Block (2026-05-20)

**Pattern**: Security scanner block "exfil_curl_auth_header"
**Job ID**: 1f1e541dd9ca
**First Report**: 2026-05-20T04:02:40+00:00 (DEGRADED)
**Subsequent Reports**: Multiple OK statuses with dedup annotations
**Dedup Logic**: "external-feature-daily error, cron day-of-week bug, SSH 103.230.153.91/172.16.0.3) within 48h dedup window"

## Example 2: SSH Brute Force Classification

**External IP Pattern**:
```
2026-05-19T04:19:41.684331+00:00 Failed password for invalid user user from 103.230.153.91
2026-05-19T04:19:43.243219+00:00 Failed password for invalid user user2 from 103.230.153.91
2026-05-19T04:19:45.776675+00:00 Failed password for root from 103.230.153.91
```
- Rapid sequential attempts (<5 seconds apart)
- Multiple invalid users
- External IP address
- **Classification**: P1 STALLED

**Internal IP Pattern**:
```
2026-05-20T02:11:59.128920+00:00 Failed password for invalid user yoga from 172.16.0.3
2026-05-20T09:31:10.645928+00:00 Failed password for invalid user yoga from 172.16.0.3
```
- RFC1918 internal IP (172.16.0.3)
- Same user pattern (yoga)
- Slower frequency
- **Classification**: P2 WATCH

## Example 3: Silent Response Pattern

**When to use [SILENT]**:
- All findings are duplicates within 48-hour window
- No new P0/P1 issues detected
- System status remains unchanged from previous reports
- Known recurring patterns already documented

**Correct Usage**:
```
[SILENT]
```

**Incorrect Usage**:
```
[SILENT] but found some issues...
All OK [SILENT]
```

## Example 4: Cron Day-of-Week Bug Dedup

**Pattern**: Weekly jobs never dispatched since creation
**Affected Jobs**: cost-report-weekly, weekly-review, skill-leaderboard-weekly, security-audit-weekly, vuln-scanner-twice-weekly
**Created**: 2026-05-04
**Status**: Known scheduler bug, dedup after initial reporting
**Dedup Annotation**: "6 never-run (day-of-week bug, known)"