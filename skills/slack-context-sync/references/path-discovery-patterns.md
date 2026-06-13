# Path Discovery Patterns for Hermes Deployment Variations

When session search returns limited results and cron infrastructure files are missing from expected locations, use these systematic path discovery patterns:

## Cron Job File Location Patterns
```bash
# Find cron jobs.json across all possible Hermes locations
find / -name "jobs.json" -path "*hermes*" 2>/dev/null

# Check common deployment variations
ls -la /root/.hermes/cron/jobs.json
ls -la /root/hermes-backup/cron/jobs.json  
ls -la /root/.hermes.pre-decontainerize/cron/jobs.json
ls -la /root/.hermes/state-snapshots/*/cron/jobs.json
```

## Alternative Activity Indicators
When cron infrastructure is missing, check these alternative sources for recent activity:
- Recent log directories: `ls -la ~/.hermes/logs/`
- File modification timestamps: `find ~/.hermes -type f -mmin -240`
- Article digests: `find ~/.hermes -name "*digest*" -type f -mmin -240`
- Skill output files: `find ~/.hermes/skills/*/references/ -type f -mmin -240`

## Path Resolution Notes
- `~/.hermes` may resolve to `/root/.hermes/home/.hermes` in some deployments
- Backup locations often contain state snapshots with recent cron data
- Fresh deployments may lack cron infrastructure initially — check alternative indicators

## Session Search Fallback Patterns
When session_search returns limited results:
1. Try multiple date formats: "May 20", "20260520", "15:", "2026-05-20"
2. Search by skill names: "hermes-heartbeat OR slack-context-sync"
3. Check for recent file modifications as activity indicators
4. Look for article generation and other scheduled content production