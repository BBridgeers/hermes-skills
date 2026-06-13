# Session Search Patterns for Slack Context Sync

## When session_search returns limited results (3 sessions max)

### Primary fallback sources:
1. **Heartbeat log**: `~/.hermes/heartbeat.log` - system status, cron job status
2. **Agent log**: `~/.hermes/logs/agent.log` - recent activity timestamps
3. **Cron jobs**: `~/.hermes/cron/jobs.json` - job status and last run times

### Search patterns:
```bash
# Recent heartbeat entries
grep "2026-05-20" /root/.hermes/heartbeat.log | tail -5

# Recent agent activity
tail -10 /root/.hermes/logs/agent.log

# File search for specific topics
search_files path=/root/.hermes pattern="external-feature" target=content limit=10

# Find recently modified files (last 60 minutes)
find /root/.hermes -type f -mmin -60 -name "*.json" -o -name "*.md" -o -name "*.yaml" | head -10

# Check both context files for completeness
ls -la /root/.hermes/slack-context.md /root/.hermes/telegram-context.md
head -3 /root/.hermes/slack-context.md
head -3 /root/.hermes/telegram-context.md
```

### When to maintain existing context:
- If no substantial new information found in logs
- If all findings are within 48h dedup window (already known issues)
- If the only changes are minor status updates without new topics/decisions
- **For cron heartbeat sessions**: If no new developments found, respond with exactly "[SILENT]" to suppress delivery

### JSON input structure for sync-context.sh:
```json
{
  "source": "Cron (slack-context-sync heartbeat) — deepseek-v4-pro",
  "project": "Hermes Post-Migration Stabilization",
  "topics": ["topic 1", "topic 2"],
  "decisions": ["decision 1", "decision 2"],
  "actions": ["action 1", "action 2"],
  "files": ["file/path — description", "file/path2"],
  "last_message": "Brief summary of last exchange"
}
```