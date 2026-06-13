# Find Self-Referencing False Positive

## What happens

The mandatory secondary verification `find` will always catch the heartbeat's
**own** session file because:

1. Heartbeat writes `~/.hermes/slack-context.md` at time T
2. The session JSON file (`session_YYYYMMDD_HHMMSS_xxxxxx.json`) is part of
   the same agent process — its filesystem timestamp will be T+delta (slightly
   newer than the context file)
3. The find command `-newermt '<context-file-timestamp>'` catches it because
   the session file was last touched microseconds after the context file write

## Production example (May 23, 05:12 UTC)

```
Context file timestamp: 2026-05-23 05:12:06
Session file found:    session_20260523_051221_12b9f7.json (05:12:21)
```

The session had 24 messages — it was the heartbeat that created the context
file. All messages were the heartbeat's own tool calls and its final summary.

## Detection: is it self-referencing?

1. Check if the session filename timestamp (`HHMMSS`) matches the heartbeat's
   start time (±60 seconds of the context file timestamp)
2. Read the session's last user message — if it contains the `slack-context-sync`
   skill invocation, it's the current heartbeat
3. Check if the session's message count is under 50 and all tool results are
   cron/heartbeat infrastructure calls (sync-context.sh, find, stat, session_search)

## Resolution

When the only `find` hit is the heartbeat's own session:
- Cross-validate with broader `session_search` queries (date-based, skill-based)
- Check `cron/jobs.json`, `heartbeat.log`, `gateway.log` for other activity
- If all secondary checks come back clean → **[SILENT]** is correct
- The find caught a genuine session file but it's noise, not signal

## Pitfall severity

Low. The protocol worked correctly — it forced investigation which confirmed
no real activity. The cost is 2-3 extra tool calls per heartbeat cycle. This
is acceptable given the catastrophic cost of missing real user sessions (see
`sync-script-false-negative.md` for 366-msg session missed for 14+ hours).
