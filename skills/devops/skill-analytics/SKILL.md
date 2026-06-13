---
name: skill-analytics
description: Weekly fleet-level skill-run analytics — ranks skills by 7d run count, surfaces success rates, exit-taxonomy distribution, and anomaly flags (significance-gated). The only place the operator sees the entire fleet ranked side-by-side.
tags: [meta, devops, monitoring]
---

# Skill Analytics — Fleet-Level Observability

> Adapted from Aeon's skill-analytics. Hermes has no GitHub Actions — runs are tracked via cron jobs, session history, and daily log files.

## Purpose

Generate a fleet-level performance view of every Hermes skill that has run in the window. **Answer four questions in one report:** which skills run most, which fail most, which are silently skipping, and which scheduled skills haven't fired at all. `hermes-heartbeat` gives binary ok/not-ok per run; `skill-repair` diagnoses one skill at a time. This is the only place the operator sees the entire fleet ranked side-by-side.

## Window

Default: 168 hours (7 days). The user may specify a different window by passing a number when invoking this skill (e.g., "Run skill-analytics with a 72-hour window"). Cap at 720 hours (30 days). Compute `WINDOW_HOURS=N` and `WINDOW_LABEL` (e.g. "last 7d" or "last 72h").

## Step 1: Pull the cron run snapshot

Hermes skills can be triggered two ways: by cron jobs (server-initiated) and by user/agent invocation (session-based). Start with cron jobs — they are the closest analog to GH Actions runs.

```
cronjob(action='list')
```

Parse the output. For each cron job whose `command` field references a skill (look for `skill:` prefix, skill names, or `SKILL.md` paths), extract:
- `skill_name` — derive from job name or command
- `last_run` — timestamp of last execution
- `last_status` — "succeeded", "failed", or "running"
- `schedule` — the cron expression
- `enabled` — whether the job is active

Build `CRON_SKILLS`: an array of `{skill_name, last_run, last_status, schedule, enabled}`.

If `cronjob(action='list')` returns empty or errors out:
- Log `SKILL_ANALYTICS_NO_DATA — cronjob list returned empty (no cron jobs configured?)` to `~/.hermes/logs/DATE.md` and stop with **no notification**. A silent fleet view is correct on data-fetch failure.

## Step 2: Pull session-based skill invocations

Search session history for skill invocations in the window using `session_search`:

```
session_search(query="skill:", limit=200)
session_search(query="SKILL.md", limit=200)
session_search(query="skill_view", limit=200)
```

Parse results to find which skills were invoked and when. Cross-reference with the `CRON_SKILLS` list so cron-invoked runs aren't double-counted. Build `SESSION_SKILLS`: an array of `{skill_name, invocation_count, last_seen}`.

Merge `CRON_SKILLS` and `SESSION_SKILLS` into a unified `SKILL_RUNS` array:

```json
[
  {
    "skill": "name",
    "total": N,
    "success": N,
    "failure": N,
    "last_run": "ISO timestamp",
    "last_conclusion": "success|failure|unknown"
  }
]
```

For cron jobs: `success` = count of cron runs with "succeeded" status; `failure` = count with "failed". For session invocations: mark as `success` unless session_search reveals error markers.

## Step 3: Cross-reference scheduled skills (zero-run detection)

Build `SCHEDULED_SKILLS` from the cron job list: `{skill_name -> {enabled: bool, schedule: str}}`. For every skill where `enabled: true` AND schedule is a valid cron expression AND the skill is **not** present in `SKILL_RUNS`, mark `silent_scheduled: true` (zero runs in window despite an active schedule).

Skills triggered only by user invocation (no cron schedule) are exempt from silent-scheduled detection.

## Step 4: Load persistent state

Check `~/.hermes/state/skill-analytics-state.json`. If absent, create `{}`. This file tracks per-skill state across runs:
- `consecutive_failures` (int, 0 if missing)
- `last_status` (string, "unknown" if missing)

Used to compute the consecutive-failure anomaly without multiple session searches.

Read the file and attach these fields to each skill in `SKILL_RUNS`.

## Step 5: Mine exit taxonomy from daily logs

Scan `~/.hermes/logs/YYYY-MM-DD.md` for each date in the window (use `search_files` or `read_file`). Look for these exit markers (one match per skill section):

| Marker | Classification |
|--------|---------------|
| `_OK` (excluding `_OK_SILENT`) | ok |
| `_OK_SILENT`, `_QUIET`, `SKIP_QUIET` | quiet |
| `SKIP_UNCHANGED` | skip_unchanged |
| `NEW_INFO` | new_info |
| `_SKIP*` (other) | skip_other |
| `_ERROR`, `_FAILED` | error |
| `_PARTIAL` | partial |
| (no match) | uncategorized |

Build `EXIT_DIST[skill]` = `{ok, quiet, skip_unchanged, new_info, skip_other, error, partial, uncategorized}`. Dominant bucket = largest count; ties broken in the order above. No log markers → dominant bucket = "uncategorized".

This is best-effort regex matching from human-written logs. A miss-rate of 10–20% is expected. Cron success/failure counts from Step 1 remain the ground truth for pass/fail. The taxonomy is a secondary signal.

## Step 6: Anomaly classification

For each skill in `SKILL_RUNS` OR `silent_scheduled`, assign **at most one** anomaly flag, first match wins:

| Flag | Trigger |
|------|---------|
| `🔴 SILENT` | `silent_scheduled: true` (enabled cron skill, zero runs in window) |
| `🔴 ALL_FAIL` | `total >= 2` AND `failure == total` |
| `🟠 CONSECUTIVE_FAILURES` | `consecutive_failures >= 3` (from state) |
| `🟠 LOW_SUCCESS` | `total >= 3` AND `success / total < 0.80` |
| `🟡 ALL_SKIP` | `total >= 3` AND `EXIT_DIST.ok + EXIT_DIST.quiet + EXIT_DIST.new_info == 0` AND `EXIT_DIST.skip_unchanged + EXIT_DIST.skip_other > 0` |
| `🟡 DUPLICATE_RUNS` | `total > 2 × expected_runs(schedule, window)` |

`expected_runs(schedule, window)` is a coarse estimate: for hourly cron (`0 * * * *`) over 7 days, expect 168; for daily (`0 H * * *`), expect 7; for every-6-hours (`0 */6 * * *`), expect 28. If unparseable, skip duplicate check.

A skill with no flag is HEALTHY.

## Step 7: Compute summary

```
total_runs:          sum of every skill's total
distinct_skills:     count of skills with total >= 1
overall_success_pct: succeeded / (succeeded + failed) × 100
anomaly_count:       count of skills with any flag
silent_scheduled_count: count of SILENT flags
exit_dominant:       top 3 dominant exit buckets fleet-wide
```

## Step 8: Build the verdict line

Pick the strongest single claim, in priority:

1. Any `🔴 SILENT` → `"N scheduled skill(s) didn't run this window — {first_skill}"`
2. Any `🔴 ALL_FAIL` → `"{first_skill} failed every run (N/N) — investigate"`
3. Any `🟠 CONSECUTIVE_FAILURES` → `"{first_skill} on N-run failure streak"`
4. Any `🟠 LOW_SUCCESS` → `"{first_skill} {pct}% success over {total} runs — degraded"`
5. Any `🟡 ALL_SKIP` → `"N skill(s) only emitting skip-class exits — verify intent"`
6. Otherwise → `"All {distinct_skills} active skills healthy — {overall_success_pct}% success across {total_runs} runs"`

## Step 9: Significance gate

**Notify only if `anomaly_count >= 1`.** A clean fleet produces zero notifications. Still write the report to `~/.hermes/logs/DATE.md` regardless, so the operator has the latest state.

If gate says skip, log `SKILL_ANALYTICS_QUIET` (no anomalies) and stop. The report is still written — only the push notification is gated.

## Step 10: Write the analytics report

Write to `~/.hermes/logs/skill-analytics-{DATE}.md`. Overwrite if it exists (idempotent same-day reruns).

```markdown
# Skill Analytics — {today}

**Verdict:** {verdict_line}

*Window: {WINDOW_LABEL} · {total_runs} runs across {distinct_skills} skills · {overall_success_pct}% success · {anomaly_count} anomalies*

## Anomalies

| Flag | Skill | Detail | Action |
|------|-------|--------|--------|
| 🔴 SILENT | name | scheduled `<cron>` but zero runs | check cron scheduler |
| 🔴 ALL_FAIL | name | N/N failed | investigate root cause |
| 🟠 CONSECUTIVE_FAILURES | name | N-run streak (last_error: "...") | see skill-repair |
| 🟠 LOW_SUCCESS | name | N% over M runs | review failures |
| 🟡 ALL_SKIP | name | M runs, all skip-class | confirm intent |
| 🟡 DUPLICATE_RUNS | name | M runs, expected ~K | check triggers |

(If `anomaly_count == 0`: write `No anomalies — fleet healthy across {distinct_skills} skills.`)

## Top runners (by run count)

| # | Skill | Runs | Success | Last status | Dominant exit |
|---|-------|------|---------|-------------|---------------|
| 1 | name  | N    | XX%     | success     | ok            |

(Top 15 by total runs desc.)

## Failure rate (sorted, >=1 failure)

| Skill | Runs | Failures | Success rate | Last conclusion |
|-------|------|----------|--------------|-----------------|

(If none: "Zero failures across {distinct_skills} skills this window.")

## Exit taxonomy distribution

| Bucket | Count | % | Top skills |
|--------|-------|---|------------|
| ok            | N | XX% | a, b, c |
| skip_unchanged | N | XX% | d, e |
| quiet         | N | XX% | g |
| error         | N | XX% | h |
| uncategorized | N | XX% |   |

## Silent scheduled skills (enabled, zero runs)

{list of {skill, schedule} pairs OR "none — every enabled cron skill ran at least once."}

## Source status

- Cron jobs: {ok|empty|list_error}
- Session search: {ok|empty}
- Window: {WINDOW_HOURS}h
- State file: {ok|missing — first run?}
- Daily logs scanned: {N_LOG_FILES} for exit taxonomy

---
*Companion to `skill-repair` (per-skill diagnosis/fix) and `hermes-heartbeat` (per-run pulse). Fleet-wide observability is the gap this skill closes. Methodology: cron job history is ground truth for pass/fail; daily-log markers are best-effort secondary signal for exit taxonomy.*
```

## Step 11: Send notification (only if gate from Step 9 passed)

Use `send_message` to the configured Slack channel (check `~/.hermes/config.yaml` for channel name, default to `#hermes`):

```
*Skill Analytics — {today}*
{verdict_line}

Window: {WINDOW_LABEL} · {total_runs} runs · {distinct_skills} skills · {overall_success_pct}% success
Anomalies: {anomaly_count}

{If 🔴 flags (top 3):}
🔴 Critical:
- {skill} — {flag}: {detail}

{If 🟠 flags (top 3):}
🟠 Degraded:
- {skill} — {flag}: {detail}

{If 🟡 flags (top 3, only if no 🔴/🟠 filled slots):}
🟡 Watch:
- {skill} — {flag}: {detail}

Top by runs: {top_3_skills_by_run_count_with_counts}

Full: ~/.hermes/logs/skill-analytics-{today}.md
```

Cap at ~3500 chars. Drop "Top by runs" first if exceeded.

## Step 12: Update persistent state

Write updated `~/.hermes/state/skill-analytics-state.json`:

```json
{
  "last_run": "{ISO timestamp}",
  "window_hours": N,
  "skills": {
    "skill_name": {
      "consecutive_failures": N,
      "last_status": "success|failure",
      "last_anomaly_flag": "flag or null"
    }
  }
}
```

Update `consecutive_failures` per skill: increment by 1 if this run was a failure, reset to 0 if success.

## Step 13: Log to daily log

Append to `~/.hermes/logs/{today}.md`:

```
## Skill Analytics
- **Skill**: skill-analytics
- **Window**: {WINDOW_LABEL} ({WINDOW_HOURS}h)
- **Total runs**: {total_runs} across {distinct_skills} skills
- **Overall success rate**: {overall_success_pct}%
- **Anomalies**: {anomaly_count} (🔴 {red_count}, 🟠 {orange_count}, 🟡 {yellow_count})
- **Silent scheduled**: {silent_scheduled_count} skills
- **Top runner**: {top_skill} ({top_runs} runs)
- **Exit dominant**: {exit_dominant_summary}
- **Verdict**: {verdict_line}
- **Notification sent**: {yes|no — quiet (no anomalies)}
- **Status**: SKILL_ANALYTICS_OK | SKILL_ANALYTICS_QUIET | SKILL_ANALYTICS_NO_DATA
```

## Exit taxonomy

| Status | Meaning | Notify? |
|--------|---------|---------|
| `SKILL_ANALYTICS_OK` | snapshot fetched, >=1 anomaly flagged | Yes |
| `SKILL_ANALYTICS_QUIET` | snapshot fetched, zero anomalies | No (log only) |
| `SKILL_ANALYTICS_NO_DATA` | data sources returned empty / fetch failed | No (log only) |

## Constraints

- **Significance-gated.** A clean fleet produces zero notifications. Reports still write so state stays current, but `send_message` is silent.
- **Never invent runs.** If cronjob list returns empty, exit `SKILL_ANALYTICS_NO_DATA` — do not synthesise data from state alone.
- **Best-effort exit-taxonomy parsing.** Log markers are human-written; expect 10–20% miss rate. Drop affected skills into `uncategorized` and continue.
- **Idempotent.** Same-day reruns overwrite the report. Log entries append (one block per run).
- **No issue filing.** This skill does not write to any issue tracker — that belongs to `skill-repair`. Anomalies surface here as flags; persistence and resolution live in skill-repair's domain.
- **Respect invocation-only skills.** Skills with no cron schedule cannot be SILENT — they fire only on demand. Excluding them prevents permanent false positives.
- **send_message is the notification channel.** Hermes uses Slack via `send_message`, not `./notify` or Telegram. Check `~/.hermes/config.yaml` for channel configuration.
