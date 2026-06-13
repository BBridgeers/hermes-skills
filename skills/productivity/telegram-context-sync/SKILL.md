---
name: telegram-context-sync
description: Sync conversation context between Telegram and VPS terminal instances. Read the latest Telegram context when starting a session or when the user asks "what were we working on."
---

# Telegram Context Sync

## Purpose
Bridge conversation context between Telegram and terminal instances running on the same VPS.

## How It Works
- Telegram sessions save a running context doc at `~/.hermes/telegram-context.md`
- This file is a human-readable markdown summary of the latest conversation state
- The terminal instance reads this file to pick up where Telegram left off

## When to Use
1. **Session start on terminal** — Read `~/.hermes/telegram-context.md` to load recent context
2. **User asks "what were we doing?"** — Read the context file
3. **After completing a task on Telegram** — Update the context file with progress

## Commands
```bash
# Read latest context
cat ~/.hermes/telegram-context.md
```

## Notes
- The context file is overwritten each update (not appended)
- Keep summaries concise — bullet points, not prose
- Include: current topic, pending actions, key decisions, file paths
- Updated by the Telegram agent after significant exchanges
