# Heartbeat Search Execution Patterns

## Session Search Strategy Used in May 20, 2026 Cron Session

### Multi-query approach proven effective:
1. **Recent mode baseline**: `session_search()` - gets most recent 3 sessions
2. **Date-based queries**: `session_search(query="May 20")` - finds sessions by calendar date
3. **Skill-name queries**: `session_search(query="hermes-heartbeat OR slack-context-sync")` - finds sessions by invoked skill
4. **Time-window queries**: `session_search(query="2026-05-20 15:")` - hour-based patterns

### File system verification patterns:
```bash
# Check for recent file modifications
find ~/.hermes -type f -mmin -60 -not -path "*/logs/*" -not -path "*/.git/*"

# Check article generation timestamps
ls -la ~/.hermes/articles/

# Verify context file timestamp
stat -c "%y" /root/.hermes/slack-context.md

# Check for recent log directories
ls -la ~/.hermes/logs/ | grep "20260520" | tail -5
```

### When all strategies return only routine cron sessions:
- **slack-context-sync** heartbeat sessions
- **hermes-heartbeat** monitoring sessions
- No user-initiated sessions (CLI or Slack)

### Decision criteria for [SILENT] response:
- ✅ Sync script exit code 0 + no output
- ✅ Context file timestamp recent (< 4 hours)
- ✅ No file modifications in last 60 minutes
- ✅ No new log directories or articles
- ✅ Session search returns only routine cron activity
- ✅ All pending actions already reflected in existing context

### Fresh deployment considerations:
- `~/.hermes/cron/jobs.json` may not exist yet
- Check alternative indicators: logs, articles, file mods
- Use absolute paths (`/root/.hermes/`) for reliability
- Some deployments may have `~/.hermes` resolve to `/root/.hermes/home/.hermes`