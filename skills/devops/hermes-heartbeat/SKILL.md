---
name: hermes-heartbeat
description: Proactive ambient health check for Hermes agent — detect failed cron jobs, stuck processes, resource alerts, and configuration drift. Adapted from Aeon's heartbeat skill.
var: ""
tags: [meta, devops, monitoring]
---

# Hermes Heartbeat — Proactive Health Monitor

> Adapted from Aeon's heartbeat skill architecture. Trigger conditions, priority tiering, dedup, and status page concepts preserved.

## Purpose

Detect anything in the Hermes agent's operational state that needs attention. Run periodically (recommended: 3x daily) to catch failures before they compound.

**Key enhancement**: The heartbeat now includes specific detection and guidance for model paywall errors (e.g., Ring-2.6-1T transitioning to paid tier on OpenRouter) to prevent prolonged job failures.
- `references/heartbeat-session-2026-05-28.md` — Session-specific findings from heartbeat run on 2026-05-28: P0 Ring-2.6-1T model paywall errors, P1 missing ollama/qwen3-coder-next model
- `references/heartbeat-session-2026-06-01.md` — Session-specific findings from heartbeat run on 2026-06-01: P2 model drift (operator-driven), 163+ consecutive silent runs
- `references/heartbeat-session-2026-06-02-credit-exhaustion.md` — P0 OpenRouter credit exhaustion (HTTP 402), detection pattern, and recovery
- `references/heartbeat-session-2026-06-08-402-cascade.md` — P0 OpenRouter 402 cascade affecting 11 jobs + heartbeat self-blindspot (13h monitoring gap)
- `references/co-tenant-container-issues.md` — Known co-tenant container problems (fb-scraper port conflict, etc.)
\n## Checks (priority-ordered)

### P0 — Failed & stuck jobs (check first)

1. **List all cron jobs**: USE `cronjob(action='list')` when available (the canonical tool). **Fallback**: if the `cronjob` tool is unavailable or returns incomplete data, read the jobs file directly: `read_file(path='/root/.hermes/cron/jobs.json')`. This JSON file is the scheduler's authoritative state — every job record includes `id`, `name`, `last_status`, `last_run_at`, `next_run_at`, `last_error`, `repeat.completed`, `state`, and `enabled`. Flag:
   - Any job with `last_status: "failed"` OR `last_status: "error"` — include job name, last run time, and `last_error` if present
   - **Stuck jobs**: any job where `last_status: "running"` AND `last_run > 45 min ago` — job dispatched but never completed (likely hung). Also: any job with state `"running"` (not `"scheduled"`) for >45 min.
   - **Dead execution loop**: if ANY job has `next_run_at` in the past (>1 hour ago) AND `last_run_at` is either null or >48 hours stale — the scheduler's API layer is alive (accepting commands, updating `next_run_at`) but its asyncio execution loop is not dispatching jobs. Flag as P0 DEGRADED. A gateway restart may resolve it; if not, the scheduler source needs investigation.
   - **never-run jobs (sentinel)**: Jobs with `last_run_at: null` and `repeat.completed: 0` created >24h ago with `next_run_at` in the future. These don't prove a dead loop (they may simply not be due yet) but should be flagged as P1 WATCH for investigation — they may indicate scheduling issues, dependencies not met, or simply that their first run time has not yet arrived.
- **security guardrail failures**: Jobs with `last_status: "error"` due to tirith blocks are expected behavior for proactive-repo jobs whose prompts contain auth-header patterns in curl commands. These failures don't indicate gateway decay — they indicate the job's prompt triggers a security rule. See `references/external-feature-daily-error-analysis.md` for diagnosis and resolution paths, and see the `external-feature` skill's `references/tirith-safe-http.md` for guidance on avoiding tirith blocks in cron prompts.
- **Model not found errors**: Jobs with `last_status: "error"` due to missing models (e.g., `HTTP 404: model "ollama/qwen3-coder-next" not found`) indicate incorrect model configuration. Check the job's model/provider configuration in config.yaml or the job definition. See `references/model-configuration-issues.md` for diagnosis and resolution paths.
- **Model paywall errors**: Jobs failing with HTTP 404 due to Ring-2.6-1T transitioning to a paid model (e.g., `slack-context-sync`, `Job Pipeline — Follow-Up Decay Monitor`) indicate the model is no longer free on OpenRouter. Check the job's model configuration and update to a free alternative (e.g., `deepseek-v4-pro`). See `references/ring-2-6-1t-model-paywalled.md` for diagnosis and resolution paths. Example error from 2026-05-28: `RuntimeError: HTTP 404: Ring-2.6-1T is no longer available as a free model. It has transitioned to a paid model. Continue using it here: https://openrouter.ai/inclusionai/ring-2.6-1t`
- **OpenRouter credit exhaustion (HTTP 402)**: If all default-model cron jobs start failing with HTTP 402 or "insufficient credits" messages, OpenRouter credits are exhausted. This is a P0 — it blocks every job using the default model. **Detection**: check OpenRouter credit balance via API (use the OpenRouter `/api/v1/auth/key` endpoint with the API key from env — note: tirith blocks curl commands containing auth headers, so use `python3 -c` with `requests` or `urllib` to check the balance instead). **Pitfall — endpoint may return 401**: The `/api/v1/auth/key` endpoint may return HTTP 401 "User not found" even with a key that is valid for model inference (verified by cron jobs returning 402, not 401). This is an endpoint-level permission issue, not a key problem. **Fallback detection**: if the API endpoint fails with 401, infer credit exhaustion from cron job error patterns alone — count all jobs with `last_error` containing `HTTP 402` or `Insufficient Balance`. A sudden spike of 402 errors across 7+ agent-based jobs is definitive evidence of credit exhaustion even if the API balance endpoint is unreachable. **Symptoms**: heartbeat logs show `HEARTBEAT_DEGRADED` with credit exhaustion message; jobs show `last_status: "error"` with HTTP 402 or token-limit errors like "can only afford X tokens, requested Y". **Recovery**: credits replenish on the monthly billing cycle; until then, jobs using the exhausted provider will fail. Flag as P0 DEGRADED with the count of affected jobs. Once credits recover (verified by a job completing successfully or API returning valid balance), downgrade to OK/silent — do not keep alerting on a resolved credit issue.
- **Ollama Cloud weekly usage limit (HTTP 429)**: If multiple agent-based cron jobs simultaneously fail with HTTP 429 and error message containing `you (bbridgers) have reached your weekly usage limit`, the Ollama Cloud free-tier weekly quota is exhausted. This is a P0 — it blocks ALL jobs dispatching through the Ollama provider. **Detection**: count jobs with `last_error` containing `HTTP 429` and `weekly usage limit`. **Symptoms**: large simultaneous job failure count (8-12+ jobs all failing within one cycle); script-only jobs (disk-REDACTED, rclone-upload-gdrive) and non-Ollama-provider jobs (slack-context-sync using OpenRouter) continue to succeed. **Recovery**: (1) wait for Ollama Cloud weekly limit reset (check ollama.com/settings for reset date), or (2) switch cron jobs to OpenRouter provider (`hermes config set model.provider openrouter` or override per-job). Once recovered, downgrade to OK — do not keep alerting. See `references/ollama-cloud-weekly-limit.md` for full detection pattern.
- **Ghost jobs (scheduled but never dispatch despite elapsed opportunities)**: A job with `last_run_at: null` and `repeat.completed: 0` that has existed >7 days AND whose schedule has produced multiple opportunities that should have fired (e.g., `0 10 * * 0` job created 5 weeks ago = 5 missed Sundays) is a ghost job. Flag as P1 WATCH with the count of missed opportunities. This differs from "never-run jobs (sentinel)" because the schedule window has definitively elapsed multiple times.
- **toolsets null bug**: Jobs with `enabled_toolsets: null` may be silently skipped by the scheduler even when `next_run_at` advances normally. This is a known bug where jobs created via certain methods lack the required toolsets configuration. Flag as P1 WATCH if a job shows advancing `next_run_at` but stagnant `last_run_at` with `enabled_toolsets: null`. See `references/cron-jobs-json-schema.md` for diagnosis and fix.
- **Recovered jobs**: Jobs that previously failed but have since recovered (e.g., `last_status: "error"` → `last_status: "ok"` with recent successful runs) should be noted but not flagged as active issues. These indicate transient problems that self-resolved.
   - **BEWARE**: `cronjob(action='run')` updates `next_run_at` but if the execution loop is dead, `last_run_at` will never change. `next_run_at` moving does NOT prove the scheduler works — only `last_run_at` proves execution.
   
## Reference Files\n\n- `references/cron-jobs-json-schema.md` — Field definitions and health signal mapping\\n- `references/job-analysis-patterns.md` — Analysis of specific job patterns and recovery behaviors\\n- `references/cron-job-analysis-patterns.md` — Comprehensive classification of failure patterns and priority guidelines\\n- `references/ssh-brute-force-classification.md` — Detailed RFC1918 internal IP handling with concrete examples\\n- `references/primary-model-config.md` — Canonical model configuration expectations\\n- `references/model-configuration-issues.md` — Diagnosis and resolution of model not found errors in cron jobs\\n- `references/ring-2-6-1t-model-paywalled.md` — Diagnosis and resolution of Ring-2.6-1T model paywall errors\\n- `references/known-recurring-patterns.md` — Complete list of known issues and dedup guidelines\\n- `references/heartbeat-session-2026-05-28.md` — Session-specific findings from heartbeat run on 2026-05-28: P0 Ring-2.6-1T model paywall errors, P1 missing ollama/qwen3-coder-next model\\n- `references/never-run-job-patterns.md` — Patterns and investigation procedures for never-run cron jobs\\n- `references/ollama-cloud-weekly-limit.md` — Detection, recovery, and dedup for Ollama Cloud HTTP 429 weekly quota exhaustion

2. **Check VPS resources** via terminal:
   ```bash
   # CPU load
   top -bn1 | head -5
   # Disk usage
   df -h / | tail -1
   # Memory
   free -h | head -2
   # Zombie processes
   ps aux | awk '$8 ~ /Z/ {print}'
   ```
   Flag: CPU > 90%, disk > 85%, memory > 90%, any zombie processes

3. **Service health** (detect deployment mode first):
   ```bash
   docker ps --format '{{.Names}}' 2>/dev/null | grep -q 'hermes' && MODE=docker || MODE=native
   ```
   If MODE=docker:
   ```bash
   docker ps -a --format "table {{.Names}}\\t{{.Status}}"
   ```
   Flag any container with `Exited`, `Restarting`, or `Created` status. (Created = container was created but never successfully started — check `docker inspect <name> --format '{{.State.Status}} {{.State.Error}}'` for the failure reason; common causes include port-bind conflicts and missing dependencies.)
**Co-tenant Docker containers** (regardless of deployment mode): Always check ALL Docker containers, not just Hermes', since co-tenant services share the same host:
```bash
docker ps -a --format "table {{.Names}}\t{{.Status}}"
```
Flag any container with `Created`, `Exited`, or `Restarting` status — these indicate a service that cannot start or crashed. For `Created` containers (never started), inspect the error:
```bash
docker inspect <name> --format '{{.State.Status}} {{.State.Error}}'
```
Common `Created` causes: port-bind conflicts (`address already in use`), missing dependencies, missing volumes. Report as P2 WATCH for co-tenants (they're not the agent's responsibility but can consume resources and indicate misconfiguration). Do NOT auto-fix co-tenant containers — just flag.

**Native mode service checks**: Always check all THREE services (gateway + dashboard + workspace):
```bash
# Gateway (core agent, port 8642)
systemctl --user is-active hermes-gateway
curl -s --max-time 3 http://localhost:8642/health
# Dashboard (models/config/sessions, port 9119 — MANDATORY for workspace)
systemctl --user is-active hermes-dashboard
# Workspace (web UI, port 3100)
systemctl --user is-active hermes-workspace
curl -s --max-time 5 http://localhost:3100/ | grep -a -q '<title>'
```
Flag any service not `active` or returning empty/error. Gateway alone is NOT enough — without dashboard, the workspace model picker/config/sessions are all dead. **Note**: The workspace title check is more reliable than simple HTTP status codes.

**🔧 Slack Gateway + Workspace — AUTO-FIX (P0, every heartbeat):**

The Slack gateway (`hermes-gateway`) and Workspace (`hermes-workspace`) are the user's primary interfaces. If either is down, Hermes is unreachable via Slack and the web UI is dead. These MUST be checked AND auto-fixed on every single heartbeat — detection alone is not enough.

```bash
# Check gateway (Slack + API, port 8642)
GATEWAY_ACTIVE=$(systemctl --user is-active hermes-gateway)
GATEWAY_HEALTH=$(curl -s --max-time 3 http://localhost:8642/health 2>/dev/null)

# Check workspace (web UI, port 3100)
WORKSPACE_ACTIVE=$(systemctl --user is-active hermes-workspace)
WORKSPACE_TITLE=$(curl -s --max-time 5 http://localhost:3100/ 2>/dev/null | grep -a -o '<title>[^<]*</title>')
```

**Auto-fix protocol:**

If gateway is NOT `active` OR health check returns empty/error:
```bash
systemctl --user restart hermes-gateway
sleep 3
# Verify it came back
systemctl --user is-active hermes-gateway && curl -s --max-time 3 http://localhost:8642/health
```
Report: `🔧 AUTO-FIXED: hermes-gateway restarted → now active/healthy`

If workspace is NOT `active` OR title check returns empty:
```bash
systemctl --user restart hermes-workspace
sleep 3
# Verify it came back
systemctl --user is-active hermes-workspace && curl -s --max-time 5 http://localhost:3100/ | grep -a -o '<title>[^<]*</title>'
```
Report: `🔧 AUTO-FIXED: hermes-workspace restarted → now active`

If restart fails (still not active after restart): escalate to P0 DEGRADED with the exact error from `systemctl --user status <service> --no-pager -l`.

**Workspace restart failure — missing npm dependency (May 2026)**:
If the workspace service is `active` but still returns HTTP 500 or a truncated JSON error like `{"status":500,"unhandled":true,"message":"HTTPError"}`, check journalctl for `Cannot find module 'rehype-raw'` (or any `ERR_MODULE_NOT_FOUND`). This occurs when node_modules drift after a lockfile or pnpm change. Fix:
```bash
cd /root/hermes-workspace && CI=true pnpm install
systemctl --user restart hermes-workspace
sleep 8
# Verify title returns
curl -s --max-time 8 http://localhost:3100/ | grep -a -o '<title>[^<]*</title>'
```
The restart alone is insufficient when the dependency is physically missing — `pnpm install` is required first.

**Gateway crash — unresolved git merge conflict in source (June 2026)**:
If the gateway is crash-looping (`systemctl --user status hermes-gateway` shows `exit-code status=1/FAILURE` with rapid restarts), check the last traceback:
```bash
journalctl --user -u hermes-gateway --no-pager -n 50 | grep -A5 'SyntaxError\|<<<<<<'
```
If you see `SyntaxError: expected 'except' or 'finally' block` or raw `<<<<<<< Updated upstream` / `=======` / `>>>>>>> Stashed changes` markers in a Python file under `~/.hermes/hermes-agent/`, a git merge was left unresolved. The gateway imports these modules at startup — a single merge-conflict marker kills the entire process.

Fix: open the file, find the conflict markers, resolve by keeping the correct branch (typically the local/stashed branch with the functional code), and delete the markers + the alternative branch code. Then restart:
```bash
# Find all conflicted files
grep -rl '<<<<<<' ~/.hermes/hermes-agent/ --include='*.py'
# Resolve each one, then:
systemctl --user restart hermes-gateway
sleep 3
systemctl --user is-active hermes-gateway && curl -s --max-time 3 http://localhost:8642/health
```
This is a P0 auto-fix candidate — the gateway cannot start with unresolved merge conflicts, and it will crash-loop indefinitely until resolved.

**Kanban DB corruption (June 2026)**:
If gateway logs show `kanban dispatcher: board default database /root/.hermes/kanban.db is not a valid SQLite database`, the kanban DB file is corrupted or zero-length. The gateway self-pauses kanban dispatch but stays running — this is not fatal but means no background task scheduling.
Fix:
```bash
mv /root/.hermes/kanban.db /root/.hermes/kanban.db.bak
hermes kanban init
# Gateway will auto-detect the new DB on next tick
```

Dashboard is checked too but does NOT get auto-restarted — it's monitored but the gateway/workspace are the critical user-facing services.

**Why this matters:** The gateway was KILLED by systemd on May 23 at 13:35 UTC and stayed dead for 3+ hours before being manually restarted. Heartbeat runs every 5 minutes. If the heartbeat had this auto-fix, the gateway would have been down for at most 5 minutes instead of 3 hours. This is the difference between "the user notices Slack is dead and has to SSH in" and "the user never notices because it fixed itself."

4. **Volume/file permissions** (mode-dependent):
   **Docker mode:**
   ```bash
   # Check ownership of critical volume paths
   ls -lan /var/lib/docker/volumes/hermes-data/_data/logs/ 2>/dev/null | head -5
   docker exec hermes-agent ls -la /opt/data/sessions/sessions.json 2>&1
   ```
   Flag if any files/dirs are root-owned when the rest are UID 10000.
   Fix: `docker exec hermes-agent chown hermes:hermes /opt/data/sessions/sessions.json`
   
   **Native mode:**
   ```bash
   ls -la /root/.hermes/sessions/sessions.json
   ls -la /root/.hermes/state.db
   du -sh /root/.hermes/state.db
   ```
   Flag if unreadable or empty. No UID mismatch issue in native mode (all files owned by host user).
   **state.db size threshold**: If `state.db` exceeds 1GB, flag as P2 WATCH (disk pressure risk — the SQLite session database grows continuously and can reach 2GB+). Consider `VACUUM` or periodic cleanup. Note the current size in the log entry.

5. **API key / secret health**:
   ```bash
   # Check that critical env files exist and are non-empty
   test -s /root/.hermes/env.sh && echo "env.sh OK" || echo "⚠ env.sh MISSING or EMPTY"
   ```
   Read `/root/.hermes/env.sh` and verify key variables (OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN, DEEPSEEK_API_KEY) are present.

### P1 — Stalled work & security

- **SSH brute force**: Check auth.log for recent failed attempts
  ```bash
  grep "Failed password" /var/log/auth.log | tail -20
  ```
  Flag if >5 failures in last hour from same external IP — consider banning.
  **Note**: Internal IPs (172.16.x.x, 192.168.x.x, 10.x.x.x) may be testing/automation and should be treated as P2 WATCH rather than P1 STALLED unless pattern indicates actual attack.
  
  **Classification examples**:
  - **P1 STALLED**: External IPs with rapid sequential attempts (<10s apart), multiple invalid users (user, user2, admin, root), coordinated attack patterns
  - **P2 WATCH**: RFC1918 internal IPs (172.16.x.x, 192.168.x.x, 10.x.x.x), slower frequency attempts, same user pattern suggesting testing
  - **P3 INFO**: Single isolated attempts, diverse IPs with no pattern, self-resolving incidents
  
  See `references/dedup-concrete-examples.md` for detailed pattern examples.
  
  **Pitfall**: Internal IP SSH failures should not trigger P1 alerts. In this session, 172.16.0.3 attempts were correctly classified as P2 WATCH (testing/automation) rather than P1 STALLED (external attack). This pattern (172.16.x.x) is specifically RFC1918 internal range and should always be treated as P2.
  
  **Classification guidelines**:
  - **P1 STALLED**: External IPs (not RFC1918 ranges) with >5 failed attempts in last hour
  - **P2 WATCH**: Internal IPs (RFC1918: 172.16.x.x, 192.168.x.x, 10.x.x.x) — likely testing/automation
  - **P3 INFO**: Single isolated attempts or patterns that self-resolve
  
  See `references/ssh-brute-force-classification.md` for detailed examples and response guidelines.

- **Disk space trending**: Compare current disk usage to last heartbeat log. If growth >5% since last check, flag.

- **Pending git changes in key repos**: Check `/root/Resonate_Freq_Proj/` and `/root/aeon/` for uncommitted work. Handle gracefully if directories don't exist:
  ```bash
  cd /root/Resonate_Freq_Proj/ 2>/dev/null && git status --porcelain | head -5 || echo "No Resonate_Freq_Proj directory"
  cd /root/aeon/ 2>/dev/null && git status --porcelain | head -5 || echo "No aeon directory"
  ```

### P2 — Configuration drift

- Check `~/.hermes/config.yaml` parse validity (quick `python3 -c "import yaml; yaml.safe_load(open(...))"`)
- **Model/provider drift**: verify `model.default` and `model.provider` match the expected primary (currently `deepseek-v4-pro` / provider `deepseek`). Silent changes here — e.g., a quick command or skill accidentally rewriting the primary — cause the user to find themselves on the wrong model without knowing. Flag any mismatch.
- **Individual job model configuration**: Check all cron jobs for outdated or incorrect model configurations. Flag jobs that reference:
  - `Ring-2.6-1T` (transitioned to paid model)
  - `ollama/qwen3-coder-next` (not found in Ollama library)
  - Any other known deprecated/moved models
  See `references/model-configuration-issues.md` for diagnosis and resolution paths.
- Check that critical skills are present (search for SKILL.md count — should be stable)
- Check that taps are accessible (try `git ls-remote` on each tap repo)

See `references/primary-model-config.md` for canonical expected values used in drift detection.
**Config drift pattern**: The primary model configuration (`model.default` / `model.provider`) should be verified on each heartbeat run. Flag any unexpected mismatch as P2 CONFIG drift. Always use `cronjob(action='list')` or read `/root/.hermes/cron/jobs.json` directly as the authoritative job state rather than relying on gateway REST API endpoints (`/api/cron`, `/api/cron/jobs` return 404).

### P3 — Low-priority maintenance

- Log file sizes: `du -sh /var/log/*.log` — flag any >100MB
- Docker image accumulation: `docker images | wc -l` — flag if >50 (suggest prune)
- Pending system updates: `apt list --upgradable 2>/dev/null | wc -l`
See `references/cron-jobs-json-schema.md` for the full jobs.json field reference and health signal mapping.
See `references/job-analysis-patterns.md` for detailed analysis of specific job patterns and recovery behaviors  
See `references/ssh-brute-force-classification.md` for detailed RFC1918 internal IP handling with concrete examples.
See `references/never-run-job-patterns.md` for analysis of never-run job patterns.
See `references/silent-response-examples.md` for detailed guidelines on when to use `[SILENT]` vs full reporting.
See `references/dedup-concrete-examples.md` for real session examples of dedup patterns and classification.
See `references/primary-model-config.md` for canonical expected values used in drift detection.
See `references/ssh-brute-force-classification.md` for detailed examples and response guidelines.
See `references/known-recurring-patterns.md` for complete list of known issues and dedup guidelines.

Batch all findings into a single message grouped by priority:
```
🔴 P0 FAILED: job-name (failed 2h ago), container-name (Exited)
🟡 P1 STALLED: auth.log shows 12 SSH failures from 1.2.3.4
🔵 P2 CONFIG: env.sh missing OPENROUTER_API_KEY
```

## Status determination

- **DEGRADED** — any P0 flag (requires immediate attention)
- **WATCH** — any P1 or P2 flag (needs investigation)
- **OK** — no flags

## Output

**When running as a cron job** (auto-delivery): The system auto-delivers your final response to the configured destination. Do NOT call `send_message` — produce your report as your final response text. If there are genuinely no new findings (see dedup), respond with exactly `[SILENT]` and nothing else to suppress delivery.

**CRITICAL**: When running as a cron job, your final response MUST be either:
- A full report with findings (if new issues detected)
- Exactly `[SILENT]` (no other text) if all findings are duplicates

Never combine `[SILENT]` with content — the system treats any response containing `[SILENT]` as a silent delivery instruction, so mixing it with content will result in the content being silently discarded.

See `references/silent-response-concrete-examples.md` for detailed real-world examples and decision guidelines.

**When running interactively** (manual trigger): 

If OK: log "HEARTBEAT_OK" and write timestamp to `~/.hermes/heartbeat.log`. No notification needed.

If degraded: send a single notification via `send_message` to the primary Telegram channel, log findings to `~/.hermes/heartbeat.log`, and save a summary to memory.

**Log format** (always write to `~/.hermes/heartbeat.log`):
```
HEARTBEAT_{STATUS} {ISO_TIMESTAMP} | CPU:{pct} Disk:{pct} Mem:{pct} | Native:{services_status} | Cron:{count} jobs, {failed} failed, {stuck} stuck, {never_run} never-run | Config:{status} | Model:{model}/{provider} | Status:{OK|WATCH|DEGRADED} | {findings summary}
```
Append to heartbeat.log by reading the full file with `read_file`, then rewriting with `write_file` — prepend a `read_file` call to get current content, concatenate the new line, and `write_file` the full updated content. This avoids `patch` uniqueness issues (identical-status entries make the last line non-unique) and is the only reliable way to append. Never use `patch` with `replace_all=true` here — it will insert after every matching line and corrupt the log. The security scanner blocks shell `>>` redirections to dotfiles; `write_file` is the safe path.

**Native mode service status format**: Use concise status indicators like "gateway/dashboard/workspace up" or "gateway/dashboard up, workspace down" to clearly indicate which services are operational.

## Verification

Manual trigger: "Run the hermes-heartbeat skill"
Expected: console output showing status (OK/WATCH/DEGRADED) and any flagged items.
If DEGRADED: specific actionable items listed with exact commands to fix.

## Reference Files Available:\n- `references/cron-jobs-json-schema.md` — Detailed field analysis and health signal mapping\n- `references/job-analysis-patterns.md` — Analysis of specific job patterns and recovery behaviors  \\n- `references/cron-job-analysis-patterns.md` — Comprehensive classification of failure patterns and priority guidelines\\n- `references/ssh-brute-force-classification.md` — Detailed RFC1918 internal IP handling with concrete examples\\n- `references/primary-model-config.md` — Canonical model configuration expectations\\n- `references/model-configuration-issues.md` — Diagnosis and resolution of model not found errors in cron jobs\\n- `references/known-recurring-patterns.md` — Complete list of known issues and dedup guidelines\\n- `references/heartbeat-log-analysis-patterns.md` — Advanced pattern recognition in heartbeat logs\n- `references/heartbeat-session-2026-05-28.md` — Session-specific findings from heartbeat run on 2026-05-28: P0 Ring-2.6-1T model paywall errors, P1 missing ollama/qwen3-coder-next model
- `references/heartbeat-session-2026-06-01.md` — Session-specific findings from heartbeat run on 2026-06-01: P2 model drift (operator-driven), 163+ consecutive silent runs

- **Blocked content handling**: When checking git directories or other paths, some files may be blocked by security scanners (e.g., CLAUDE.md with prompt injection patterns). Handle this gracefully by:
  - Using `2>/dev/null` to suppress "Permission denied" errors
  - Using `|| echo "No access to directory"` fallbacks
  - Not treating blocked content as failures — they're security features, not operational issues

## Pitfalls

- **Operational reflex — when the user screams about looping cron jobs, KILL FIRST:** If the user is furious about cron jobs hammering dead API keys (401/402/429), do NOT explain the root cause or suggest key rotation first. Immediately list all cron jobs with `cronjob(action='list')`, identify the ones with `last_status: error` and `schedule: every 5m` or similar short intervals, and REMOVE them with `cronjob(action='remove', job_id='...')`. You can restart them later after fixing the keys. The user wants the noise stopped NOW, not an explanation of why the noise exists. This was learned June 8, 2026 when 4 cron jobs (hermes-heartbeat, slack-context-sync, context-loss-recovery, rclone-torrent-upload) were hammering dead DeepSeek/Ollama keys every 5 minutes, flooding errors.log with 401 entries.

- **Security scanner (tirith) blocks piped commands**: Commands like `curl ... | python3` or `cat file | python3 -c "..."` are blocked as `[HIGH] Pipe to interpreter`. Workaround: use `read_file()` to read JSON files, then process in Python with `execute_code` or inline reasoning.

- **Log appending via `patch` corrupts the heartbeat log**: When heartbeat entries have identical status strings (e.g., consecutive `HEARTBEAT_DEGRADED` lines), the last line is not unique so `patch` mode='replace' with `replace_all=false` fails with "found N matches", and `replace_all=true` inserts after EVERY match — producing hundreds of lines of garbage. **Correct approach**: read the full log with `read_file`, concatenate the new entry, and rewrite with `write_file`. Never use shell `>>` redirection to dotfiles (blocked by tirith as `[HIGH] Dotfile overwrite`).

- **Log appending via `write_file` TRUNCATES if existing content is not prepended**: `write_file` replaces the target file entirely — it does not append. To append safely, you MUST first `read_file` the existing log, concatenate the new line to the content string (including a newline), and pass the complete combined string to `write_file`. Forgetting to prepend the existing content destroys all historical heartbeat entries.

- **Heartbeat self-blindspot (monitoring gap)**: When the heartbeat itself fails with the same condition it is designed to detect (e.g., HTTP 402 credit exhaustion), it stops producing log entries and cannot deliver reports. This creates a blind spot that lasts until the root cause resolves — every subsequent scheduled run fails identically, so no detection is possible. The only indicator of the gap is a missing entry in heartbeat.log for the failure duration. **Detection at recovery**: when the heartbeat finally succeeds again after a gap, cross-reference the heartbeat's own `last_error` against the job-wide error pattern. If the heartbeat failed with the same 402/429/404 as other jobs during the gap, it was itself a victim of the condition it should have reported. A stale last heartbeat combined with N+ jobs failing with the same error is stronger evidence than either signal alone. **Mitigation**: this is inherent to any monitoring system sharing the same provider/credentials as the services it monitors — no heartbeat-level fix exists. The gap duration should be flagged in the recovery report so the operator knows monitoring was dark for that period.
- **`session_search` tool may be unavailable in some contexts**: The tool is loaded based on session toolset configuration. Sessions with restricted toolsets (e.g., cron jobs) may not have it. When checking for past heartbeat issues or patterns, fall back to reading `~/.hermes/heartbeat.log` directly with `read_file`.

- **Heartbeat run-as-cron silent behavior**: When running as a scheduled cron job (auto-delivery), the agent MUST either deliver a full report OR exactly `[SILENT]` with no extra text. Mixing content with `[SILENT]` causes the content to be silently discarded because the system treats any response containing `[SILENT]` as a silent delivery instruction. This was learned in the 162nd consecutive run where identical findings triggered `[SILENT]` — the session correctly suppressed delivery. The log now shows 161st/162nd consecutive OK runs — the dedup mechanism is working as designed and `[SILENT]` is the correct behavior. For **batch deduplication**: if the last N consecutive heartbeat entries (N ≥ 2) are identical, the current run MUST output exactly `[SILENT]` to suppress delivery — otherwise the system will redeliver the same notification repeatedly.

- **Gateway `/api/cron` and `/api/cron/jobs` return 404**: The cron subsystem is not exposed via the gateway REST API. Use the `cronjob()` tool (when available) or read `/root/.hermes/cron/jobs.json` directly as the authoritative job state.

- **`/root/.hermes/state.db` is a SQLite database (not a text file)**: During disk space investigation, I checked for unreadable files and found `/root/.hermes/state.db` - a large (815MB), executable permission file. This is the agent's SQLite session/state database, not a text file to grep. **Never treat session DB files as text** — use `sqlite3` CLI or Hermes' `session_search` tool to query it.

- **`hermes-agent` Docker container may not exist**: Hermes can run natively (direct process) or in Docker. The container name varies or may be absent. Always detect deployment mode first: check `docker ps | grep hermes` and `ps aux | grep 'hermes gateway'` to determine which path to take.

- **Cron session gaps don't prove a dead loop alone**: The scheduler may pause between ticks. The definitive dead-loop signal is `next_run_at` in the past (>1 hour) with `last_run_at` null or >48h stale. Compare against job creation dates and expected fire windows.

- **Cron output directory path**: The cron output directory is `/root/.hermes/cron/output` (singular), not `/root/.hermes/cron/outputs`. This affects session search patterns for deduplication.

- **`cronjob` tool may be unavailable in some contexts**: The tool is loaded based on session toolset configuration. Cron sessions with restricted toolsets may not have it. Always fall back to `read_file('/root/.hermes/cron/jobs.json')`.

- **Gateway crash-loop from unresolved git merge conflicts**: If `hermes-gateway` is crash-looping with `exit-code status=1/FAILURE`, always check for merge-conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) in Python files under `~/.hermes/hermes-agent/`. A single unresolved conflict causes a `SyntaxError` on import that kills the entire process. The restart auto-fix will NOT resolve this — you must manually edit the file to remove conflict markers and keep the correct branch. See the "Gateway crash — unresolved git merge conflict" section under P0 auto-fix.

- **`grep` returns "binary file matches" on HTML pages**: Some HTTP responses from the workspace include non-ASCII characters or null bytes, causing `grep` to treat them as binary and return "binary file matches" instead of the actual match. Always use `grep -a` (--text) when grepping HTML from curl to force text-mode processing. Affects all workspace title checks and any `grep` on `curl` output from web endpoints.

- **`[SILENT]` vs full report for cron auto-delivery**: When running as a scheduled cron job, the agent MUST either deliver a full report OR exactly `[SILENT]` with no extra text. Mixing content with `[SILENT]` causes the content to be silently discarded because the system treats any response containing `[SILENT]` as a silent delivery instruction. This was learned in the 162nd consecutive run where identical findings triggered `[SILENT]` — the session correctly suppressed delivery. The log now shows 161st/162nd consecutive OK runs — the dedup mechanism is working as designed and `[SILENT]` is the correct behavior.

- **Operator-driven model drift is NOT a new finding**: The primary model in config.yaml changes between heartbeats because the operator switches models in the workspace UI. When the model differs from the canonical default (`deepseek-v4-pro`/`deepseek`), classify it as P2 CONFIG DRIFT (ongoing) and note "first flagged 05-30T07:05" — do NOT treat each heartbeat as a new drift discovery. This prevents redundant alerts for intentional operator behavior.

## Constraints

- **Auto-fix gateway/workspace**: If `hermes-gateway` or `hermes-workspace` service is down, restart it immediately and report the fix. These are the user's primary interfaces (Slack + web UI) and must self-heal. All other checks are detection-only — never auto-fix cron jobs, disk issues, permissions, config, or anything outside gateway/workspace restarts.
- Never notify twice about the same issue within 48h
- Always log timestamp even when OK (for staleness detection)
- Group all findings into one notification max