# Cron Job Extraction Patterns

When `read_file` hits dedup limits on `/root/.hermes/cron/jobs.json`, use these patterns to extract specific job information:

## Simple Field Extraction (Terminal)

```bash
# Get specific job details
grep -A 30 "hermes-heartbeat" /root/.hermes/cron/jobs.json | grep -E "(last_run_at|next_run_at|last_status)" | head -3

# Get error status for blocked jobs
grep -A 10 -B 10 "external-feature" /root/.hermes/cron/jobs.json | grep -E "(last_error|last_status)"
```

## Complex Filtering (execute_code)

When you need more sophisticated filtering:

```python
from hermes_tools import read_file
import json

def get_job_status(job_name):
    result = read_file("/root/.hermes/cron/jobs.json")
    if not result.get("content_returned", False):
        # Dedup blocked - use fallback or return cached data
        return None
    
    data = json.loads(result["content"])
    for job in data["jobs"]:
        if job["name"] == job_name:
            return {
                "last_run_at": job.get("last_run_at"),
                "next_run_at": job.get("next_run_at"),
                "last_status": job.get("last_status"),
                "last_error": job.get("last_error")
            }
    return None

# Usage
heartbeat_status = get_job_status("hermes-heartbeat")
external_feature_status = get_job_status("external-feature-daily")
```

## Gap Calculation

For calculating time gaps between runs:

```python
from datetime import datetime

def calculate_gap_minutes(last_run_str, current_time_str):
    last_run = datetime.fromisoformat(last_run_str.replace("Z", "+00:00"))
    current_time = datetime.fromisoformat(current_time_str.replace("Z", "+00:00"))
    return (current_time - last_run).total_seconds() / 60

# Example usage
gap = calculate_gap_minutes("2026-05-20T07:33:15.302030+00:00", "2026-05-20T11:31:52Z")
print(f"Heartbeat gap: {gap:.1f} minutes (~{gap/60:.1f} hours)")
```

## Common Job Names

- `hermes-heartbeat` - 5-minute interval health check
- `external-feature-daily` - Daily external repo enhancement (often blocked)
- `skill-health-daily` - Daily skill health audit
- `github-trending-daily` - Daily GitHub trending repos
- `vibecoding-digest-daily` - Daily r/vibecoding digest
- `vuln-scanner-twice-weekly` - Security vulnerability scanning