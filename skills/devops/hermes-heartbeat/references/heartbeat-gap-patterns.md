# Hermes Heartbeat Gap Resolution Patterns

## Gap Detection

Heartbeat gaps occur when the hermes-heartbeat cron job fails to run at its scheduled interval (every 5 minutes). These can be detected by:

1. **Context file mentions**: "hermes-heartbeat gap: last ran X, now ~Y gap"
2. **Jobs.json status**: Compare `last_run_at` vs current time
3. **Session search**: Look for missing heartbeat sessions

## Common Gap Causes

### Resolved Gaps (Self-Healing)
- **Scheduler rescheduling**: The scheduler may detect missed runs and automatically reschedule
- **Temporary resource constraints**: CPU/memory spikes that resolve
- **Network blips**: Temporary connectivity issues

### Persistent Gaps (Require Intervention)  
- **Scheduler execution loop dead**: Jobs show `next_run_at` in past but `last_run_at` never updates
- **Configuration issues**: `enabled_toolsets=null` preventing job execution
- **Resource exhaustion**: Persistent high CPU/memory preventing job dispatch

## Gap Resolution Verification

When a gap is mentioned in context but appears resolved:

1. **Check jobs.json**: Verify `last_run_at` is recent and `next_run_at` is properly scheduled
2. **Verify execution**: Confirm heartbeat sessions are appearing in recent session search
3. **Monitor trend**: Watch for recurring patterns vs one-time events

### Example Recovery Pattern
```json
{
  "last_run_at": "2026-05-20T11:43:46.444131+00:00",
  "next_run_at": "2026-05-20T11:48:46.444131+00:00", 
  "last_status": "ok",
  "last_error": null
}
```

This shows a healthy 5-minute interval with successful execution.

## Monitoring Commands

```bash
# Check current heartbeat status
grep -A 10 '"name": "hermes-heartbeat"' /root/.hermes/cron/jobs.json | grep -E "(last_run_at|next_run_at|last_status)"

# Check for recent heartbeat sessions  
session_search(query="hermes-heartbeat")

# Verify scheduler is alive
ps aux | grep -i scheduler
```

## Alert Thresholds

- **P0**: Gap > 30 minutes (scheduler likely dead)
- **P1**: Gap > 15 minutes (investigate cause)  
- **P2**: Gap > 5 minutes (monitor, may self-resolve)

Gaps under 5 minutes are normal scheduler jitter and should not be alerted.