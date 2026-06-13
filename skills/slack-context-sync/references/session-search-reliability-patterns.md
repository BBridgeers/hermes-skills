# Session Search Reliability Patterns

## Core Challenge

`session_search` can be unreliable for heartbeat operations due to:
- Limited result sets (often only 3 sessions returned)
- Inconsistent date/time format matching
- Variable session metadata completeness

## Effective Query Strategies

### 1. Date-Based Queries (Most Reliable)
```
"May 20"           # Month + day
"20260520"         # YYYYMMDD format  
"2026-05-20"       # ISO date format
"05/20"            # Month/day format
```

### 2. Time Window Queries
```
"14:"              # Sessions around 2 PM
"15:"              # Sessions around 3 PM
"2:27"             # Specific time
```

### 3. Skill Name Queries
```
"hermes-heartbeat"
"slack-context-sync" 
"external-feature"
"vuln-scanner"
```

### 4. Source/Model Queries
```
"cron"             # Cron sessions
"cli"              # CLI sessions
"deepseek"         # Model used
```

### 5. Keyword Probes
```
"P0"               # Critical issues
"P1"               # High priority issues
"exfil_curl_auth_header" # Specific security flags
```

## Path Discovery Patterns

When terminal access is limited or `session_search` returns sparse results:

### Check Alternative Data Sources:
```bash
# Cron job files
find ~/.hermes -name "jobs.json" -path "*cron*"

# State snapshots (backups)
find ~/.hermes -name "*state-snapshot*" -type d

# Recent log directories  
find ~/.hermes/logs -type d -mmin -240

# Article generation
find ~/.hermes/articles -name "*.md" -mmin -240
```

### Common Backup Locations:
- `~/.hermes/state-snapshots/` - Automatic state backups
- `~/.hermes.pre-decontainerize/` - Migration backups
- `~/hermes-backup/` - Manual backups

## Handling Deduplication

When `read_file` hits deduplication limits:

1. **Check `content_returned` flag** before accessing `content`
2. **Use content from earlier reads** - you already have the data
3. **Fallback to terminal** for JSON field extraction:
```bash
grep -A 20 "hermes-heartbeat" /root/.hermes/cron/jobs.json | grep -E "(last_run_at|next_run_at|last_status)"
```

## Multi-Query Approach

Plan for 5-7 different query attempts:
1. Broad `session_search()` (no query)
2. Current date in multiple formats
3. Recent time windows
4. Skill names
5. Source types
6. Priority keywords
7. Error patterns

Each query may return different sessions - combine results mentally.