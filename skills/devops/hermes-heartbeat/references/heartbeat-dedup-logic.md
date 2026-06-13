# Heartbeat Dedup Logic — Silent Response Rules

## Core Principle

**Never notify twice about the same issue within 48 hours**. Dedup prevents alert fatigue while ensuring real problems get attention.

## Dedup Decision Matrix

| Finding Type | Previous Status | Current Status | 48h Window | Action |
|---|---|---|---|---|
| P0 FAILED | `ok` | `failed` | active | ALERT (new finding) |
| P0 FAILED | `failed` | `ok` | active | ALERT (state change) |
| P0 FAILED | `failed` | `failed` | active | SUPPRESS (DUP) |
| P0 FAILED | `failed` | `ok` | expired | ALERT (old finding resolved, reset window) |
| P1 SSH | reported | `0 attempts` | active | SUPPRESS (DUP) |
| P1 SSH | `0 attempts` | `>5 attempts` | active | ALERT (threshold crossed) |
| P2 CONFIG | `ok` | `ok` | N/A | SUPPRESS (DUP if identical config) |
| Never-run job | noted | `same` | active | SUPPRESS (known pattern) |
| Stuck job | noted | `still stuck` | active | SUPPRESS (DUP) |
| Stuck job | noted | `fixed` | active | ALERT (recovery) |

## Dedup Annotations

When dedup triggers, append to heartbeat log:
```
DUP: Xth consecutive run with identical findings. Zero SSH failures. All services healthy. Execution loop alive. No P0/P1 issues.
```

Where X = number of consecutive runs with same finding set.

## Silent Response Triggers

Use exactly `[SILENT]` (no other content) when:
1. All findings are duplicates within 48h window
2. No new P0/P1 issues detected
3. No state changes (ok↔failed, healthy↔degraded)
4. System status unchanged from previous report

## Silent Response Non-Triggers

Never use `[SILENT]` when:
- Any P0/P1 issue found, even if previously reported (state change or severity increase)
- New job introduced or existing job removed
- Configuration drift detected
- New SSH failure pattern from different IP(s)
- Service status change (up↔down, active↔inactive)

## Session Pattern Analysis

**Session Log**:
```
HEARTBEAT_OK 2026-05-24T18:46:22+00:00 | ... | Status:OK | DUP: 161st consecutive run...
HEARTBEAT_OK 2026-05-24T18:04:45+00:00 | ... | Status:OK | DUP: 159th consecutive run...
HEARTBEAT_OK 2026-05-24T17:27:15+00:00 | ... | Status:OK | DUP: 157th consecutive run...
```

Pattern shows 161+ runs of identical findings. Dedup working correctly — system stable.

**Today's session (2026-05-28)**: Demonstrated P0 failures being correctly suppressed as duplicates:
- Current run found: skill-health-daily (model not found), slack-context-sync (Ring-2.6-1T paywalled), Job Pipeline — Follow-Up Decay Monitor (Ring-2.6-1T paywalled)
- Previous log (2026-05-28T20:02:28Z) showed identical findings
- As a result, the heartbeat output was suppressed with [SILENT] to prevent alert fatigue

**If dedup were broken**, you'd see:
```
HEARTBEAT_OK 2026-05-24T18:46:22+00:00 | ... | Status:OK | (no DUP annotation)
HEARTBEAT_OK 2026-05-24T18:46:17+00:00 | ... | Status:OK | (no DUP annotation)
HEARTBEAT_OK 2026-05-24T18:46:12+00:00 | ... | Status:OK | (no DUP annotation)
```