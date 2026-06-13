# Session Disaster Recovery

When chat context vanishes unexpectedly — tab switch, browser refresh, session timeout, or explicit question about "where we left off" — use this workflow to restore state from disk.

## Why This Happens

Hermes sessions are in-memory by default. Context loss occurs when:
- Tab switch + tab reload (browser behavior)
- Session timeout or connection drop
- Model switch between sessions
- Explicit "clear chat" action
- "Where were we?" prompt without session context

## Permanent Recovery Methods

### Method 1: Session Export to Disk (PREFERRED)

**Use when you need *exact* previous session state, including tool calls and reasoning.**

```bash
# Export a session to disk (permanent storage)
hermes sessions export --session-id <SESSION_ID> /root/.hermes/pinned-sessions/<filename>.json

# List existing pinned sessions
ls -la /root/.hermes/pinned-sessions/

# Re-import later (in any new session)
hermes sessions import /root/.hermes/pinned-sessions/<filename>.json
```

**Critical detail**: Add human-readable summary file too:
```bash
# Save human-readable context
cat /root/.hermes/pinned-sessions/<filename>.json | jq '.[0].content' | head -c 2000 > /root/.hermes/RECOVERY-<SESSION_ID>.md
```

**Pro Tip**: Pin frequently-recovered sessions to `/root/.hermes/pinned-sessions/` — they survive container restarts.

---

### Method 2: Session DB Lookup (No Export Available)

**Use when you only have the session ID or can search the DB:**

```bash
# Find recent sessions by topic
session_search(query="vehicle analyzer fb marketplace", limit=3, sort="newest")

# Scroll through a specific session
session_search(session_id="20260506_000848_beabd8", around_message_id=9826, window=20)
```

---

### Method 3: Bash Recovery Alias (Instant Trigger)

**Add to `~/.bashrc` for keyboard-triggered recovery:**

```bash
alias recovery='session_search(query="vehicle analyzer fb marketplace scraper", limit=2, sort="newest")'
```

Then type `recovery` in any new session to auto-recover context.

---

## Quick Recovery Checklist (When Context Loss Happens)

1. **Check if session ID is visible** in current chat (look for `session_id: ...` in tool outputs)
2. **Search session DB** if ID unknown:
   ```
   session_search(query="<project> <task>", limit=3, sort="newest")
   ```
3. **Import pinned session** if exported:
   ```
   hermes sessions import /root/.hermes/pinned-sessions/<filename>.json
   ```
4. **Read human-readable summary**:
   ```
   cat /root/.hermes/RECOVERY-<SESSION_ID>.md
   ```

---

## Prevention Patterns (AVOID Context Loss)

| Pattern | How to Avoid |
|---------|-------------|
| Tab switch → reload | Keep active sessions in a dedicated browser window |
| Session timeout | Use `hermes gateway install` → 8642 port → keep browser tab open |
| Model switch | Stick to one provider per workspace (`hermes chat --provider openrouter`) |
| Explicit clear | Disable "clear chat" button in workspace settings |

---

## When You Need to Export a Session

**Before closing a productive session:**
```bash
# Get current session ID
hermes status | grep "Session ID"

# Export immediately before ending
hermes sessions export --session-id $(hermes status | grep "Session ID" | cut -d: -f2 | tr -d ' ') /root/.hermes/pinned-sessions/$(date +%Y%m%d_%H%M%S)_prod.json
```

**Alternative one-liner** (add to `~/.bashrc`):
```bash
alias pin-current='hermes sessions export --session-id $(hermes status | grep "Session ID" | cut -d: -f2 | tr -d " ") /root/.hermes/pinned-sessions/$(date +%Y%m%d_%H%M%S)_prod.json'
```

---

## Pitfalls to Avoid

| Pitfall | Fix |
|---------|-----|
| `hermes sessions export` says "no sessions found" | Use `hermes sessions list` to verify session still exists in DB |
| Export file is empty | Check `session_id` is correct (format: `YYYYMMDD_HHMMSS_xxxxxx`) |
| Bash alias doesn't work after adding | Run `source ~/.bashrc` after `alias` edit |
| Session DB lookup returns stale data | Add `limit=1` and `sort="newest"` to recent-first search |

---

## Example: Export From Previous Session (This Session)

- **Session ID**: `20260506_000848_beabd8`
- **Title**: Facebook Marketplace Scraping Error Fix
- **Exported**: `/root/.hermes/pinned-sessions/fb_scraper_prior.json`
- **Summary**: `/root/.hermes/RECOVERY-SESSION-20260506_000848_beabd8.md`
