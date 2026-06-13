# Fresh Deployment Patterns for Slack Context Sync

When `~/.hermes/cron/jobs.json` doesn't exist (common in fresh deployments), use these alternative activity indicators:

## Primary Activity Signals

1. **Recent session directories** — Check `~/.hermes/logs/` for recently created session directories:
   ```bash
   find ~/.hermes/logs -type d -mmin -60 2>/dev/null
   ```

2. **Article generation** — Look for recently created article files:
   ```bash
   find ~/.hermes/articles -type f -mmin -60 2>/dev/null
   ```

3. **Skill output files** — Check for recent activity in skill reference directories:
   ```bash
   find ~/.hermes/skills -type f -mmin -60 -name "*.json" -o -name "*.md" | head -10
   ```

4. **File modifications** — General recent activity scan:
   ```bash
   find ~/.hermes -type f -mmin -60 -name "*.md" -o -name "*.json" -o -name "*.yaml" | head -10
   ```

## Fresh Deployment Indicators

- No `~/.hermes/cron/jobs.json` file exists
- Limited session history in `session_search` results
- Recent timestamps on context file but no cron infrastructure
- Skill directories may be present but cron jobs not yet configured

## Action Patterns

When cron infrastructure is missing:
1. **Focus on file system activity** — Use `find` commands to detect recent modifications
2. **Check article generation** — Scheduled content creation is a reliable signal
3. **Verify context file freshness** — Compare current timestamp with context file timestamp
4. **Use multiple search strategies** — Combine date queries, skill-name queries, and file system scans
5. **Preserve existing context** — When no new activity found, maintain current context rather than rewriting stale information

## Silent Mode Triggers for Fresh Deployments

Respond with `[SILENT]` when:
- No cron jobs file exists AND
- No recent file modifications detected AND  
- Context file timestamp is recent (within last 2 hours) AND
- No alternative activity indicators found

This prevents unnecessary context rewrites while the cron infrastructure is being established.