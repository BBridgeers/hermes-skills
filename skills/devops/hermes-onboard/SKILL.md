---
name: hermes-onboard
description: Comprehensive setup validator for Hermes Agent — checks VPS environment, API keys, service health (Docker or native), platform connectivity (Slack/Telegram), skills integrity, and cron job health.
tags: [meta, devops, validation]
---

# Hermes Onboard — Setup Validator

Validates that Hermes Agent is correctly configured and all subsystems are operational. Supports both Docker and native (bare-metal) deployments.

## Purpose

Convert a freshly-configured Hermes instance into a known-working state in one pass. Every gap comes with the exact command that fixes it.

## Deployment Mode Detection

Before running checks, determine the deployment mode:

```bash
# If this returns hermes-agent or hermes-workspace containers → DOCKER mode
docker ps --format '{{.Names}}' 2>/dev/null | grep -i hermes

# If hermes runs natively (hermes doctor shows terminal backend: local) → NATIVE mode
hermes status --all 2>&1 | grep "Backend:"
```

Most checks apply to both modes. Where they differ, follow the mode-specific variant.

## Checks

### 1. Core files present
- `~/.hermes/config.yaml` exists and is valid YAML
- `~/.hermes/.env` exists and is non-empty (native) OR `~/.hermes/env.sh` (Docker)
- `~/.hermes/skills/` directory exists with SKILL.md files
- Fix: `touch ~/.hermes/.env && chmod 600 ~/.hermes/.env`

### 2. API keys configured
Read `~/.hermes/.env` and verify:
- `DEEPSEEK_API_KEY` set and non-empty (primary provider)
- `OPENROUTER_API_KEY` set and non-empty (fallback/compression)
- Platform keys: `SLACK_BOT_TOKEN` (primary platform) and/or `TELEGRAM_BOT_TOKEN`
- Fix: `nano ~/.hermes/.env` (add missing keys)

### 3. Service health

**Native mode — three services must be running for full functionality:**

| Service | Port | Required For |
|---|---|---|
| Gateway | 8642 | Core agent, chat, tool execution |
| Dashboard | 9119 | Workspace models, config, sessions, skills, cron UI |
| Workspace | 3100 | Web UI (separate from agent) |

```bash
# Quick port sweep:
ss -tlnp | grep -E "8642|9119|3100"

# Gateway should be running as systemd user service
hermes gateway status
systemctl --user is-active hermes-gateway

# Dashboard — if missing, workspace model picker and config will be dead
# See devops/hermes-workspace-deployment for full native setup procedure
# and devops/hermes-workspace-models-config-fix for model list sync
curl -s --max-time 3 http://127.0.0.1:9119/ | head -3

# Doctor check (catches most issues)
hermes doctor
```

**⚠ Dashboard is mandatory for workspace functionality.** Without port 9119, the workspace cannot populate the model picker dropdown, load sessions, edit config, or access skills/cron screens. The gateway alone (8642) only provides chat — everything else needs the dashboard.

### 3. Service health
- **Native deployment**: Check systemd services are active
  ```bash
  systemctl --user is-active hermes-gateway hermes-dashboard hermes-workspace
  ```
- **Docker deployment**: Check containers are up
  ```bash
  docker ps --format "{{.Names}}: {{.Status}}"
  ```
- Verify gateway restart loop NOT occurring (gateway overwrites manual service files):
  ```bash
  journalctl --user -u hermes-gateway --no-pager -n 10 | grep -c "Scheduled restart"
  ```
  If restart counter > 0: the service file was manually written. Fix: `hermes gateway install`
- Verify ports listening: `ss -tlnp | grep -E "8642|9119|3100"`
- Fix native: `systemctl --user restart hermes-gateway hermes-dashboard hermes-workspace`
- Fix Docker: `docker compose -f /opt/hermes/docker-compose.yml up -d`
### 3b. Swap exists (VPS-level)
Without swap, a memory spike triggers the OOM killer → gateway SIGKILL with no graceful degradation.
```bash
free -h | grep Swap | awk '{print $2}'
```
If zero: `fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile && echo '/swapfile none swap sw 0 0' >> /etc/fstab`

### 4. Platform connectivity

**Slack (primary):**
```bash
curl -s --max-time 5 -X POST "https://slack.com/api/auth.test" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN"
```
Verify: `"ok": true` in response.

**Telegram:**
```bash
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

### 5. Cron jobs operational
List all cron jobs via cronjob tool. Verify:
- At least one job is configured (heartbeat minimum)
- No jobs in permanent failure state
- Fix: `cronjob(action='create', schedule='every 5m', prompt='Run hermes-heartbeat skill', name='heartbeat', skills=['hermes-heartbeat'])`

### 6. Skills integrity
- Count SKILL.md files: `find ~/.hermes/skills/ -name "SKILL.md" | wc -l`
- Verify no SKILL.md files are empty or corrupt
- Check critical skills load: hermes-heartbeat, skill-repair
- **Docker only**: verify skills directory ownership matches container user (uid 10000):
  ```bash
  stat -c '%U:%G' ~/.hermes/skills/*/SKILL.md | sort -u
  ```
  If `root:root`: `chown -R 10000:10000 ~/.hermes/skills && chmod -R u+rwX ~/.hermes/skills`
- **Native**: ownership should be the user running hermes (typically root or the user account)
- Fix: `hermes skills update` or re-clone from taps

### 7. Memory system functional
- Memory tool can read and write (test with a probe entry, then remove)
- Honcho is accessible if configured: `docker ps | grep honcho` + `curl -s http://localhost:8000/health`
- Fix: Check config.yaml for memory configuration

### 7b. Workspace health (native deployments)

If workspace is deployed natively alongside the agent:
```bash
# Port listening?
ss -tlnp | grep -E "3100|3000"

# HTML serving? (first request may be slow — Vite lazy compilation)
curl -s --max-time 30 http://127.0.0.1:3100 | head -5

# Gateway bridge healthy?
curl -s http://127.0.0.1:8642/health
```
Verify workspace `.env` has `HERMES_API_TOKEN` matching gateway's `API_SERVER_KEY`.
Without this, all workspace↔gateway API calls return 401.

⚠ **models.json sync**: The workspace model picker reads `~/.hermes/models.json` — NOT
config.yaml directly. If this file is missing or stale, the workspace will show only the
default model. Sync with: `python3 ~/.hermes/skills/devops/hermes-workspace-models-config-fix/scripts/sync-models-json.py`
Then restart workspace: `systemctl --user restart hermes-workspace`.

### 7c. Gateway service pitfall

**Never write the gateway systemd unit file manually.** The gateway self-manages its
service definition. On startup, it detects mismatches, overwrites the file, and runs
`systemctl daemon-reload` — which triggers SIGTERM → SIGKILL → restart loop.

Symptoms: `systemctl --user is-active hermes-gateway` returns "activating" perpetually.
Journal shows: "Updated gateway user service definition" followed by SIGKILL every 5 min.

Fix:
```bash
systemctl --user stop hermes-gateway
rm ~/.config/systemd/user/hermes-gateway.service
systemctl --user daemon-reload
hermes gateway install      # let the gateway generate its own service file
hermes gateway start
```

### 7d. Dashboard startup (native)

The `hermes dashboard` CLI may fail with Docker errors on native deployments.
Workaround: call the Python module directly in the systemd service:
```
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python3 -m hermes_cli.main dashboard --port 9119 --host 127.0.0.1 --skip-build --no-open
```
Set `HERMES_WEB_DIST` to the pre-built web dist path. Pre-build with:
```bash
cd /usr/local/lib/hermes-agent/web && npm install && npm run build
```

### 8. Network / firewall — MANDATORY TWO-LAYER REQUIREMENT

**For external access, you MUST configure BOTH layers — UFW on VPS AND Hostinger HPanel cloud firewall — or the port is unreachable from outside. Missing either = 502/Connection refused.**

1. **UFW (VPS firewall)**:
   ```bash
   ufw allow <port>/tcp
   ufw status verbose | grep <port>
   ```
   Example: `ufw allow 3002/tcp`

2. **Hostinger HPanel (cloud firewall)** — **REQUIRED**:
   - Go to `https://panel.hostinger.com`
   - Navigate to **VPS → Firewall** (left menu for your server)
   - Click **Add Rule**
   - Port: `<port>`, Protocol: `TCP`, Action: `Allow`
   - Apply

**DO NOT proceed to verification until BOTH layers show the port is ALLOWED.**

- Outbound internet: `curl -s --max-time 5 https://api.deepseek.com/v1/models > /dev/null`
- DNS: `nslookup api.deepseek.com`
- Verify port accessible from outside: `curl -s -o /dev/null -w "%{http_code}\n" "http://<public-ip>:<port>"`
- Fix: Configure both UFW AND Hostinger HPanel firewall rules

### 9. (Optional) SSH security
- Check auth.log for brute force attempts: `grep "Failed password" /var/log/auth.log | wc -l` (last 24h)
- Verify SSH key-only auth: `grep "^PasswordAuthentication" /etc/ssh/sshd_config`
- Fix: Configure fail2ban or switch to key-only auth

### 10. (Optional) Backup strategy
- Check if any backup cron jobs exist
- Verify critical files are backed up: `~/.hermes/`
- Fix: Configure rclone or rsync backup

### 11. Co-tenant agent CLIs
- See `references/installed-agent-clis.md` for full inventory of coding agent CLIs on this VPS (Claude Code, Codex, Pi, OpenCode, Antigravity) — paths, versions, skill directories, and bundle recommendations.

### 12. Keeping Hermes Updated (bare-metal)

For git-installed Hermes at `/usr/local/lib/hermes-agent/`, `git pull` alone
is insufficient — `hermes --version` can report "Up to date" while the venv
runs stale code. Full procedure in `references/bare-metal-update.md`.

## Quick Health Check (abbreviated)

For routine checks (not onboarding), run a focused subset:

```bash
# The three high-signal commands:
hermes doctor                          # Config, API keys, connectivity, tools
hermes status --all                    # Platform, gateway, cron, model
hermes gateway status                  # Gateway process health
```

## Output format

Group by status:
```
*Hermes Onboarding — {date}*  |  Mode: {native|docker}

{verdict_one_liner}

✅ Passing (N)
• check — detail

⚠ Warnings (N)
• check — detail
    fix: command

❌ Failing (N)
• check — detail
    fix: command

Next: {action}
```

Verdict:
- All pass → "All set — Hermes is fully operational."
- Only warnings → "Hermes will run, but {N} optional item(s) need attention."
- Any failures → "Setup incomplete — {N} required item(s) need attention."

## Constraints

- Never fabricate fixes. If unknown, say so.
- Do not auto-mutate config. Onboard is read-only diagnosis.
- One pass, one report. Don't loop.
- Detect deployment mode before running checks — don't assume Docker.
- Hard cap output at ~3500 chars.
