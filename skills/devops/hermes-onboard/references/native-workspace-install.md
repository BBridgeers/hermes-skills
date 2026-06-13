# Native Hermes Workspace Install

Full procedure for deploying Hermes Workspace natively (bare-metal) on a VPS alongside a native hermes-agent gateway.

## Prerequisites

- Hermes Agent gateway running natively on port 8642 (systemd service)
- Node.js 22+, pnpm, git
- Gateway `.env` must have `API_SERVER_ENABLED=true` and `API_SERVER_KEY` set

## Step 1 — Clone & Pull Latest

```bash
cd ~
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace
git pull --ff-only origin main
```

## Step 2 — Build Dashboard Web UI (required for workspace)

The dashboard serves its own web UI from a pre-built dist. Build it first:

```bash
cd /usr/local/lib/hermes-agent/web
npm install
npm run build
# Dist lands at: /usr/local/lib/hermes-agent/hermes_cli/web_dist/
```

## Step 3 — Configure Workspace .env

```bash
cd ~/hermes-workspace
cat > .env << 'EOF'
HERMES_API_URL=http://127.0.0.1:8642
HERMES_API_TOKEN=<same as API_SERVER_KEY in ~/.hermes/.env>
HERMES_PASSWORD=<strong-password-for-workspace-ui>
PORT=3100
HOST=127.0.0.1
EOF
```

Important: `HERMES_API_TOKEN` MUST match the gateway's `API_SERVER_KEY`. Without it, all workspace↔gateway API calls return 401.

Port 3100 avoids conflict with mission-control on port 3000.

## Step 4 — Install Workspace Dependencies

```bash
cd ~/hermes-workspace
CI=true pnpm install
```

If pnpm blocks on build script approval (esbuild, unrs-resolver), work around it:

```bash
# Option A: approve builds interactively
pnpm approve-builds  # select esbuild + unrs-resolver

# Option B: skip pnpm scripts entirely and use vite directly
npx vite build   # for production build
npx vite dev --port 3100 --host 127.0.0.1   # for dev server
```

## Step 5 — Start the Dashboard

The dashboard (port 9119) is REQUIRED for workspace features. Without it, the model picker, config editor, sessions list, skills browser, and cron UI are all disabled.

**The `hermes dashboard` CLI command may fail with "No such container: hermes-agent" in native deployments.** Workaround:

```bash
cd /usr/local/lib/hermes-agent
source venv/bin/activate
HERMES_WEB_DIST=/usr/local/lib/hermes-agent/hermes_cli/web_dist \
  python3 -m hermes_cli.main dashboard \
  --port 9119 --host 127.0.0.1 --skip-build --no-open
```

This must run as a persistent background process. For production, wrap in a systemd service.

## Step 6 — Start the Workspace

```bash
cd ~/hermes-workspace
NODE_OPTIONS="--max-old-space-size=2048" npx vite dev --port 3100 --host 127.0.0.1
```

For production (after `npx vite build`):

```bash
NODE_OPTIONS="--max-old-space-size=2048" node dist/server/server.js
```

## Step 7 — Sync models.json (workspace model picker)

The workspace model picker reads `~/.hermes/models.json`, NOT config.yaml directly.
If this file doesn't exist, only the default model shows in dropdowns.

```bash
# Run the sync script from hermes-workspace-models-config-fix skill
python3 ~/.hermes/skills/devops/hermes-workspace-models-config-fix/scripts/sync-models-json.py

# Or manually: extract from config.yaml and write models.json
```

After syncing, restart the workspace so it picks up the new file:
```bash
systemctl --user restart hermes-workspace
```

**models.json does NOT auto-sync.** When models are added/changed via `/model` in CLI, re-sync is needed.

## Pitfalls

### File Browser Workspace Selector

The workspace Files tab does NOT default to `/root/`. It uses a workspace selector dropdown at the top of the Files panel. The user must manually select `/root` (or another directory) as the active workspace. Files placed at `/root/MODEL-REFERENCE.md` will only appear after selecting `/root` as the workspace root.

### Gateway Service — Do Not Write Manually

Never write `~/.config/systemd/user/hermes-gateway.service` by hand. The gateway self-manages its service file and will overwrite it on startup, triggering a SIGTERM/SIGKILL restart loop. Always use `hermes gateway install`.

### Dashboard CLI on Native Deployments

`hermes dashboard` may fail with "No such container: hermes-agent" on native deployments. Use the Python module invocation with `HERMES_WEB_DIST` set and `--skip-build`.

### pnpm Build Script Approval

`pnpm build` and `pnpm dev` re-run `pnpm install` as a pre-step, which fails when build scripts (esbuild, unrs-resolver) aren't approved. Workaround: skip pnpm scripts entirely and use `npx vite build` / `npx vite dev` directly.

```bash
# All three ports should be listening
ss -tlnp | grep -E "8642|9119|3100"

# Dashboard serves HTML
curl -s http://127.0.0.1:9119/ | head -3

# Workspace serves HTML (first request slow due to Vite lazy compilation)
curl -s --max-time 30 http://127.0.0.1:3100/ | head -5

# Gateway health
curl -s http://127.0.0.1:8642/health
```

## Step 9 — Systemd Services (survive reboots)

Copy the templates from this skill's `templates/` directory and enable:

```bash
cp templates/hermes-dashboard.service ~/.config/systemd/user/
cp templates/hermes-workspace.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable hermes-dashboard hermes-workspace
systemctl --user start hermes-dashboard hermes-workspace
```

⚠ **CRITICAL: Never write the gateway systemd unit file manually.** The gateway
self-manages its service definition. On startup it detects mismatches, overwrites
the file, and runs `systemctl daemon-reload` — which triggers SIGTERM/SIGKILL and
a restart loop (5-minute cycle). Always use:

```bash
hermes gateway install     # generates correct service file
hermes gateway start       # starts clean
```

Verify all three are running:
```bash
systemctl --user status hermes-gateway hermes-dashboard hermes-workspace
```

## External Access

### Option A — Tailscale Serve (recommended)

Install Tailscale on the VPS, authenticate to your tailnet, and use `tailscale serve` for automatic HTTPS access from any Tailscale-connected device:

```bash
# Install
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up  # follow auth link

# Enable Serve on tailnet (one-time admin action at the link shown)
tailscale serve --bg --https=443 http://127.0.0.1:3100

# Dashboard on separate port
tailscale serve --bg --https=8443 http://127.0.0.1:9119
```

Then access from any device on the tailnet:
- Workspace: `https://<vps-name>.<tailnet>.ts.net`
- Dashboard: `https://<vps-name>.<tailnet>.ts.net:8443`

No SSH tunnels needed. Tailscale handles TLS certificates automatically. Works on mobile (iOS/Android Tailscale app → browser).

**Does NOT conflict with existing WireGuard VPNs** when WireGuard runs in Docker bridge mode (different ports, different interfaces). Tailscale uses `tailscale0` interface and random high UDP ports.

### Option B — SSH Tunnel

```bash
ssh -L 3100:127.0.0.1:3100 -L 9119:127.0.0.1:9119 root@<vps-ip>
```

Then open `http://localhost:3100` in browser. Enter the workspace password from `.env`.

### Option C — Bind to 0.0.0.0 (insecure, use with password)

## Architecture Note

The workspace is a "zero-fork" architecture — it uses TWO backend services:

| Service | Port | Provides |
|---|---|---|
| Gateway | 8642 | Core agent, chat/completions, /health |
| Dashboard | 9119 | Models, config, sessions, skills, cron, env vars, settings |

The workspace probes both on startup. If the dashboard is unreachable, enhanced features (model picker, config, sessions, skills, cron, conductor, kanban) are silently disabled. Only basic chat remains functional.
