# Native (Bare-Metal) Deployment (Blake's VPS)

As of May 2026, Hermes runs natively on the Hostinger VPS — decontainerized. No Docker overhead, no bind mounts, no port forwarding.

## Key Paths

| Path | Contents |
|---|---|
| `/usr/local/lib/hermes-agent/` | Git checkout + venv |
| `/root/.hermes/config.yaml` | Sole config source |
| `/root/.hermes/.env` | API keys and secrets |
| `/root/.hermes/skills/` | Skill library |
| `/root/.hermes/sessions/` | Session transcripts |
| `/root/.hermes/logs/` | Gateway and error logs |
| `/root/.hermes/SOUL.md` | Agent identity |
| `/root/.hermes/models.json` | Model list for workspace (synced from config.yaml) |

## Services (systemd user)

| Service | Port | Command |
|---|---|---|
| `hermes-gateway` | 0.0.0.0:8642 | `hermes gateway install` (auto-generated unit) |
| `hermes-dashboard` | 127.0.0.1:9119 | `python3 -m hermes_cli.main dashboard --port 9119 --host 127.0.0.1 --skip-build --no-open` |
| `hermes-workspace` | 127.0.0.1:3100 | `npx vite dev --port 3100 --host 127.0.0.1` in `/root/hermes-workspace` |

## Critical Pitfalls

### Do NOT hand-write the gateway systemd unit
The gateway regenerates its own unit file on every startup via `refresh_systemd_unit_if_needed()`. A hand-written unit that doesn't match the generated one causes a restart doom loop. **Always use `hermes gateway install`** to create the service file.

### `hermes dashboard` may fail on native installs
The `hermes dashboard` CLI may fail with Docker container errors on bare-metal installs. Workaround: call the Python module directly:
```bash
HERMES_WEB_DIST=/usr/local/lib/hermes-agent/hermes_cli/web_dist \
  python3 -m hermes_cli.main dashboard --port 9119 --host 127.0.0.1 --skip-build --no-open
```
The web UI must be pre-built: `cd /usr/local/lib/hermes-agent/web && npm install && npm run build`

### Heartbeat cron jobs may reference old Docker containers
After decontainerization, existing cron jobs (especially hermes-heartbeat) may still try `docker exec hermes-agent ...`. Check with `hermes cron list` and update any jobs that reference Docker.

### models.json sync for workspace
The workspace reads available models from `~/.hermes/models.json`, but the CLI stores models in `config.yaml`. After any model changes via `/model`, re-sync:
```python
# Extract models from config.yaml custom_providers + fallback_providers + providers
# Write to ~/.hermes/models.json as [{"model": "...", "provider": "..."}, ...]
```
The workspace API then serves these via `/api/models`.

## Co-Tenants (Docker, same host)

| Project | Containers | Notes |
|---|---|---|
| `honcho` | honcho-api, honcho-database, honcho-deriver, honcho-redis | Memory backend |
| `traefik` | traefik-traefik-1 | Reverse proxy |
| `wireguard` | wireguard | VPN |
| `mission-control` | mission-control | Monitoring |

## Tailscale Remote Access

```bash
# Install
curl -fsSL https://tailscale.com/install.sh | sh
# Authenticate
tailscale up
# Enable serve (one-time tailnet setting at the printed URL)
tailscale serve --bg --https=443 http://127.0.0.1:3100
tailscale serve --bg --https=8443 http://127.0.0.1:9119
```
Workspace then available at `https://<hostname>.<tailnet>.ts.net`. Does not conflict with existing WireGuard Docker container (different ports, different interfaces).
