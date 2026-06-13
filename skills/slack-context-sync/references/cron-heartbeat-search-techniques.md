# Cron Heartbeat Session Search Techniques

## Effective Search Patterns Discovered

### Multi-strategy session search
When `session_search` returns limited results, use multiple query approaches:

```python
# Strategy 1: Recent sessions (default)
session_search(limit=5)

# Strategy 2: Date-based queries  
session_search(query="2026-05-20")

# Strategy 3: Skill-name queries
session_search(query="hermes-heartbeat OR external-feature OR vuln-scanner")

# Strategy 4: Time-window patterns
session_search(query="14:")  # Sessions from 2 PM hour
```

### File system investigation patterns
When session search is insufficient, check file system activity:

```bash
# Find recently modified files
find /root/.hermes -type f -mmin -60 -name "*.json" -o -name "*.md" -o -name "*.yaml" | head -10

# Check agent logs for recent activity
tail -20 /root/.hermes/logs/agent.log

# Verify context file timestamps
ls -la /root/.hermes/slack-context.md /root/.hermes/telegram-context.md
```

### Cross-context verification
Always check both context files for completeness:
- `~/.hermes/slack-context.md` - Primary Slack/Terminal sync
- `~/.hermes/telegram-context.md` - Telegram-specific context

### Silent response protocol
For cron heartbeat sessions with no new developments:
- If no significant changes found after thorough search
- If all issues are already documented and unchanged
- Respond with exactly "[SILENT]" to suppress delivery
- This prevents unnecessary notifications while maintaining freshness checks

### Key file monitoring targets
- `~/.hermes/cron/jobs.json` - Cron job status
- `~/.hermes/skills/external-feature/watched-repos.md` - External feature status
- `~/.hermes/memory/skill-health/cron-state.json` - Skill health status
- `~/.hermes/skills/vuln-scanner/references/vuln-scanned.json` - Vulnerability scan results