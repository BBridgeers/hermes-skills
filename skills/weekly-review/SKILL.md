---
name: Weekly Review
description: KALM retrospective grounded in objective metrics, with closed-loop tracking of last week's actions and SMART next-week actions
tags: [meta, review, operations]
---

## Why this skill exists

A weekly review is only valuable if (a) findings rest on objective data, not vibes, and (b) findings turn into **specific actions that get checked next week**. This skill enforces both: pull metrics from multiple sources, frame findings as KALM (Keep/Add/Less/More), and emit each action as SMART (specific, measurable, owner, deadline) so the next run can audit follow-through.

## Inputs (gather all before writing)

Read in this order. If any source is empty or missing, note it explicitly in the article — don't silently skip.

1. **Context** — `~/.hermes/memories/MEMORY.md` for goals and system knowledge; `~/.hermes/SOUL.md` for voice and identity (skip if empty or blocked).
2. **Activity logs** — `terminal("hermes logs agent --since 7d", timeout=30)` to capture all agent activity. Also `terminal("hermes logs errors --since 7d --level ERROR", timeout=30)` for failures. Parse for session counts, tool errors, gateway events, and skill invocations. **PITFALL**: agent.log rotates daily — `--since 7d` only scans the current log file, not rotated logs. If the output is suspiciously short (<200 lines for a high-frequency cron setup that generates 500+ sessions/day), the log has rotated. Check for rotated logs with `ls -la ~/.hermes/logs/agent.log*` and grep them individually if needed. Mark affected metrics as `_degraded source_`.
3. **Session activity** — `terminal("hermes sessions list --limit 500", timeout=10)` to count sessions this week (500 covers ~24h at typical cron density; for quiet systems 200 is fine). Also `terminal("hermes sessions stats", timeout=10)` for total session counts across the DB. Use `session_search()` to find activity relevant to specific areas (e.g. "cron job", "skill failure", "deployment").
4. **Cron job health** — `terminal("hermes cron list", timeout=10)` to see active jobs and their next-run times. **Explicitly count jobs in error state** — grep for `error:` in the output. Each error-state job is a finding candidate. Check `~/.hermes/logs/agent.log` for cron-triggered session IDs and grep for task outcomes. Also pull the most recent cost report (`ls -t ~/.hermes/articles/cost-report-*.md | head -1`) for spend metrics — it provides session counts, model distribution, and burn rate that enrich the metrics table.
5. **Errors and warnings** — `terminal("hermes logs errors --since 7d", timeout=30)` for the full error log. Count distinct error types, cluster by component (tools, gateway, plugins, agent), note recurring patterns.
6. **Code and skill activity** — If `~/.hermes` is in a git repo: `terminal("git log --since=\"7 days ago\" --pretty=format:\"%h %s\"", workdir=\"/root/.hermes\")`. If not a repo, use `search_files(target='files', pattern='SKILL.md', path='~/.hermes/skills')` to count skills and check modification times.
7. **Prior review** — The most recent `~/.hermes/articles/weekly-review-*.md`. Extract its "Next week — actions" section — you will audit those actions in step 1 below.

## Steps

### 1. Close the loop on last week's actions (do this FIRST)

For each action item in the prior weekly-review's "Next week — actions" checklist:

- Did it ship? Check the agent log + session history + git log for evidence.
- If yes: note as **shipped** with the log line, session ID, or commit that proves it.
- If no: classify as **slipped** (still relevant, carry over), **abandoned** (no longer needed, explain why), or **blocked** (needs unblocking — name the blocker).

If there is no prior weekly-review, write `_No prior review to audit — this is the baseline._` and continue.

### 2. Compile objective metrics

A short table at the top of the article. Use exact numbers from inputs above.

| Metric | This week | Prior week (if known) | Δ |
|---|---|---|---|
| Sessions (total) | N | M | ±X |
| Sessions (cron-triggered) | N | — | — |
| ERROR events | N | — | — |
| WARNING events | N | — | — |
| Distinct error types | N | — | — |
| Cron jobs active | N | — | — |
| Skills present | N | — | — |
| Articles written | N | — | — |
| Commits (if git repo) | N | — | — |
| API spend (from cost report) | $X | $Y | ±Z |

If you can't compute prior-week numbers (no prior article, missing data), leave the column blank — don't fabricate.

### 3. KALM findings, prioritized

Group findings into four buckets. **Each finding must cite at least one log line, session ID, error trace, or commit** as evidence — no unsupported claims.

- **Keep** — what's working and should continue unchanged (healthy cron jobs, fast responses, stable skills).
- **Add** — capabilities or monitoring missing this week that would have helped (missing alerts, unlogged failures, blind spots).
- **Less** — things consuming resources without proportional value (recurring warnings that don't matter, noisy error patterns, sessions that achieved nothing).
- **More** — things that worked but are under-invested (a skill producing high-signal output that only ran once, a monitoring pattern that caught something important).

After listing, score each finding by **Frequency × Impact ÷ Effort** (1-5 each). Compute the priority number; sort descending. Keep the top 5; drop the rest. Generic items ("improve monitoring") fail the priority threshold and must be dropped or rewritten with specific data.

### 4. Translate top findings into SMART next-week actions

For each of the top 3-5 prioritized findings, write a next-week action in this exact shape:

```
- [ ] {action verb} {specific change} in {file/skill/path} by {YYYY-MM-DD}
  - Why: {finding it addresses}
  - Done when: {observable outcome — a file exists, a metric crosses a threshold, a skill runs clean for 7 days}
```

Owner is implicitly Hermes. Deadline must be within the next 7 days. If you can't write an action that concrete, the finding wasn't ready — drop it and note why.

### 5. Compare to goals in MEMORY.md

For each goal or priority listed in `~/.hermes/memories/MEMORY.md`:
- **Progress** — cite the specific log line, session, or commit that moved it forward.
- **Stalled** — name the blocker.
- **Retire/revise** — propose explicitly if the goal no longer matches reality.

If MEMORY.md has no concrete goals (placeholder content only), flag that as itself an Add finding.

### 6. Write the article

Save to `~/.hermes/articles/weekly-review-${today}.md`. Required structure:

```markdown
# Weekly Review — ${today}

## TL;DR
{one paragraph: the single most important thing this week + the #1 action for next week}

## Last week's actions — closed loop
{from step 1}

## Metrics
{table from step 2}

## Findings (KALM, prioritized)
### Keep
### Add
### Less
### More

## Next week — actions
{from step 4, as the SMART checklist}

## Goals progress
{from step 5}

## Notes
{anything worth recording but not actionable: trivia, half-formed observations, interesting session patterns}
```

### 7. Send the notification (gated)

Use `send_message` to Slack. Send **only if there is signal worth sharing**. Skip the notification (and note the skip in the article) if all of these hold: zero ERROR events, zero next-week actions ranked priority ≥10, and no blocked/slipped actions from the prior week. A silent week deserves a silent notification.

When you do notify, lead with the action, not the count:

```
*Weekly Review — ${today}*
Top action: {the #1 SMART action, in one line}
Health: N sessions, K errors, J warnings
Full review: ~/.hermes/articles/weekly-review-${today}.md
```

### 8. Log to memory

Append to `~/.hermes/memories/MEMORY.md`:

```
§
Weekly review ${today}: {one-line TL;DR}. Metrics: N sessions, K errors. Top action: {one-line SMART action}. Closed-loop: X shipped / Y slipped / Z abandoned of N prior. Article: ~/.hermes/articles/weekly-review-${today}.md
```

## Data source reference

See `references/operational-pitfalls.md` for log rotation workarounds and bare-metal/Docker DNS failure patterns.

| Aeon source | Hermes equivalent |
|---|---|
| `memory/MEMORY.md` | `~/.hermes/memories/MEMORY.md` |
| `soul/SOUL.md` | `~/.hermes/SOUL.md` |
| `memory/logs/YYYY-MM-DD.md` | `hermes logs agent --since 7d` + `hermes sessions list` |
| `./scripts/skill-runs --hours 168 --json` | `hermes cron list` + parse agent.log for cron-triggered sessions |
| `memory/cron-state.json` | `hermes cron list` (status) + agent.log grep for cron outcomes |
| `memory/issues/INDEX.md` | `hermes logs errors --since 7d` (cluster errors by type) |
| `git log --since="7 days ago"` | `terminal("git log --since=\"7 days ago\" ...", workdir="/root/.hermes")` |
| `articles/cost-report-*.md` | `ls -t ~/.hermes/articles/cost-report-*.md \| head -1` (most recent) |
| `articles/weekly-review-*.md` | `~/.hermes/articles/weekly-review-*.md` |
| `./notify` | `send_message` (to Slack) |
| Session search | `session_search()` tool |

## Constraints

- **Evidence required.** Every finding cites a log line, session ID, error trace, or commit. No unsupported claims.
- **No generic actions.** "Improve monitoring" is a finding, not an action. If you can't make it SMART, drop it.
- **Audit before generating.** Always run step 1 (close the loop) first — skipping it breaks the feedback cycle this skill exists to enforce.
- **Don't pad.** A short, sharp review beats a long, mushy one. If only 2 findings clear the priority threshold, write 2.
- **Voice.** If `~/.hermes/SOUL.md` is populated, match it in the TL;DR and notification. Otherwise neutral and direct.
- **Data degradation.** If `hermes logs` returns empty (log rotation, new install), note it and use `hermes sessions list` + `hermes sessions stats` as fallback activity metrics. Mark the affected rows in the metrics table as `_degraded source_`.
