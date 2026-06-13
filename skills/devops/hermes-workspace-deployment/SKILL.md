---
name: hermes-workspace-deployment
description: Deploy Hermes Workspace natively on bare-metal alongside a native Hermes Agent — clone, configure, build, systemd service, and Tailscale access. Covers the full end-to-end workflow and common pitfalls.
tags: [devops, workspace, deployment, native, systemd, tailscale]
---

# Hermes Workspace — Native Deployment

Deploy `outsourc-e/hermes-workspace` (the web UI) on bare metal alongside a native Hermes Agent installation. Covers prerequisites, build, systemd service, remote access, and every pitfall we hit in production.

## Prerequisites

- Node 22+, npm, pnpm (`npm install -g pnpm`)
- Hermes Agent already installed and gateway running natively on port 8642
- Hermes Dashboard running natively on port 9119 (required for model picker, config, sessions, skills, cron)
- `API_SERVER_ENABLED=true` and `API_SERVER_KEY=<secret>` in `~/.hermes/.env`
- Linger enabled: `sudo loginctl enable-linger $USER`

## Port Binding for External Access

Both services bind to `127.0.0.1` by default. For external access (VPS public IP), services must bind to `0.0.0.0`.

- **Hermes Workspace (Vite dev)**: `vite dev --host 0.0.0.0 --port 3100`
- **veracar-app (Next.js)**: `PORT=3002 HOSTNAME=0.0.0.0 npx next start`

**Critical**: Services bound to `127.0.0.1` respond to curl from VPS but return 502 when accessed via public IP due to browser proxy misconfiguration. Binding to `0.0.0.0` fixes this.

## 1. Clone and Update

```bash
cd ~
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace
git pull --ff-only origin main   # if already cloned
```

## 2. Configure .env

Create `/root/hermes-workspace/.env`:

```
HERMES_API_URL=http://127.0.0.1:8642
HERMES_API_TOKEN=<same value as API_SERVER_KEY in ~/.hermes/.env>
HERMES_PASSWORD=<strong-workspace-password>
PORT=3100
HOST=127.0.0.1
```

**Critical**: `HERMES_API_TOKEN` MUST match the gateway's `API_SERVER_KEY`. Without this, all workspace ↔ gateway API calls return 401. The gateway's `/health` endpoint answers without auth, but `/api/sessions`, `/api/models`, and all other dashboard-backed routes require the token.

If port 3000 is already in use (e.g., by mission-control), set `PORT=3100` or another free port.

## 3. Build

**Pitfall — pnpm approval loop**: `pnpm install` in CI/non-TTY contexts blocks on an interactive approval prompt for `esbuild` and `unrs-resolver` build scripts. `CI=true pnpm install` works for the install step but `pnpm build` re-runs install internally and fails again.

**Workaround**: Install deps with `CI=true pnpm install`, then build with `npx vite build` directly:

```bash
CI=true pnpm install
NODE_OPTIONS="--max-old-space-size=2048" npx vite build
```

The build output goes to `dist/server/`. For the dashboard web UI needed by `hermes dashboard`:

```bash
cd /usr/local/lib/hermes-agent/web
npm install && npm run build
# Output: /usr/local/lib/hermes-agent/hermes_cli/web_dist/
```

## 4. Start (Development)

For development with hot-reload:

```bash
cd ~/hermes-workspace
NODE_OPTIONS="--max-old-space-size=2048" npx vite dev --port 3100 --host 127.0.0.1
```

For production (pre-built):

```bash
NODE_OPTIONS="--max-old-space-size=2048" node dist/server/server.js
```

## 5. Systemd Service

Create `/root/.config/systemd/user/hermes-workspace.service`:

```ini
[Unit]
Description=Hermes Workspace - Web UI
After=network-online.target hermes-gateway.service hermes-dashboard.service
Wants=network-online.target hermes-gateway.service hermes-dashboard.service
StartLimitIntervalSec=0

[Service]
Type=simple
ExecStart=/usr/bin/npx vite dev --port 3100 --host 127.0.0.1
WorkingDirectory=/root/hermes-workspace
Environment="PATH=/root/.hermes/node/bin:/usr/local/lib/hermes-agent/venv/bin:/usr/bin:/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="NODE_OPTIONS=--max-old-space-size=2048"
Environment="HERMES_API_URL=http://127.0.0.1:8642"
Environment="HERMES_API_TOKEN=<your-token>"
Environment="HERMES_DASHBOARD_URL=http://127.0.0.1:9119"
Restart=always
RestartSec=5
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

Then:

```bash
systemctl --user daemon-reload
systemctl --user enable hermes-workspace
systemctl --user start hermes-workspace
```

## 6. Dashboard Service (separate, required)

The workspace needs the Hermes Dashboard on port 9119 for models, config, sessions, skills, and cron. The dashboard is part of hermes-agent but requires its own systemd service.

**Pitfall**: `hermes dashboard` CLI may fail with Docker errors ("No such container: hermes-agent") on native deployments. Workaround: call the Python module directly.

Create `/root/.config/systemd/user/hermes-dashboard.service`:

```ini
[Unit]
Description=Hermes Dashboard - Config, Models, Sessions
After=network-online.target hermes-gateway.service
Wants=network-online.target hermes-gateway.service
StartLimitIntervalSec=0

[Service]
Type=simple
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python3 -m hermes_cli.main dashboard --port 9119 --host 127.0.0.1 --skip-build --no-open
WorkingDirectory=/usr/local/lib/hermes-agent
Environment="PATH=/usr/local/lib/hermes-agent/venv/bin:/root/.hermes/node/bin:/usr/bin:/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="VIRTUAL_ENV=/usr/local/lib/hermes-agent/venv"
Environment="HERMES_HOME=/root/.hermes"
Environment="HERMES_WEB_DIST=/usr/local/lib/hermes-agent/hermes_cli/web_dist"
Restart=always
RestartSec=5
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

## 7. Gateway Service Pitfall

**Never write the gateway systemd unit file manually.** The gateway self-manages its service definition. On startup, it detects mismatches between the installed unit and its expected definition, overwrites the file, and runs `systemctl daemon-reload` — which triggers SIGTERM → SIGKILL → 5-minute restart loop.

Fix:
```bash
systemctl --user stop hermes-gateway
rm ~/.config/systemd/user/hermes-gateway.service
systemctl --user daemon-reload
hermes gateway install       # let the gateway generate its own service file
hermes gateway start
```

Also remove any stale system-level service: `sudo hermes gateway uninstall --system`

## 8. Remote Access via Tailscale Serve

Workspace (3100) and dashboard (9119) bind to 127.0.0.1. For phone/remote access, use Tailscale Serve:

```bash
# Install + authenticate
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up   # → visit auth link

# Enable Serve on tailnet (one-time admin action via link)

# Expose services
tailscale serve --bg --https=443 http://127.0.0.1:3100      # workspace
tailscale serve --bg --https=8443 http://127.0.0.1:9119     # dashboard
```

Workspace: `https://<hostname>.<tailnet>.ts.net`
Dashboard: `https://<hostname>.<tailnet>.ts.net:8443`

Do NOT enable Funnel — it exposes services to the public internet. Serve keeps them tailnet-only.

WireGuard coexistence: if an existing WireGuard container runs on the VPS (UDP 51820), Tailscale installs alongside without conflict. Different port, different interface.

## 9. Models Sync

The workspace model picker reads `~/.hermes/models.json` — NOT `~/.hermes/config.yaml`. The CLI stores model data in config.yaml. These files go out of sync whenever the user adds providers via `/model`, changes the default model, or when upstream APIs add new models. They are **not auto-synced**.

**Format**: `~/.hermes/models.json` is an array of `{"model": "model-id", "provider": "provider-name"}`.

### When to Sync

- User says "models missing in workspace" or "model picker only shows 1–2 models"
- After running `/model` to add/change providers
- After adding new API keys (OpenRouter, OpenCode, etc.) that unlock additional models
- Periodically to pick up newly released free models on OpenRouter

### Sources (Priority Order)

1. **`~/.hermes/models.json`** — primary source. If missing or empty, the picker falls back to just the gateway default (usually 1 model).
2. **Gateway `/v1/models`** — OpenAI-compatible endpoint. Requires auth. Usually sparse.
3. **Local Ollama** — auto-discovered if Ollama is running on the VPS.

### Sync Procedure

**Recommended**: Use the bundled sync script (runs all five phases in one pass):

```bash
python3 ~/.hermes/skills/devops/hermes-workspace-deployment/scripts/sync-models.py
```

The script pulls from five sources:

1. **config.yaml** — default model, custom providers, providers section, fallback providers
2. **OpenRouter API** — `/api/v1/models`, adds all free models (pricing.prompt + pricing.completion == $0, excluding the `openrouter/free` router meta-model)
3. **OpenCode Go** — `https://opencode.ai/zen/go/v1/models` (Bearer auth using `OPENCODE_GO_API_KEY`)
4. **OpenCode Zen** — `https://opencode.ai/zen/v1/models` (Bearer auth using `OPENCODE_ZEN_API_KEY`)
5. **Google Gemini** — `https://generativelanguage.googleapis.com/v1beta/models?key=<GOOGLE_API_KEY>` (filters to gemini models, excludes deprecated)

After sync, restart the workspace so it picks up the new models.json:

```bash
systemctl --user restart hermes-workspace
```

### Manual Sync (if script unavailable)

The sync logic in detail:

**Phase 1 — Extract from config.yaml**: Walk `config.model`, `config.custom_providers`, `config.providers.<name>.models`, and `config.fallback_providers`. Deduplicate by `provider:model_id` key.

**Phase 2 — Fetch OpenRouter free models**: Call `https://openrouter.ai/api/v1/models` with `Authorization: Bearer <OPENROUTER_API_KEY>`. Filter for `pricing.prompt + pricing.completion == 0` and exclude `openrouter/free`.

**Phase 3 — Fetch OpenCode models**: Call both Go and Zen endpoints with their respective API keys from `~/.hermes/.env`. Use Bearer auth (NOT `x-api-key`).

**Phase 4 — Fetch Google Gemini models**: Call `https://generativelanguage.googleapis.com/v1beta/models?key=<GOOGLE_API_KEY>`. Filter for `gemini` in model ID and exclude `deprecated` in display name. Strip the `models/` prefix from the name field to get the model ID.

**Phase 5 — Save**: Write the deduplicated list to `~/.hermes/models.json` as a JSON array, then restart the workspace.

### Verification

```bash
# Count models in models.json
python3 -c "
import json
with open('/root/.hermes/models.json') as f:
    models = json.load(f)
print(f'{len(models)} models across {len(set(m[\"provider\"] for m in models))} providers')
"

# Verify workspace sees them
curl -s http://127.0.0.1:3100/api/models | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Workspace sees {len(d.get(\"models\",d.get(\"data\",[])))} models')"
```

### Pitfalls

- **Python urllib 403 on OpenCode** — the sync script uses `subprocess` + `curl` instead of `urllib.request`. OpenCode APIs reject Python's default TLS/User-Agent. If hand-rolling a sync, use curl or set a browser-like User-Agent header.
- **Provider name normalization** — config.yaml may use capital-case names (`Google`, `DeepSeek`) while live APIs return lowercase (`google`, `deepseek`). The sync script normalizes to lowercase. Without this, the workspace model picker shows split providers (e.g., "Google: 7" + "google: 31" instead of "google: 38").
- **Script overwrites without backup** — the fixed script creates a `.bak.<timestamp>` backup before overwriting `models.json`. Always verify the model count didn't drop significantly after sync — a single failed phase (expired key, network error) can silently lose dozens of models.
- **OpenCode APIs use Bearer auth** — the key from `.env` must be passed as `Authorization: Bearer <key>`, NOT `x-api-key`.
- **OpenRouter free model detection** — check `pricing.prompt + pricing.completion == 0`. Skip `openrouter/free` (it's a router, not a real model).
- **Duplicate detection** — use `provider:model_id` as the dedup key. Same model ID can appear under different providers.
- **Workspace restart required** — the workspace caches models at startup. Restart the systemd service after updating models.json.
- **Config changes require re-sync** — if user runs `/model` in CLI to add/change providers, models.json does NOT auto-update. Must re-run this procedure.

## 10. Duplicate Vite Process Pitfall

**Symptom:** Workspace was working, then suddenly returns ERR_CONNECTION_REFUSED or ERR_CONNECTION_TIMED_OUT. No process appears to be listening on port 3100.

**Root Cause:** Multiple Vite dev server processes spawned on the same port (e.g., from repeated `npm run dev` calls). They conflict and neither serves properly.

**Diagnosis:**
```bash
ps aux | grep "vite.*3100" | grep -v grep
# If more than 1 process shows, that's the problem
```

**Fix:**
```bash
# Kill all Vite processes on port 3100
pkill -f "vite.*3100"
sleep 2
ss -tulpn | grep 3100
# Should show nothing

# Restart cleanly
cd /root/hermes-workspace
npm run dev -- --host 0.0.0.0 --port 3100 &
```

**Pitfall — killed yesterday, alive today**: A Vite dev server killed days ago may show up again on a DIFFERENT PID. This means a separate instance was launched manually in another session and never cleaned up — it's not the same process miraculously surviving. After killing, always verify the port is clear AND audit for resurrection vectors:

```bash
# 1. Verify port is actually clear
ss -tlnp | grep 3100 || echo "CLEAR"

# 2. Check if anything will resurrect it
systemctl list-units --type=service --state=running | grep -iE 'vite|3100'
pm2 list 2>/dev/null
crontab -l 2>/dev/null | grep -iE 'vite|3100'

# 3. Check for any remaining node/vite processes
ps aux | grep -iE 'vite|dev.*server' | grep -v grep || echo "No dev servers"
```

A dev server bound to `0.0.0.0` is also a security exposure — always prefer `127.0.0.1` unless external access is explicitly needed and firewall-gated.

## 11. Verification

```bash
# All three ports listening?
ss -tlnp | grep -E "8642|9119|3100"
# Expected: 8642 (hermes), 9119 (python3), 3100 (node)

# Gateway health
curl -s http://127.0.0.1:8642/health
# → {"status":"ok","platform":"hermes-agent"}

# Dashboard status
curl -s http://127.0.0.1:9119/api/status
# → {"version":"0.14.0",...,"gateway_running":true,...}

# Workspace serving
curl -s http://127.0.0.1:3100/ | grep -o "<title>[^<]*</title>"
# → <title>Hermes Workspace</title>

# Systemd all active?
systemctl --user is-active hermes-gateway hermes-dashboard hermes-workspace
# → active / active / active

# No gateway restart loop?
journalctl --user -u hermes-gateway --no-pager -n 10 | grep -c "Scheduled restart"
# → 0
```

## Quick Reference — File Locations

| What | Where |
|------|-------|
| Workspace repo | `/root/hermes-workspace/` |
| Workspace .env | `/root/hermes-workspace/.env` |
| Workspace systemd | `~/.config/systemd/user/hermes-workspace.service` |
| Dashboard systemd | `~/.config/systemd/user/hermes-dashboard.service` |
| Gateway systemd | `~/.config/systemd/user/hermes-gateway.service` |
| Dashboard web dist | `/usr/local/lib/hermes-agent/hermes_cli/web_dist/` |
| models.json | `~/.hermes/models.json` |
| API_SERVER_KEY | `~/.hermes/.env` (must match HERMES_API_TOKEN) |
| Model reference | `/root/hermes-model-reference.md` |
| WebUI archive (decommissioned) | `/root/workspace/webui-archive/` |
| WebUI migration summary | `/root/workspace/webui-migration-summary.md` |

## 12. WebUI Decommissioned

Hermes WebUI (`hermes-webui/server.py` on port 9119) was decommissioned 2026-06-03. The `hermes-webui` systemd service is **disabled** and **stopped**. Do not restart it.

The official Hermes dashboard (`hermes_cli dashboard` on port 9119) continues running — it is NOT the same as WebUI. Port 9119 now exclusively serves the dashboard.

All WebUI session data, attachments, and settings are archived at `/root/workspace/webui-archive/`. Migration summary at `/root/workspace/webui-migration-summary.md`.

**Skill parity note**: When WebUI was decommissioned, 18 profile-only skills (LinkedIn, Instagram scrapers, headless browser, voice/avatar stack, etc.) were copied from their profile dirs into the global `~/.hermes/skills/` directory to ensure parity. Global skills now number 189 packages. If creating new profiles, clone from default and verify that niche skills (Instagram, LinkedIn, browser automation) are present — they may not propagate automatically.

**Workspace directory**: `/root/workspace/` contains all project directories previously shared between WebUI and Workspace. Workspace reads from this path natively.

## 13. Rebrand Splash Screen Images

The workspace HTML references `claude-avatar.webp`, `claude-avatar.png`, `claude-banner.png`, and `claude-banner-light.png` from `/public/`. These are Claude-branded by default. To replace them with Hermes-branded equivalents without changing the code:

### Quick Rebrand (Pillow)

```bash
python3 ~/.hermes/skills/devops/hermes-workspace-deployment/scripts/rebrand-splash.py
systemctl --user restart hermes-workspace
```

The script:
1. Backs up existing `claude-*` files as `.bak` (if no backup exists)
2. Generates a Hermes avatar (400×400) — winged caduceus with circuit-board accents on #031A1A
3. Generates dark and light banner variants (1145×196) — "HERMES WORKSPACE" text with geometric wings
4. Copies new images to the `claude-*` filenames so no code changes are needed

### Verification

```bash
# Confirm hashes match between hermes-* source and claude-* served file
sha256sum /root/hermes-workspace/public/hermes-avatar.webp
curl -s http://127.0.0.1:3100/claude-avatar.webp | sha256sum
# Hashes must be identical

# Check all four images serve
for f in claude-avatar.png claude-avatar.webp claude-banner.png claude-banner-light.png; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:3100/$f")
  echo "$f → $code"
done
# All should return 200
```

## 14. Session Persistence Fix (sessionStorage → localStorage)

**Problem**: Workspace chat clears on tab switch because `chat-store.ts` uses `sessionStorage` (tab-scoped) instead of `localStorage` (persisted).

**Fix**: In `/root/hermes-workspace/src/stores/chat-store.ts`, replace all `sessionStorage` with `localStorage` calls. Also adjust TTLs from minutes to hours.

See `references/session-persistence.md` for the full fix including heartbeat endpoint recovery and React integration changes.

## 15. WebUI (Decommissioned — for reference only)

Hermes WebUI (`nesquena/hermes-webui`, port 8787) was decommissioned 2026-06-03 in favor of Hermes Workspace. The `hermes-webui` systemd service is **disabled and stopped**.

**Access methods that still apply to Workspace:**
- **Tailscale direct**: `http://<tailscale-ip>:3100` from any tailnet device
- **SSH tunnel**: `ssh -N -L 3100:127.0.0.1:3100 root@<vps-ip>` then browse `http://127.0.0.1:3100`
- **nginx reverse proxy**: Add server block proxying `127.0.0.1:3100`

All WebUI session data archived at `/root/workspace/webui-archive/`.

## Consolidated Skills

This skill absorbs: `hermes-workspace-session-persistence`, `hermes-webui-deployment`.

See `references/session-persistence.md` for the full sessionStorage→localStorage migration.
