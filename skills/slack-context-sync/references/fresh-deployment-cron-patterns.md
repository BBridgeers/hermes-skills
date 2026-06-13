# Fresh Deployment Cron Patterns

When `~/.hermes/cron/jobs.json` doesn't exist (common in fresh deployments), use these alternative indicators:

## Primary Activity Indicators

1. **Article digests** — Check `~/.hermes/articles/` for recent content:
   ```bash
   ls -la ~/.hermes/articles/  # Look for vibecoding-digest-*.md, blogwatcher-*.md
   stat -c "%y" ~/.hermes/articles/vibecoding-digest-*.md
   ```

2. **Recent file modifications** — Look for any recent activity:
   ```bash
   find ~/.hermes -type f -mmin -120 | head -10
   ```

3. **Session logs** — Check for recent session directories:
   ```bash
   ls -la ~/.hermes/logs/ | grep "2026" | tail -5
   ```

4. **Skill output files** — Look for skill-specific outputs:
   ```bash
   find ~/.hermes/skills -name "*.json" -o -name "*.md" -mmin -240 | head -5
   ```

## Path Resolution Issues

In some deployments, `~/.hermes` may resolve to `/root/.hermes/home/.hermes`. Always use absolute paths:

```bash
# Instead of:
read_file("~/.hermes/cron/jobs.json")

# Use:
read_file("/root/.hermes/cron/jobs.json")
```

## Fresh Deployment Signals

When these files exist, the system has activity even without cron infrastructure:
- `~/.hermes/articles/vibecoding-digest-*.md` — Scheduled content generation
- `~/.hermes/skills/*/references/*.json` — Skill output files
- `~/.hermes/logs/2026*/` — Session directories
- `~/.hermes/memory/` — Memory files with recent timestamps

## Verification Commands

```bash
# Check if cron directory exists at all
ls -la /root/.hermes/ | grep cron

# Check alternative cron locations (backups, migrations)
find /root -name "jobs.json" -path "*hermes*" 2>/dev/null

# Check recent activity through multiple indicators
find /root/.hermes -type f -mmin -360 | grep -E "\.(md|json|log)$" | head -10
```

## When to Consider Fresh Deployment

- `jobs.json` doesn't exist at `/root/.hermes/cron/jobs.json`
- No cron session logs in `~/.hermes/logs/`
- But article digests or skill outputs show recent activity
- System is otherwise functional (skills work, models respond)

In fresh deployments, focus on the activity that DOES exist rather than treating missing cron as an error.