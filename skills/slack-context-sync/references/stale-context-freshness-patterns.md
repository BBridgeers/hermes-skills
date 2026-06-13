# Stale Context Freshness Patterns

## Scenario: Sync script returns empty but context file is hours old

**Pattern observed:**
- `sync-context.sh` returns empty output (exit code 0)
- Context file timestamp shows it's several hours old (6+ hours)
- Session search shows only routine cron sessions
- No recent file modifications or activity indicators

**Interpretation:**
This indicates a "quiet period" where no significant activity occurred across channels, but the context file hasn't been refreshed due to the sync script's staleness checks.

**Recommended action:**
Even when the sync script returns empty, if the context file is >4 hours old, perform a manual refresh by:
1. Running comprehensive session search with multiple query patterns
2. Checking alternative activity indicators (logs, articles, file mods)
3. If still no new activity, update the context file with a "system status stable" note and refreshed timestamp

**Rationale:**
Context files older than 4 hours risk becoming stale even if no new activity occurred. Regular timestamp refreshes maintain the perception of "currentness" across channels.

**Example update when stale:**
```
# Active Context — <current UTC timestamp>

## Current Source
Cron (slack-context-sync heartbeat) — <model>

## Active Project
System maintenance — no new activity detected

## Recent Topics
- System status stable — no new activity in last 6 hours
- All cron jobs running normally
- No pending user actions requiring attention

## Key Decisions
- Maintain current configuration and monitoring

## Pending Actions
- [ ] Continue routine monitoring

## Key Files
- ~/.hermes/slack-context.md — context refresh

## Last Message
Heartbeat refresh: System status stable, no new activity detected. Context timestamp updated for freshness.
```

**Threshold:** Refresh context file if >4 hours old, regardless of sync script output.