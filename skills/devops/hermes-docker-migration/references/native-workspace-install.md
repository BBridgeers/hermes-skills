# Native Hermes Workspace Installation

After decontainerizing Hermes Agent, the workspace container
(`ghcr.io/outsourc-e/hermes-workspace`) is gone. The workspace must be
reinstalled natively from the GitHub repo.

## Prerequisites

- Node 22+, pnpm, git
- Hermes Agent gateway running natively with API server enabled
- `API_SERVER_KEY` set in `~/.hermes/.env`

## Install Steps

```bash
cd /root
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace
git pull --ff-only origin main
```

## .env Configuration

```bash
# Must match gateway's API_SERVER_KEY for the workspace→gateway bridge
HERMES_API_URL=http://127.0.0.1:8642
HERMES_API_TOKEN=<same-as-API_SERVER_KEY>
HERMES_PASSWORD=<strong-password>
PORT=3100        # 3000 is often taken by mission-control
HOST=127.0.0.1   # loopback-only; switch to 0.0.0.0 for remote access
```

Without `HERMES_API_TOKEN` matching the gateway's `API_SERVER_KEY`, all
workspace↔gateway API calls return 401.

## Port Conflict

Port 3000 is frequently occupied by mission-control or other Docker services.
Always check before launching:

```bash
ss -tlnp | grep 3000
```

Set `PORT=3100` in `.env` if 3000 is taken.

## Build: pnpm Pitfall

`pnpm build` and `pnpm dev` both run `pnpm install` as a pre-step. If any
dependency has unapproved build scripts (typically `esbuild`, `unrs-resolver`),
pnpm exits with error 1 — even when all packages are already installed.

Attempted fixes that DO NOT WORK:
- `.npmrc` `onlyBuiltDependencies[]=esbuild` — ignored by pnpm
- `package.json` `pnpm.onlyBuiltDependencies` — ignored by pnpm
- `pnpm rebuild esbuild unrs-resolver` — succeeds but doesn't clear the approval gate
- `pnpm approve-builds` — interactive, requires PTY

**What works: bypass pnpm scripts entirely.** Use npx to call vite directly:

```bash
cd /root/hermes-workspace
CI=true pnpm install          # install deps (CI=true skips TTY check)
npx vite build                # build (NOT pnpm build)
npx vite dev --port 3100 --host 127.0.0.1   # dev server (NOT pnpm dev)
```

The build outputs to `dist/server/server.js` (~136KB). Build time is ~10s.

## Verify

```bash
# Workspace serving HTML?
curl -s --max-time 30 http://127.0.0.1:3100 | head -5

# Gateway health via workspace API bridge?
curl -s http://127.0.0.1:8642/health
# → {"status":"ok","platform":"hermes-agent"}

# Login test (should return 200 with full SPA HTML)
curl -v -X POST http://127.0.0.1:3100/api/login \
  -H "Content-Type: application/json" \
  -d '{"password":"<HERMES_PASSWORD>"}'
```

## Remote Access

Workspace defaults to `HOST=127.0.0.1`. For remote browser access:

**Option A — SSH tunnel (no config change):**
```bash
ssh -L 3100:127.0.0.1:3100 root@VPS_IP_REDACTED
# Then open http://localhost:3100
```

**Option B — Bind to 0.0.0.0 (use with password):**
Set `HOST=0.0.0.0` in `.env` and restart. The server refuses to start on
0.0.0.0 without `HERMES_PASSWORD` set.

**Option C — Traefik reverse proxy:**
Add a router for port 3100 in the existing Traefik config.


## Dashboard (Port 9119) — Mandatory for Full Workspace Functionality

The workspace is NOT self-contained. It requires a **second backend service** —
the Hermes Dashboard — running on port 9119. This is what provides:

| Feature | Without Dashboard | With Dashboard |
|---|---|---|
| Model picker dropdown | Only shows "hermes-agent" | Full model list from config |
| Config editor | Dead (401s / empty) | Reads/writes config.yaml |
| Sessions list | Empty / error | Full session history |
| Skills browser | "0/0" or errors | Full skills catalog |
| Cron jobs UI | Error | Full management |
| `/api/status` in workspace | Partial | Version, gateway state, platforms |

**The dashboard was the missing piece in Docker deployments too** — the
container had both gateway (8642) and dashboard (9119), but if the dashboard
sidecar failed or was misconfigured, the workspace appeared "broken" with
empty config and missing models.

### Dashboard Install & Startup (Native)

```bash
# 1. Build the web UI frontend (one-time)
cd /usr/local/lib/hermes-agent/web
npm install && npm run build
# Output: hermes_cli/web_dist/index.html + assets/

# 2. Start the dashboard (MUST use python3 -m, NOT the hermes CLI)
#    The `hermes dashboard` CLI has a Docker container lookup bug that
#    fails with "Error response from daemon: No such container: hermes-agent"
HERMES_WEB_DIST=/usr/local/lib/hermes-agent/hermes_cli/web_dist \
  python3 -m hermes_cli.main dashboard --port 9119 --host 127.0.0.1 --skip-build --no-open

# 3. Verify
curl -s http://127.0.0.1:9119/api/status
# → {"version":"0.14.0","gateway_running":true,"gateway_platforms":{...}}
```

### Systemd Service (Survives Reboots)

```ini
# ~/.config/systemd/user/hermes-dashboard.service
[Unit]
Description=Hermes Dashboard - Web UI for config, models, sessions
After=network-online.target hermes-gateway.service
Wants=network-online.target hermes-gateway.service

[Service]
Type=simple
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python3 -m hermes_cli.main dashboard --port 9119 --host 127.0.0.1 --skip-build --no-open
WorkingDirectory=/usr/local/lib/hermes-agent
Environment="HERMES_HOME=/root/.hermes"
Environment="HERMES_WEB_DIST=/usr/local/lib/hermes-agent/hermes_cli/web_dist"
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now hermes-dashboard
```

### The THREE-Service Architecture

A fully functional native Hermes stack requires all three:

| Service | Port | Provides | Systemd Unit |
|---|---|---|---|
| Gateway | 8642 | Core agent, chat, tool execution | `hermes-gateway` |
| Dashboard | 9119 | Config, models, sessions, skills, cron | `hermes-dashboard` |
| Workspace | 3100 | Web UI (browser frontend) | `hermes-workspace` |

The workspace `.env` must point at both:
```
HERMES_API_URL=http://127.0.0.1:8642
HERMES_DASHBOARD_URL=http://127.0.0.1:9119
```

**Pitfall**: If only the gateway and workspace are running (no dashboard), the
workspace UI loads but models, config, sessions, skills, and cron screens are
all dead — exactly the symptoms users reported in Docker deployments.
