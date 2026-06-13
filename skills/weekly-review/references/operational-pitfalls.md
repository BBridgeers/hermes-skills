# Operational Pitfalls for Weekly Review

## Log rotation truncates `--since 7d`

**Problem**: `hermes logs agent --since 7d` only scans the current `agent.log` file, not rotated logs (`.1`, `.2`, etc.). On a high-frequency cron setup with 500+ sessions/day, the current log may only cover a few hours.

**Detection**: If the output is <200 lines for a system with heartbeat + context-sync every 5 min, rotation has occurred.

**Workaround**:
```bash
# Check rotated log files
ls -la ~/.hermes/logs/agent.log*

# Grep across all rotation files for a specific date range
for f in ~/.hermes/logs/agent.log*; do
  echo "=== $f ==="
  grep "2026-06-0[1-7]" "$f" | head -20
done
```

**Impact on review**: Mark affected metrics as `_degraded source_`. Use `hermes sessions list` and `hermes sessions stats` as fallbacks.

## Bare-metal Hermes + Docker services = DNS failures

**Problem**: When Hermes runs bare-metal (decontainerized) and services like Honcho run in Docker, Docker container hostnames (`honcho-api`, `honcho-database`) are NOT resolvable from the host. All connections fail with `Temporary failure in name resolution`.

**Detection**: `hermes logs errors --since 7d --level ERROR | grep "name resolution"`

**Fix**: Switch connection configs from Docker hostnames to `localhost:<mapped_port>`. Check `docker ps` for port mappings.

**Impact on review**: If Honcho errors dominate the error log, flag as a top-priority Add finding. Session memory sync is silently broken.
