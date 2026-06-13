# Heartbeat Session Search Patterns

## Effective Query Strategies

Based on operational experience, these patterns reliably surface recent sessions:

### 1. Date-Based Queries (Most Reliable)
- `"May 20"` - Current month/day format
- `20260520` - YYYYMMDD format  
- `"2026-05-20"` - ISO date format

### 2. Time-Window Probes
- `"14:"` - Hour prefix (e.g., 2 PM sessions)
- `"09:"` - Morning sessions
- Combine with date: `"May 20 14:"`

### 3. Skill-Based Discovery
- `"hermes-heartbeat"` - Find other heartbeat sessions
- `"vuln-scanner"` - Security scanning sessions
- `"external-feature"` - External repo monitoring
- `"github-trending"` - GitHub discovery sessions

### 4. Activity-Based Fallbacks
When session_search returns limited results:
- `find ~/.hermes -type f -mmin -60` - Recent file modifications
- `find ~/.hermes -name "*.md" -mmin -240` - Recent Markdown files (4-hour window)
- `find ~/.hermes -name "*digest*" -mmin -240` - Recent digest files
- Check `~/.hermes/logs/` directory timestamps and recent session folders
- Look for skill-specific output files in `~/.hermes/skills/*/references/`
- Check `~/.hermes/articles/` for recent digests and generated content

## Common Deployment Scenarios

### Fresh Install (No cron/jobs.json)
- `~/.hermes/cron/jobs.json` often missing initially
- Check alternative sources:
  - `~/.hermes/logs/` - Session directories
  - `~/.hermes/articles/` - Generated content
  - Skill-specific output directories

### Limited Session Results
When session_search returns only 3 results despite more activity:
- Try multiple query patterns (4-5 different approaches)
- Combine date + skill queries
- Use file system activity as secondary indicator

### Cold Start Context
When no recent sessions found:
- Preserve existing context file
- Only update if substantive new information exists
- Respond with `[SILENT]` to suppress delivery

## Verification Patterns

After updating context file:
- Verify with `head -3 ~/.hermes/slack-context.md`
- Check timestamp updated
- Retry with content changes if write_file appears to fail silently

## Performance Notes

- Multiple session_search calls normal (3-5 expected)
- Date-based queries most reliable for time windows
- Skill-based queries best for activity-based discovery
- File system checks provide fallback when session search limited