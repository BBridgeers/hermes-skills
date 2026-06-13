# Heartbeat Check Procedures Reference

This file consolidates all check procedures referenced in the main hermes-heartbeat skill.

## P0 — Failed & Stuck Jobs

1. **List jobs and detect issues**:
   ```bash
   # Use cronjob tool if available, otherwise read authoritative file
   cronjob(action='list')  # canonical
   # fallback:
   read_file(path='/root/.hermes/cron/jobs.json')
   ```
   **Flag**:
   - `last_status: "failed"` or `"error"` → include job name, last run time, error
   - `last_status: "running"` >45 min → stuck (likely hung)
   - `next_run_at` past >1h AND `last_run_at` null or >48h → dead execution loop
   - `enabled_toolsets: null` with advancing `next_run_at` but stagnant `last_run_at` → null toolsets bug

2. **VPS resources**:
   ```bash
   top -bn1 | head -5       # CPU >90%?
   df -h / | tail -1        # disk >85%?
   free -h | head -2        # memory >90%?
   ps aux | awk '$8 ~ /Z/ {print}'  # zombies?
   ```

3. **Service health** (native mode always checks 3 services):
   ```bash
   systemctl --user is-active hermes-gateway
   curl -s --max-time 3 http://localhost:8642/health
   systemctl --user is-active hermes-dashboard
   systemctl --user is-active hermes-workspace
   curl -s --max-time 5 http://localhost:3100/ | grep -a -o '<title>[^<]*</title>'
   ```

4. **File permissions**:
   ```bash
   # Docker mode
   ls -lan /var/lib/docker/volumes/hermes-data/_data/logs/
   docker exec hermes-agent ls -la /opt/data/sessions/sessions.json
   # Native mode
   ls -la /root/.hermes/sessions/sessions.json
   ls -la /root/.hermes/state.db
   ```

5. **API key health**:
   ```bash
   test -s /root/.hermes/env.sh && echo "env.sh OK" || echo "⚠ env.sh MISSING or EMPTY"
   ```

## P1 — Stalled Work & Security

- **SSH brute force**:
  ```bash
  grep "Failed password" /var/log/auth.log | tail -20
  ```
  Flag >5 failures from same external IP in last hour. Internal RFC1918 IPs treated as P2/WATCH.

- **Disk space trending**: Compare current usage to last heartbeat log entry. Flag growth >5%.

- **Pending git changes**:
  ```bash
  cd /root/Resonate_Freq_Proj/ 2>/dev/null && git status --porcelain | head -5 || echo "No Resonate_Freq_Proj directory"
  cd /root/aeon/ 2>/dev/null && git status --porcelain | head -5 || echo "No aeon directory"
  ```

## P2 — Configuration Drift

- **Config parse validity**:
  ```bash
  python3 -c "import yaml; yaml.safe_load(open('/root/.hermes/config.yaml'))"
  ```

- **Model/provider drift**: verify `model.default` and `model.provider` match the expected primary.

- **Skills integrity**: search for SKILL.md count — should be stable.

## P3 — Low-Priority Maintenance

- **Log file sizes**:
  ```bash
  du -sh /var/log/*.log
  ```
  Flag any >100MB.

- **Docker image accumulation**:
  ```bash
  docker images | wc -l
  ```
  Flag if >50 (suggest prune).

- **Pending system updates**:
  ```bash
  apt list --upgradable 2>/dev/null | wc -l
  ```

## Output Format

**All-OK (cron)**: `[SILENT]`

**Findings**:
```
🔴 P0 FAILED: job-name (failed 2h ago), container-name (Exited)
🟡 P1 STALLED: auth.log shows 12 SSH failures from 1.2.3.4
🔵 P2 CONFIG: env.sh missing OPENROUTER_API_KEY
```

**Log format**:
```
HEARTBEAT_{STATUS} {ISO_TIMESTAMP} | CPU:{pct} Disk:{pct} Mem:{pct} | Native:{services_status} | Cron:{count} jobs, {failed} failed, {stuck} stuck, {never_run} never-run | Config:{status} | Model:{model}/{provider} | Status:{OK|WATCH|DEGRADED} | {findings summary}
```

## Known Recurring Patterns (DO NOT ALERT)

- **external-feature-daily**: Job ID `1f1e541dd9ca` frequently triggers `exfil_curl_auth_header` scanner block. Known false positive — treat as P3 INFO after initial reporting.

## Dedup Guidelines

- Check `session_search(query="...")` for same finding in last 48h.
- Check `~/.hermes/heartbeat.log` for identical entries in last 48h.
- Status transitions (OK→WATCH→DEGRADED) indicate escalation — note in log.
- `next_run_at` advancing alone DOES NOT prove execution loop alive — only `last_run_at` proves it.