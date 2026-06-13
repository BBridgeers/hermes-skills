# Session Crash Recovery — Reconstructing What Was In Progress

## When To Use This

The user's terminal/SSH session died unexpectedly and they ask:
- "What was I working on?"
- "My window closed, what were we doing?"
- "Terminals crashed — what was in progress?"

Or the user appears after an absence with no memory of the last session.

## Recovery Protocol (Ordered By Signal Density)

### Step 1 — Read slack-context.md (Highest Signal)

`~/.hermes/slack-context.md` is the single most information-dense artifact for crash recovery. It contains:
- **Active Project** — what the user was working on
- **Recent Topics** — what was discussed
- **Pending Actions** — the exact TODO list with checkboxes
- **Key Files** — files being modified, with descriptions
- **Last Message** — what the last exchange was about

One read of this file usually answers the question. No other tool call needed.

### Step 2 — session_search for Recent Sessions

If slack-context.md is stale (last updated > 1 hour ago), search for recent sessions:

```
session_search(limit=5, sort="newest")
```

Match the session labels against the active project from slack-context.md. Remember: session labels are derived from the first few messages and can be misleading — don't dismiss a session by its label.

### Step 3 — Check File Modification Timestamps

For project files referenced in slack-context.md, check `ls -lt` to confirm which files were most recently touched:

```bash
ls -lt /opt/hermes/<project>/
```

The most recently modified file is usually where work was happening.

### Step 4 — Cross-Reference Memory

The user's memory store (visible in the system prompt) carries the last known state across sessions. Cross-reference it against slack-context.md — memory may have state that the context file doesn't.

### Step 5 — Read the Most Recent Session File Directly

If `session_search(session_id=...)` returns "not found," the session JSON file may still exist on disk:

```bash
find /root/.hermes/sessions/ -name "session_*.json" -mmin -120 | sort
```

Read the most recent one directly with `python3 -c` to extract the last user messages and see what was in progress.

## Example: DETOXXX Crash Recovery (May 22, 2026)

1. Read slack-context.md → "DETOXXX Section 4 Audit — IN PROGRESS"
2. Session search for "DETOXXX Section" → confirmed Section 3 complete, Section 5 closed
3. Check `/opt/hermes/detoxxx_v2/` timestamps → section_4_master_daily_grids.md modified at 21:44
4. Memory confirms: Section 3 done (618 lines), Section 5 done (10/10)
5. Answer: Section 4 audit was in progress — Master Daily Grids, Task 1 verifying day ranges

## Anti-Patterns

- **Don't lead with session_search** — slack-context.md is faster and more reliable
- **Don't guess** — if the file timestamps don't match the context file's claim, say so
- **Don't report on Fort Knox/security tasks** when the user asked about content work — they're separate threads
