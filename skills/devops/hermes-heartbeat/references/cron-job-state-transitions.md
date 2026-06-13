# Cron Job State Transitions — Heartbeat Analysis Patterns

## State Machine Overview

| State | Description | Heartbeat Signal | Action |
|---|---|---|---|
| `scheduled` | Waiting for next scheduler tick | `last_status: null` or `ok`, `state: scheduled` | Normal — no action |
| `running` | Job dispatched, executing | `state: running`, `last_run_at` updated | Monitor duration >45m → stuck |
| `completed` | Job finished successfully | `last_status: ok`, `state: scheduled` | Normal — no action |
| `failed` | Job execution failed | `last_status: failed/error`, `last_error` populated | P0 flag if recurring |
| `error` | Critical failure | `last_status: error`, `last_error` populated | P0 flag if recurring |

## Common State Transition Patterns

### 1. Successful Execution Loop
```
scheduled → running → completed → scheduled
```
- `last_run_at` advances on each cycle
- `last_status: ok`
- `state` returns to `scheduled`
- **Heartbeat Response**: Normal operation, no flags

### 2. Recovered Job (Transient Failure)
```
scheduled → running → failed/error → scheduled
                              ↓
                         scheduled → running → completed → scheduled
```
- `last_status: error` or `failed` → `last_status: ok` on subsequent run
- `last_error` populated for failed attempt
- **Heartbeat Response**: Note as recovered — if no new failure in 48h, no alert

### 3. Stuck Job (Hung Execution)
```
scheduled → running (state=running, last_run_at stale >45m)
```
- `state: running` persists beyond expected completion time
- `last_run_at` not updated for >45 minutes
- `next_run_at` may still advance (scheduler API alive, execution loop dead)
- **Heartbeat Response**: P0 STUCK job — requires gateway restart Investigation

### 4. Dead Execution Loop (Scheduler API Alive, Execution Loop Dead)
```
next_run_at advances repeatedly (>1 hour in past)
last_run_at = null OR last_run_at >48h stale
```
- Scheduler API layer accepting commands and updating `next_run_at`
- Execution loop not dispatching jobs
- `last_run_at` stationary while `next_run_at` moves
- **Heartbeat Response**: P0 DEGRADED — gateway restart required

### 5. Never-Run Job (Sentinel Pattern)
```
created_at >24h ago, last_run_at = null, repeat.completed = 0
next_run_at in future
```
- Job created but never executed
- May be valid if not yet due (check `schedule_display` vs `next_run_at`)
- **Heartbeat Response**: P3 INFO — note for monitoring if persists beyond expected due time

### 6. Null Toolsets Bug
```
enabled_toolsets: null
next_run_at advances normally
last_run_at stagnant
```
- Known scheduler bug where jobs lack required toolsets configuration
- Job appears normal but silently skipped on execution
- **Heartbeat Response**: P1 WATCH — check job creation source for toolsets missing

## Job JSON Field Health Mapping

| Field | Expected Value | Problem Signal | Severity |
|---|---|---|---|
| `state` | `scheduled` or `completed` | `running` >45m | P0 STUCK |
| `last_status` | `ok` or `null` | `failed` or `error` | P0 FAILED |
| `last_error` | `null` | populated | P0 FAILED (if recent) |
| `last_run_at` | Recent (within 2x interval) | stale >45m | P0 STUCK |
| `next_run_at` | Future | past >1h | P0 DEGRADED (if last_run_at stale) |
| `enabled_toolsets` | Non-null array | `null` | P1 WATCH |
| `repeat.completed` | Incrementing | stagnant | P0 STUCK or P3 NEVER-RUN |

## Dedup window logic

- **Same findings** within 48h = DUP, suppress delivery
- **State change** (failed→ok, ok→failed) = alert, reset dedup window
- **New job introduced** = alert, even if status matches existing pattern
- **Known pattern** (e.g., external-feature-daily security block, weekly jobs not-due) = log message, DUP if identical to prior run