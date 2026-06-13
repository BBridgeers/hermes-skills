# OpenRouter Cost Forensics

Last updated: 2026-06-05

When OpenRouter credits vanish unexpectedly, pull the activity CSV and run this analysis before assuming a key leak.

## Pulling Activity Data

1. Go to https://openrouter.ai/settings/activity
2. Click Export → CSV
3. Save to Google Drive (rclone-accessible) or upload to VPS

## Forensic Analysis Script

```python
import csv
from collections import defaultdict
from datetime import datetime

rows = []
with open("/tmp/openrouter_activity.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Total
total_cost = sum(float(r["cost_total"]) for r in rows if r["cost_total"])
total_calls = len(rows)

# By model
model_costs = defaultdict(lambda: {"cost": 0.0, "calls": 0, "prompt_tokens": 0})
for r in rows:
    m = r["model_permaslug"]
    model_costs[m]["cost"] += float(r["cost_total"]) if r["cost_total"] else 0
    model_costs[m]["calls"] += 1
    model_costs[m]["prompt_tokens"] += int(r["tokens_prompt"]) if r["tokens_prompt"] else 0

# Hourly buckets
hourly = defaultdict(lambda: {"cost": 0.0, "calls": 0})
for r in rows:
    if r["created_at"]:
        dt = datetime.strptime(r["created_at"][:13], "%Y-%m-%d %H")
        hourly[dt]["cost"] += float(r["cost_total"]) if r["cost_total"] else 0
        hourly[dt]["calls"] += 1

# Top calls
top = sorted(rows, key=lambda r: float(r["cost_total"]) if r["cost_total"] else 0, reverse=True)[:10]

# App breakdown
app_data = defaultdict(lambda: {"cost": 0.0, "calls": 0})
for r in rows:
    app_data[r.get("app_name", "unknown")]["cost"] += float(r["cost_total"]) if r["cost_total"] else 0
    app_data[r.get("app_name", "unknown")]["calls"] += 1

print(f"TOTAL: ${total_cost:.4f} across {total_calls} calls")
print(f"Models: {dict(model_costs)}")
print(f"Apps: {dict(app_data)}")
```

## Red Flags for "It's a Leak"

- Multiple `app_name` values (not just "Hermes Agent")
- Calls from unknown IPs (check if available)
- Calls at hours you know you weren't active
- Multiple different model families being called

## Red Flags for "It's Your Own Usage"

- Every call from "Hermes Agent" (single app)
- Single model used for all calls (e.g., qwen/qwen3.7-max-20260520)
- Calls concentrated in 1-2 hour windows (your active session)
- High prompt tokens per call (60K-87K) = long-context agent sessions
- All calls show `tool_calls` finish reason

## Real Example (2026-06-05)

- Total: $2.88 across 107 calls in 65 minutes
- Every call: qwen/qwen3.7-max-20260520
- Every call: "Hermes Agent" app
- Average prompt: 36K tokens, largest: 87K tokens
- Cache hit rate: 61.4%
- Window: 17:00-18:05 UTC

**Verdict**: Own usage. A single Hermes session with qwen3.7-max burned through $2.88 in an hour. At sustained usage, $10 vanishes in ~3-4 hours. NOT a key leak — just an expensive model at high context with tool calling.

## Prevention

1. Never use qwen3.7-max via OpenRouter as primary — it's ~$1.25/M input at scale
2. Set OpenRouter spending limits: https://openrouter.ai/settings/limits
3. Use DeepSeek native API instead (50-100x cheaper for same-tier models)
4. Use Google Gemini free tier (1500 req/day) for cron jobs
5. Monitor with `cost-report` cron job (weekly)
