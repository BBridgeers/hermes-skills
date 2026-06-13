# Hermes Workspace Native Installation

Complete native (bare-metal) deployment of Hermes Workspace + Dashboard on a VPS alongside the gateway.

## Prerequisites

- Hermes Agent gateway running on port 8642
- Node 22+, pnpm, git
- API_SERVER_ENABLED=true and API_SERVER_KEY set in ~/.hermes/.env

## Install Workspace

```bash
cd ~
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace

# .env — critical: HERMES_API_TOKEN must match gateway's API_SERVER_KEY
cat > .env << 'EOF'
HERMES_API_URL=http://127.0.0.1:8642
HERMES_API_TOKEN=HERMES_API_KEY_REDACTED
HERMES_PASSWORD=HERMES_WORKSPACE_PASSWORD_REDACTED
PORT=3100
HOST=127.0.0.1
EOF

# Install deps + build
CI=true pnpm install
NODE_OPTIONS="--max-old-space-size=2048" npx vite build
```

## Install Dashboard

The dashboard CLI (`hermes dashboard`) may fail with Docker container errors on native installs. Workaround:

```bash
# Build web UI
cd /usr/local/lib/hermes-agent/web
npm install && npm run build

# Start via Python module directly
HERMES_WEB_DIST=/usr/local/lib/hermes-agent/hermes_cli/web_dist \
  python3 -m hermes_cli.main dashboard --port 9119 --host 127.0.0.1 --skip-build --no-open
```

## Systemd Services

### Dashboard
```
# ~/.config/systemd/user/hermes-dashboard.service
[Unit]
Description=Hermes Dashboard
After=network-online.target hermes-gateway.service
[Service]
Type=simple
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python3 -m hermes_cli.main dashboard --port 9119 --host 127.0.0.1 --skip-build --no-open
Environment=HERMES_WEB_DIST=/usr/local/lib/hermes-agent/hermes_cli/web_dist
Environment=HERMES_HOME=/root/.hermes
Restart=always
RestartSec=5
[Install]
WantedBy=default.target
```

### Workspace
```
# ~/.config/systemd/user/hermes-workspace.service
[Unit]
Description=Hermes Workspace
After=hermes-gateway.service hermes-dashboard.service
[Service]
Type=simple
ExecStart=/usr/bin/npx vite dev --port 3100 --host 127.0.0.1
WorkingDirectory=/root/hermes-workspace
Environment=NODE_OPTIONS=--max-old-space-size=2048
Environment=HERMES_API_URL=http://127.0.0.1:8642
Environment=HERMES_API_TOKEN=HERMES_API_KEY_REDACTED
Environment=HERMES_DASHBOARD_URL=http://127.0.0.1:9119
Restart=always
RestartSec=5
[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable hermes-dashboard hermes-workspace
systemctl --user start hermes-dashboard hermes-workspace
```

## Gateway Pitfall

NEVER write the gateway systemd unit manually. The gateway regenerates its service file on startup. Hand-written files cause a restart loop. Always use:
```bash
hermes gateway install
hermes gateway start
```

## Model Sync

Workspace reads models from `~/.hermes/models.json` (NOT config.yaml). If missing, only the gateway default model appears in dropdowns. Format: `[{"model": "...", "provider": "..."}]`.
