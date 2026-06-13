# Effective Session Search Queries for Slack Context Sync

## Date/Time Patterns
- `"May 20"` — Current date in month-day format
- `20260520` — Current date in YYYYMMDD format  
- `"14:"` — Hour-specific search (e.g., 14:00-14:59)
- `"2026-05-20"` — Full ISO date format

## Skill-Based Queries
- `"vuln-scanner"` — Security scanning sessions
- `"external-feature"` — Repository enhancement sessions
- `"skill-health"` — Skill monitoring sessions
- `"github-trending"` — Trending repo sessions
- `"hermes-heartbeat"` — System health sessions

## Source-Based Queries
- `"cron"` — All cron job sessions
- `"cli"` — All terminal sessions
- `"slack"` — All Slack sessions (when available)

## Activity-Based Queries
- `"terminal OR Slack"` — Cross-channel activity
- `"sync context"` — Manual sync requests
- `"heartbeat"` — System monitoring

## Fallback Strategies
When session_search returns limited results:
1. Check file modification times: `find ~/.hermes -type f -mmin -60`
2. Scan log directories: `ls -la ~/.hermes/logs/`
3. Look for skill output files in references directories
4. Check if cron/jobs.json exists — if missing, recent cron activity may be in logs

## Best Practices
- Always try multiple query patterns (3-5 different approaches)
- Combine date-based and skill-based queries for best coverage
- Use terminal fallbacks when session_search dedup limits are hit
- When no new information is found, preserve existing context rather than rewriting stale data