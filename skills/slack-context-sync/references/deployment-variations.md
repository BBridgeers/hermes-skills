# Deployment Variations for Slack Context Sync

## Cron Infrastructure Variations

Different Hermes deployments may have varying cron infrastructure setups:

### Type 1: Full Cron Infrastructure
- `~/.hermes/cron/jobs.json` exists with structured job data
- `~/.hermes/cron/` directory contains operational files
- Standard session search patterns work reliably

### Type 2: Minimal Cron Infrastructure (common)
- `~/.hermes/cron/jobs.json` does NOT exist
- `~/.hermes/cron/` directory may be missing entirely
- Session search relies on alternative indicators

### Type 3: Hybrid Deployment
- Cron jobs run but infrastructure files are elsewhere
- Check alternative locations: `~/.hermes/home/.hermes/cron/`, custom paths
- Session logs may be in non-standard locations

## Alternative Activity Indicators

When `~/.hermes/cron/jobs.json` is missing, use these alternative signals:

### File Modification Timestamps
```bash
find ~/.hermes -type f -mmin -60 -name "*.md" -o -name "*.json" -o -name "*.log"
ls -la ~/.hermes/logs/ | grep "today's date"
```

### Session Directory Activity
```bash
ls -la ~/.hermes/logs/ | head -10  # Check most recent session directories
find ~/.hermes/logs/ -type d -mmin -120  # Recent session directories
```

### Article Generation Signals
```bash
find ~/.hermes/articles/ -name "*.md" -mmin -240  # Recent article digests
```

### Skill Output Files
```bash
find ~/.hermes/skills/ -name "*.json" -mmin -120  # Recent skill output
```

## Session Search Fallback Patterns

When standard session search returns limited results:

### Date/Time Pattern Queries
```
session_search(query="May 20")  # Current date
session_search(query="20260520")  # YYYYMMDD format
session_search(query="14:")  # Hour pattern
session_search(query="15:")  # Next hour pattern
```

### Skill-Based Queries
```
session_search(query="hermes-heartbeat")  # Heartbeat sessions
session_search(query="slack-context-sync")  # Context sync sessions
session_search(query="external-feature OR vuln-scanner")  # Other active skills
```

### Source-Based Queries
```
session_search(query="cron")  # Cron sessions
session_search(query="terminal")  # CLI sessions
session_search(query="slack")  # Slack sessions
```

## Handling Empty Results

When session search returns empty or limited results:
1. **Preserve existing context** - Don't overwrite with stale information
2. **Check file freshness** - Verify context file timestamp vs current time
3. **Use [SILENT] response** - For cron heartbeat sessions with no new info
4. **Fallback to file activity** - Use file modification patterns as proxy for activity

## Deployment-Specific Notes

- **Fresh installs**: May lack cron infrastructure initially
- **Docker deployments**: Paths may differ (`/app/.hermes/` vs `~/.hermes/`)
- **Multi-user setups**: Check for user-specific hermes directories
- **Migration states**: Post-migration may have mixed path structures