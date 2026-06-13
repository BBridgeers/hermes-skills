---
name: goal-tracker
description: Quantified goal progress with OKR-style status, velocity, trend vs prior snapshot, and one concrete next action per goal
tags: [meta, productivity]
---

# Goal Tracker — Quantified Progress & Accountability

> Adapted from Aeon's goal-tracker. Core methodology: evidence-driven status assignment, trend scoring, one concrete action per goal, safe MEMORY.md updates. Adapted for Hermes: `send_message` to Slack instead of `./notify`, Hermes-native paths (`~/.hermes/memories/`, `~/.hermes/state/`, `~/.hermes/logs/`), `session_search()` as an evidence source, optional git/gh evidence only if repos are present.

## Purpose

Compare current progress against goals defined in MEMORY.md. Compute quantified status (DONE / BLOCKED / ON TRACK / NEEDS ATTENTION / AT RISK), track velocity trends vs the prior run, and propose one concrete action per non-DONE goal. Notify via Slack and persist state for trend comparison on the next run.

## Inputs

**Primary goal source:** `~/.hermes/memories/MEMORY.md` section titled `## Goals`. If absent, fall back to `## Next Priorities`. If both are missing or empty, send via Slack `send_message` a "NO_GOALS" alert and exit.

**Evidence sources (use every source that responds; record each in the source-status footer):**

- `~/.hermes/logs/*.md` — log files from the last 30 days. Case-insensitive whole-word match against keywords parsed from each goal title.
- `session_search(query="<goal-keyword>")` — search recent Hermes session conversations for mentions of each goal.
- `git log --since="30 days ago" --pretty=format:"%ad|%s" --date=short` — commit subjects. Run in any git repos found under `/root/` (try `/root/aeon/`, `/root/Resonate_Freq_Proj/`, and any others discovered via `search_files`).
- `gh pr list` / `gh issue list` — **optional**. Only attempt if `gh` CLI is available and a repo has a GitHub remote configured. If it fails, record `gh=unavailable` and proceed. These are not required for the skill to produce a useful report.

**Prior state:** `~/.hermes/state/goal-state.json` — load for trend comparison if it exists.

## Steps

### 1. Parse goals and prior state

For each goal entry in the `## Goals` section, derive:
- `id` — slugified title (stable across runs, e.g., "ship-hermes-heartbeat" from "Ship hermes-heartbeat")
- `title` — original text exactly as written
- `keywords` — title minus stopwords (also include obvious aliases, e.g., "digest" ↔ "rss-digest", "heartbeat" ↔ "health-check")
- `due` / `target` — parse if present in the bullet (e.g., "by May 15", "target: 50 users"), else null

If `~/.hermes/state/goal-state.json` exists, load `{run_at, goals: {goal_id: {status, activity_count_14d, last_activity_date}}}` for trend comparison.

### 2. Gather evidence per goal

Across all responsive sources, compute for each goal:
- `activity_count_14d` — distinct matching entries in the last 14 days
- `activity_count_30d` — same, 30-day window
- `last_activity_date` — most recent matching evidence (any source); null if none
- `days_since_last_activity` — today minus `last_activity_date`
- `completion_signal` — true if a log entry, session search result, or commit pairs the goal's keywords with phrases like "completed", "done", "shipped", "launched", "closed", "merged", "finished"
- `blocker_signal` — true if any evidence in the last 14 days pairs keywords with "blocked", "waiting on", "stuck on"; capture the blocker phrase

Dedupe evidence by `(source, date, ref)` so a log mentioning a commit doesn't double-count.

### 3. Assign status (apply rules in order — first match wins)

| Status | Rule |
|--------|------|
| DONE | `completion_signal` is true, OR the goal is already marked complete in MEMORY.md (e.g., `~~struck through~~` or moved to ## Completed Goals) |
| BLOCKED | `blocker_signal` is true within the last 14 days |
| ON TRACK | `activity_count_14d >= 2` AND `days_since_last_activity <= 7` |
| NEEDS ATTENTION | `activity_count_14d == 1` OR `days_since_last_activity` between 8 and 14 inclusive |
| AT RISK | `activity_count_14d == 0` AND (`days_since_last_activity > 14` OR no activity ever) |

### 4. Compute trend vs prior snapshot

- `improving` — status moved up the ladder (AT RISK → NEEDS ATTENTION → ON TRACK → DONE) OR `activity_count_14d` rose by ≥50%
- `flat` — same status AND `activity_count_14d` within ±25%
- `degrading` — status moved down OR `activity_count_14d` fell by ≥50%
- `new` — no prior record

### 5. Propose one concrete action per non-DONE goal

Pick the single highest-leverage next step for each goal. Rules:
- **AT RISK** with `days_since_last_activity > 21` → name a specific Hermes skill to enable, a concrete commit, or a file to create (e.g., "Enable `rss-digest` as a cron job to produce weekly digest evidence").
- **BLOCKED** → name the blocker and one unblock step.
- **NEEDS ATTENTION** → name the smallest next deliverable.
- **ON TRACK** → omit action line entirely.

Use one action verb. ≤15 words. No vague "continue monitoring" advice. No action = skip the line, don't fill with filler.

### 6. Format the report

```
*Goal Tracker — ${today}*

Summary: N goals — X at risk, Y needs attention, Z on track, W blocked, V done (overall ↑ improving / → flat / ↓ degrading)

AT RISK (sorted by days_since_last_activity, descending)
• <goal title> — 18d idle, 0 activity/14d (was NEEDS ATTENTION ↓)
  → Action: <one-verb next step>

NEEDS ATTENTION
• <goal title> — 9d idle, 1 activity/14d (new)
  → Action: <one-verb next step>

BLOCKED
• <goal title> — waiting on <blocker> since <date>
  → Action: <unblock step>

ON TRACK
• <goal title> — 3d idle, 5 activity/14d (↑ improving)

DONE
• <goal title> — completed <date>

Sources: logs=ok, session_search=ok, git=ok, gh=unavailable
```

Omit any status section that has zero goals. Use a single `send_message` call to deliver the full report to Slack.

### 7. Update MEMORY.md safely

- Move DONE goals to a `## Completed Goals` section with completion date. **Never delete goals silently.**
- Annotate BLOCKED goals inline with the blocker note, but keep them in the active list.
- Do **not** reorder, rephrase, or rewrite the user's goal text.
- Only write MEMORY.md if at least one goal's status changed since the last run. Otherwise leave the file untouched.

### 8. Persist state

Write `~/.hermes/state/goal-state.json` (create if missing):
```json
{
  "run_at": "YYYY-MM-DDTHH:MM:SSZ",
  "goals": {
    "<goal-id>": {
      "status": "AT_RISK",
      "activity_count_14d": 0,
      "last_activity_date": "YYYY-MM-DD"
    }
  }
}
```

### 9. Notify and log

Send the full formatted report via `send_message` to Slack. If `send_message` is unavailable, log `GOAL_TRACKER_NOTIFY_FAILED` and continue — the state file and log are the authoritative records.

Append to `~/.hermes/logs/YYYY-MM-DD.md`:
```
### goal-tracker
- Tracked: N goals (scope: all)
- Status: X at risk, Y needs attention, Z on track, W blocked, V done
- Trend: <notable shifts vs prior run, or "no prior snapshot">
- Actions proposed: <count>
- Sources: logs=ok, session_search=ok, git=ok, gh=unavailable
```

## Constraints

- Never mark a goal DONE without a concrete completion signal. Prefer false negatives (leaving a finished goal as ON TRACK) over false positives (declaring a goal done prematurely).
- Do not invent, add, reorder, or rephrase goals in MEMORY.md. This skill reads and annotates — it never authors.
- If MEMORY.md has zero goals, exit with NO_GOALS via `send_message` and tell the user exactly which section to add.
- If a single evidence source fails, record it in the source-status footer and proceed with remaining sources. Graceful degradation is the point of multiple sources.
- Use only Hermes-native tools: `read_file`, `write_file`, `search_files`, `session_search`, `send_message`, and `terminal` for git commands.

## Verification

Manual trigger: "Run the goal-tracker skill"
Expected: console output showing the formatted report with status per goal, trend indicators, and concrete actions. Updated `~/.hermes/state/goal-state.json` written. Slack notification sent.
