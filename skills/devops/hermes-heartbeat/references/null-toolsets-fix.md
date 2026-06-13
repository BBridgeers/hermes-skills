# NULL_TOOLSETS Repair Protocol

## Problem

Jobs with `enabled_toolsets: null` in `~/.hermes/cron/jobs.json` are silently skipped by the scheduler. The scheduler advances `next_run_at` normally but never dispatches the job — `last_run_at` stagnates while `next_run_at` keeps moving. This is a known scheduler bug where jobs created via certain code paths lack the required toolsets array.

## Detection

From a heartbeat run, flag any job where:
- `enabled_toolsets` is `null` (not just missing — explicitly null in JSON)
- `next_run_at` advances normally
- `last_run_at` is stale (never updated)

## Fix

Read, patch, and rewrite `~/.hermes/cron/jobs.json`:

```python
import json

with open('/root/.hermes/cron/jobs.json') as f:
    data = json.load(f)

# Map job names to appropriate toolsets based on job function
toolsets = {
    'slack-context-sync': ['terminal', 'file', 'search'],
    'context-loss-recovery': ['terminal', 'file', 'search'],
    'Housing Sprint — Morning Search': ['web', 'search', 'file'],
    'Job Search — Daily Discovery': ['web', 'search', 'file'],
    'Inbox Triage — Twice Daily': ['terminal', 'file'],
    'Job Pipeline — Follow-Up Decay Monitor': ['web', 'search', 'file'],
}

for j in data['jobs']:
    name = j.get('name', '')
    if name in toolsets and j.get('enabled_toolsets') is None:
        j['enabled_toolsets'] = toolsets[name]
        print(f'FIXED: {name} -> {toolsets[name]}')

with open('/root/.hermes/cron/jobs.json', 'w') as f:
    json.dump(data, f, indent=2)
```

## Toolset selection guidelines

| Job function | Recommended toolsets |
|---|---|
| Context sync (Slack/Telegram ↔ terminal) | `["terminal", "file", "search"]` |
| Web research (housing, jobs, discovery) | `["web", "search", "file"]` |
| Inbox/message triage | `["terminal", "file"]` |
| Monitoring/health checks | `["terminal", "search", "file", "skills"]` |
| Git/code automation | `["terminal", "file"]` |

Jobs without `enabled_toolsets` default to loading ALL tools, which wastes tokens. But `null` (the bug case) means zero tools loaded — the job can't do anything.

## Prevention

When creating new cron jobs, always set `enabled_toolsets` explicitly. The `cronjob` tool's `enabled_toolsets` parameter accepts an array — use it.
