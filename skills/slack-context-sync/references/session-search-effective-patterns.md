# Effective Session Search Patterns for Context Sync

## Proven Query Patterns

### Date-Based Queries (Most Reliable)
- `"May 20"` - Natural language date format
- `20260520` - Compact YYYYMMDD format
- `"2026-05-20"` - ISO date format
- `"16:"` - Hour-based time window

### Skill-Based Queries
- `"hermes-heartbeat OR slack-context-sync"` - Combined maintenance skills
- `"external-feature"` - Specific feature development
- `"vuln-scanner"` - Security scanning sessions

### Activity Indicator Patterns
- Check file modifications: `find ~/.hermes -type f -mmin -60 -name "*.md" -o -name "*.json" -o -name "*.yaml"`
- Check article generation: `find ~/.hermes/articles -name "*.md" -mmin -120`
- Verify context file freshness: `stat -c "%y" ~/.hermes/slack-context.md`

### Path Discovery Patterns
- Cron job discovery: `find / -name "jobs.json" -path "*hermes*"`
- Common backup locations:
  - `/root/hermes-backup/cron/`
  - `/root/.hermes.pre-decontainerize/cron/`
  - `/root/.hermes/state-snapshots/`

## When to Use [SILENT]

The sync script (`sync-context.sh`) returns empty output with exit code 0 when:
- No new activity detected
- Context file is already fresh (within last 30 minutes)
- Only routine maintenance sessions found
- No file modifications in the last 60 minutes
- System status remains stable

This is NORMAL behavior - not an error condition.

## File Timestamp Interpretation

- **Fresh**: < 30 minutes old - preserve existing context
- **Stale**: 30-60 minutes old - consider updating
- **Very stale**: > 60 minutes old - definitely update

Use: `stat -c "%y" ~/.hermes/slack-context.md` to get exact modification time