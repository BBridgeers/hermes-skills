# Cron Jobs JSON Schema — Field Reference

This document defines every field in `/root/.hermes/cron/jobs.json`, maps it to health signals, and explains how to detect issues.

## Top-Level Structure

```json
{
  "jobs": [
    {
      // required fields
      "id": "uuid",
      "name": "string",
      "prompt": "string",
      "schedule": { "kind": "cron|interval", "expr": "string", "display": "string" },
      "repeat": { "times": null|integer, "completed": integer },
      "enabled": boolean,
      "state": "scheduled|running|paused",
      "created_at": "ISO8601",
      "next_run_at": "ISO8601|null",
      "last_run_at": "ISO8601|null",
      "last_status": "ok|failed|error|null",
      "last_error": "string|null",
      "enabled_toolsets": ["terminal"|"file"|"web"|"skills"|"search"],
      // optional/specialized fields
      "skills": ["skill-name", ...],
      "skill": "skill-name",
      "deliver": "local|webhook",
      "last_delivery_error": "string|null"
    }
  ]
}
```

## Field Health Signal Mapping

| Field | Type | Critical for P0? | Health Signal |
|-------|------|------------------|---------------|
| `last_status` | string (`ok`/`failed`/`error`) | **YES** | Core failure flag |
| `last_error` | string | **YES** | Failure description |
| `next_run_at` | string/ISO8601 or null | **YES** | Scheduler liveness indicator |
| `last_run_at` | string/ISO8601 or null | **YES** | Execution proof |
| `state` | string (`scheduled`/`running`) | **YES** | Stuck job detection |
| `last_status: "failed"` | status enum | **P0** | Failed job |
| `last_status: "error"` | status enum | **P0** | Failed job (error condition) |
| `state: "running"` + `last_run > 45min` | state enum + timestamp | **P0** | Stuck job |
| `next_run_at` in the past (1h+) + `last_run_at` null or >48h | timestamp comparison | **P0** | Dead execution loop |
| `last_run_at: null` + `repeat.completed: 0` + created >24h + `next_run_at` future | job metadata | **P2 WATCH** | Never-run sentinel |
| `enabled_toolsets: null` | config | **P1 WATCH** | Silent failure |
| `last_delivery_error` | string | **P0** | Slack delivery issue |
| `repeat.completed` | integer | context-dependent | Execution count tracking |

## Detailed Field Analysis

### `last_status`

**Values**: `ok`, `failed`, `error`, `null`

**Health signal**:

- `failed` or `error` → **P0 FAILED** (job execution problem)
- `null` → job never ran (sentinel check below)
- `ok` → last run succeeded

**Pitfall**: `last_status: "error"` due to tirith security blocks (`exfil_curl_auth_header`) is **expected behavior**, not gateway decay. Flag as expected but don't escalate unless recurring.

### `last_error`

**Type**: string or null

**Content**:

- `null` → no error, last run OK (if `last_status: ok`) or not attempted
- Non-null → error message from job execution or scheduler

**Critical patterns**:

- `Blocked: prompt matches threat pattern 'exfil_curl_auth_header'` → Security scanner blocked the job (expected for proactive-repo jobs).
- `Request failed after 3 retries` → External API transient failure (watch, not urgent)
- `Failed to send message to Slack` → `last_delivery_error` is also present
- `Permission denied` or `No such file or directory` → Script/config issue (P1)

### `next_run_at`

**Type**: ISO8601 timestamp or null

**Health signal**:

- In the **future** (within expected window) → scheduler alive, job scheduled
- In the **past** >1 hour → scheduler alive but dead loop (if `last_run_at` unchanged)
- `null` → never scheduled (immediate P0 if job is enabled)

**Pitfall**: `next_run_at` moving does NOT prove the scheduler works — only `last_run_at` proves execution.

### `last_run_at`

**Type**: ISO8601 timestamp or null

**Health signal**:

- Non-null, recent (within expected window) → execution working
- `null` + job created >24h → never-run sentinel (P2)
- `null` + `next_run_at` past >1h → dead loop signature

**P0 signature**: `next_run_at` in the past (>1h) AND `last_run_at` null or >48h stale.

### `state`

**Type**: `scheduled`, `running`, `paused`

**Health signal**:

- `running` + persists >45 min → stuck job (P0)
- `paused` + `enabled: true` → unexpected (P1)

### `enabled_toolsets`

**Type**: Array of strings or `null`

**Health signal**:

- `null` → **P1 WATCH** (known bug: jobs can be created without toolsets, silently skipped by scheduler)
- Non-empty array → normal

**Pitfall**: Jobs with `enabled_toolsets: null` will advance `next_run_at` but never execute, causing `last_run_at` to stagnate. Flag as P1, not P0.

### `last_delivery_error`

**Type**: string or null

**Health signal**:

- Non-null → Slack delivery failed (gateway may be down, API key invalid, or channel unreachable)
- `null` → delivery OK or not attempted

### Job Categories

| Category | `last_status` | `last_error` | `enabled_toolsets` | `next_run_at` | `last_run_at` | Diagnosis |
|----------|---------------|--------------|-------------------|---------------|---------------|-----------|
| Healthy | `ok` | `null` | Valid array | Future | Recent | No action |
| Failed | `failed` or `error` | Non-null | Valid array | Past/Next | Old | P0 FAILED |
| Stuck | `running` | `null` | Valid array | Past/Next | Old | P0 FAILED (stuck) |
| Dead loop | Any | Any | Valid array | Past >1h | `null` or >48h | P0 DEGRADED |
| Never-run | `null` | `null` | Valid array | Future | `null` | P2 WATCH |
| Silent skip | Any | `null` | `null` | Future | Stagnant | P1 WATCH (toolsets null bug) |
| Delivery fail | Any | Any | Valid array | Future | Recent | P0 FAILED (Slack only) |

## Dedup Pattern Reference

| Pattern | Dedup Key | Rule |
|---------|-----------|------|
| Failed job | `job.id + job.name + error hash` | Same job+error hash → suppress |
| Stuck job | `job.id + job.name` | Same stuck job → suppress (don't spam every 5m) |
| Dead loop | `gateway` | Single global "gateway dead loop" flag |
| Toolsets null | `job.id` | Same job with null toolsets → suppress after first |
| Never-run sentinel | `job.id` | Same never-run job → suppress after first |
| Delivery fail | `job.id + gateway` | Slack gateway issue → global dedup |

## Field Reference — Complete List

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string (UUID) | YES | Unique job identifier |
| `name` | string | YES | Human-readable job name |
| `prompt` | string | YES | Full prompt presented to agent |
| `skills` | array of strings | NO | Skill names (legacy, use `skill`) |
| `skill` | string | NO | Single skill name (preferred over `skills`) |
| `model` | string | NO | Override model (null = default) |
| `provider` | string | NO | Override provider (null = default) |
| `base_url` | string | NO | Override base URL (null = default) |
| `script` | string | NO | Path to shell script (relative to ~/.hermes/scripts/) |
| `schedule` | object | YES | Scheduler config |
| `schedule.kind` | string | YES | `cron` or `interval` |
| `schedule.expr` | string | YES | Cron expression or interval value |
| `schedule.display` | string | YES | Human-readable schedule |
| `schedule_display` | string | YES | Alias for `schedule.display` |
| `repeat.times` | integer or null | YES | Limit (null = forever) |
| `repeat.completed` | integer | YES | Executions so far |
| `enabled` | boolean | YES | Whether job is enabled |
| `state` | string | YES | `scheduled`, `running`, or `paused` |
| `paused_at` | ISO8601 or null | YES | Pause timestamp |
| `paused_reason` | string or null | YES | Pause reason |
| `created_at` | ISO8601 | YES | Job creation timestamp |
| `next_run_at` | ISO8601 or null | YES | Next dispatch time |
| `last_run_at` | ISO8601 or null | YES | Last execution time |
| `last_status` | string or null | YES | `ok`, `failed`, `error`, or null |
| `last_error` | string or null | YES | Last error message |
| `last_delivery_error` | string or null | YES | Slack delivery error |
| `deliver` | string | YES | Delivery target (`local` or `webhook`) |
| `origin` | string or null | YES | Origin (e.g., `webui`, `skill`) |
| `enabled_toolsets` | array or null | YES | Allowed toolsets |
| `workdir` | string or null | NO | Working directory |
