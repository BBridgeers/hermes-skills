# Heartbeat Session Search Patterns

## Reliable Query Strategies

When `session_search` returns limited results, use these proven patterns:

### Date/Time Formats
- `"May 20"` — Month + day (most reliable)
- `20260520` — YYYYMMDD format
- `"15:"` or `"16:"` — Hour-based searches
- `"2026-05-20"` — ISO date format

### Skill-Based Queries
- `"hermes-heartbeat OR slack-context-sync"` — Core cron jobs
- `"external-feature OR vuln-scanner"` — Feature-specific jobs
- `"github-trending OR vibecoding-digest"` — Content generation

### Activity Indicators
- Recent article digests: `find ~/.hermes -name "*digest*" -mmin -120`
- File modifications: `find ~/.hermes -type f -mmin -60 -name "*.md" -o -name "*.json"`
- Log directories: `find ~/.hermes/logs -type d -mmin -120`

### Session Search Reliability Patterns

1. **Multiple query attempts are essential** — Plan for 3-5 different query patterns
2. **Combine date formats with skill names** — `"May 20 external-feature"`
3. **Check alternative activity indicators** when session search fails
4. **Preserve existing context** when no new information is found

### When to Use [SILENT]
Return exactly "[SILENT]" when:
- Only routine cron sessions found (heartbeat, context-sync)
- No file modifications in last 60 minutes
- Context file timestamp is recent (<30 minutes)
- No new pending actions or decisions
- System status remains stable
- sync-context.sh returns empty output (exit code 0)

This prevents unnecessary notifications while maintaining heartbeat cadence.