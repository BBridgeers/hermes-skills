# Heartbeat Session Findings - 2026-05-28

## P0 FAILED Jobs (3 total)
1. **skill-health-daily**
   - Error: `RuntimeError: HTTP 404: model "ollama/qwen3-coder-next" not found`
   - Last run: 2026-05-28T06:01:04Z
   - Resolution: Update job configuration to use available model (e.g., deepseek-v4-pro)

2. **slack-context-sync**
   - Error: `RuntimeError: HTTP 404: Ring-2.6-1T is no longer available as a free model. It has transitioned to a paid model. Continue using it here: https://openrouter.ai/inclusionai/ring-2.6-1t`
   - Last run: 2026-05-28T17:58:22Z
   - Resolution: Switch to free alternative model (e.g., deepseek-v4-pro)

3. **Job Pipeline — Follow-Up Decay Monitor**
   - Error: `RuntimeError: HTTP 404: Ring-2.6-1T is no longer available as a free model. It has transitioned to a paid model. Continue using it here: https://openrouter.ai/inclusionai/ring-2.6-1t`
   - Last run: 2026-05-28T17:21:25Z
   - Resolution: Switch to free alternative model (e.g., deepseek-v4-pro)

## P1 WATCH Jobs (0 total)
- No stuck jobs detected (last_status: "running" for >45 min)
- No dead execution loop detected (no jobs with next_run_at >1h ago and last_run_at null/>48h stale)

## Never-Run Jobs (4 total)
Jobs with last_run_at: null and repeat.completed: 0 created >24h ago:
1. cost-report-weekly (created: 2026-05-04T21:51:51Z, next_run: 2026-06-01T09:00:00Z)
2. weekly-review-sunday (created: 2026-05-04T21:52:13Z, next_run: 2026-05-31T10:00:00Z)
3. skill-leaderboard-weekly (created: 2026-05-04T21:52:14Z, next_run: 2026-06-01T08:00:00Z)
4. security-audit-weekly (created: 2026-05-04T21:52:34Z, next_run: 2026-06-01T04:00:00Z)

## System Status
- CPU: 4% (healthy)
- Disk: 71% / 96G (healthy - below 85% alert threshold)
- Memory: 34% used / 7940.9MiB total (healthy)
- Zombie processes: 0
- Services: 
  - hermes-gateway: active
  - hermes-dashboard: active  
  - hermes-workspace: active
- Gateway health check: OK (port 8642 responding)
- Workspace title check: OK (HTML title tag present)
- No SSH brute force attempts in auth.log
- No pending git changes in /root/Resonate_Freq_Proj/ or /root/aeon/
- Configuration: model.default/model.provider correctly set to deepseek-v4-pro/deepseek

## Recommendations
1. Update skill-health-daily, slack-context-sync, and Job Pipeline — Follow-Up Decay Monitor to use deepseek-v4-pro instead of deprecated/unavailable models
2. Investigate why weekly/weekly jobs have not run (may be scheduling issue or dependency not yet met)
3. Continue monitoring - all critical services operational