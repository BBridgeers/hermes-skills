---
name: hermes-docker-migration
description: Hermes Docker migrations both directions — Docker ↔ native host, including decontainerization (Docker → host), the chown crash-loop, port-swap dance, and workspace quirks.
---

# Hermes Docker Migration (Hostinger VPS)

Use when: moving Hermes from systemd/host to Docker on a Hostinger VPS, or fixing
a Docker crash-loop caused by `chown` failures on bind mounts.

## Root Cause of Crash-Loop

Hostinger's kernel blocks `chown` inside Docker containers when files are on
host bind mounts (e.g. `- /opt/data:/opt/data`). The upstream entrypoint
(`/opt/hermes/docker/entrypoint.sh`) has this fatal line with NO fallback:

```bash
if [ -f "$HERMES_HOME/config.yaml" ]; then
    chown hermes:hermes "$HERMES_HOME/config.yaml"   # BOOM — no || fallback
    chmod 640 "$HERMES_HOME/config.yaml"
fi
```

The first `chown -R` on the volume has a `|| echo "Warning..."` fallback,
so it doesn't crash. But the config.yaml `chown` is unprotected and
`set -e` causes immediate container exit → restart → loop.

## Fix: Named Volumes, Not Bind Mounts

Docker-managed named volumes don't have the Hostinger chown restriction.
Use this pattern in docker-compose.yml:

```yaml
services:
  hermes-agent:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-agent
    restart: unless-stopped
    # Canonical entrypoint: use the IMAGE'S internal entrypoint, NOT a wrapper
    entrypoint: /usr/bin/tini -g -- /opt/hermes/docker/entrypoint.sh
    # Explicit command array — safer than inline string
    command: ["gateway", "run", "--replace"]
    env_file:
      - .env
    environment:
      - API_SERVER_KEY=${API_SERVER_KEY}
      - HERMES_DASHBOARD=1              # ← Start dashboard sidecar on :9119
    volumes:
      - hermes-data:/opt/data            # ← Named volume, NOT bind mount
      # Bind-mount host customizations so container always matches host:
      - /root/.hermes/config.yaml:/opt/data/config.yaml
      - /root/.hermes/.env:/opt/data/.env             # Host .env (49+ keys)
      - /root/.hermes/SOUL.md:/opt/data/SOUL.md       # Custom identity
      - /root/.hermes/auth.json:/opt/data/auth.json   # Credential cache
      # Bind-mount host skills so workspace sees real skills (not just 89 bundled)
      - /root/.hermes/skills:/opt/data/skills
    ports:
      - "127.0.0.1:8642:8642"          # Bind loopback (UFW handles external)
      - "127.0.0.1:9119:9119"          # Dashboard API
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost:8642/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s
    networks:
      - mc-net

volumes:
  hermes-data:
    name: hermes-data
  workspace-data:              # Sessions/auth state — survives container recreation
    name: workspace-data

networks:
  mc-net:
    external: true
    name: mission-control_mc-net
```

## Config Files — Bind-Mount, Don't Copy

The entrypoint script copies stock versions of `.env`, `SOUL.md`, and
`config.yaml` into the volume if they don't exist. **Always bind-mount** the
host versions from `/root/.hermes/` to `/opt/data/` in the compose file instead
of copying via `docker cp`. Bind-mounts stay in sync when you edit the host file
and survive container recreation.

Files to bind-mount:
```
/root/.hermes/config.yaml  → /opt/data/config.yaml
/root/.hermes/.env         → /opt/data/.env
/root/.hermes/SOUL.md      → /opt/data/SOUL.md
/root/.hermes/auth.json    → /opt/data/auth.json
/root/.hermes/skills/      → /opt/data/skills/
```

Only the base `/opt/data` directory uses a named volume (hermes-data) for
writable runtime state (sessions, logs, cron, cache).

## Workspace Service Port

hermes-workspace listens on port **3000** inside the container, not 3100.
The port mapping MUST be:

```yaml
ports:
  - "127.0.0.1:3100:3000"    # host:3100 → container:3000
```

Not `3100:3100` — that will fail silently with HTTP 000.

## Restart Commands

```bash
cd /root/hermes-docker
docker compose up -d --force-recreate     # Full recreate after config changes
# Or for lock issues:
docker run --rm -v hermes-data:/opt/data alpine rm -f /opt/data/gateway.lock
docker compose up -d
```

## Workspace Configuration

The workspace container needs explicit dashboard URLs pointing at the agent by
**Docker network name** (not localhost, which would resolve inside the workspace
container, not the agent container):

```yaml
  hermes-workspace:
    image: ghcr.io/outsourc-e/hermes-workspace:latest
    container_name: hermes-workspace
    restart: unless-stopped
    depends_on:
      hermes-agent:
        condition: service_healthy
    environment:
      HERMES_API_URL: http://hermes-agent:8642
      HERMES_DASHBOARD_URL: http://hermes-agent:9119   # Docker network name!
      HERMES_API_URL: http://hermes-agent:8642
      HERMES_DASHBOARD_URL: http://hermes-agent:9119   # Docker network name!
      HERMES_API_TOKEN: ${API_SERVER_KEY:-}
      HERMES_DASHBOARD_TOKEN: ${API_SERVER_KEY:-}
      # IMPORTANT: Do NOT set CLAUDE_DASHBOARD_TOKEN or CLAUDE_API_TOKEN!
      # Setting them PREVENTS the HTML-scrape token flow that the dashboard
      # actually uses for /api/skills and similar endpoints. The dashboard
      # returns 401 Unauthorized to Bearer tokens; only session tokens scraped
      # from the HTML page (<script>window.__HERMES_SESSION_TOKEN__=...</script>)
      # work. Without the HTML-scrape fallback, skills show "0/0" forever.
      HERMES_PASSWORD: ${HERMES_PASSWORD:-}
      COOKIE_SECURE: "0"                  # Must be "0" — empty string fails!
    volumes:
      - workspace-data:/home/workspace     # Session store needs persistence
    ports:
      - "127.0.0.1:3100:3000"           # Workspace listens on :3000 internally
    networks:
      - mc-net
```

Without `HERMES_DASHBOARD_URL` and `HERMES_DASHBOARD_TOKEN`, the workspace
falls back to **portable mode** (chat-only, no sessions/skills/config/jobs).

## Container Users

The hermes-agent image creates a `hermes` user (UID 10000, GID 10000) and the
entrypoint drops privileges from root to hermes after initial setup. All volume
files written by the container will appear as UID 10000 on the host.

```
# Inside the image:
hermes:x:10000:10000::/opt/data:/bin/sh
```

The workspace image uses UID 10010 (`workspace` user).

**Critical pitfall**: If any file in the named volume is root-owned while the
container runs as hermes, the container will crash with PermissionError and
restart-loop. Common culprits: agent.log created during a root-owned process
before the privilege drop, or `docker cp` that preserves host ownership.

**Fix**: `chown -R 10000:10000` on the affected volume paths.

## Logs Directory

The hermes-agent writes logs to `/opt/data/logs/` inside the container. This
directory MUST exist on the named volume before the container starts, or the
entrypoint's log handler will fail with PermissionError.

```bash
mkdir -p /var/lib/docker/volumes/hermes-data/_data/logs
chown -R 10000:10000 /var/lib/docker/volumes/hermes-data/_data/logs
```

Without this, every restart cycle recreates the logs dir in the ephemeral
container layer, which vanishes on the next restart — and the cycle repeats.

## Stale Lock File Cleanup

After crashes or ungraceful shutdowns, the named volume may contain lock files
owned by root that block the hermes user from restarting. Symptom:
`PermissionError: Permission denied: '/opt/data/gateway.lock'` on startup.

**Fix** — clear lock files without destroying the volume:

```bash
docker run --rm -v hermes-data:/opt/data alpine rm -f /opt/data/gateway.lock
```

Then recreate: `docker compose up -d --force-recreate`

## Upstream Image Evolution (v0.12.0+)

The upstream `nousresearch/hermes-agent` image v0.12.0 reorganized internals:
- Module `hermes_agent` → `hermes_cli` (the old `hermes_agent.cli` no longer exists)
- Internal entrypoint at `/opt/hermes/docker/entrypoint.sh` handles venv activation
  and gosu privilege drop — do NOT wrap it with a custom script
- Use `entrypoint:` + `command:` as separate compose fields, not inline

**Wrapper scripts that call `python3 -m hermes_agent.cli` will fail.** Always use
the canonical `entrypoint: /usr/bin/tini -g -- /opt/hermes/docker/entrypoint.sh`
with `command: ["gateway", "run", "--replace"]`.

## Decontainerization (Docker → Native Host)

Use when: moving Hermes from Docker containers to running natively on the VPS
host. Eliminates the "dual-brain" problem (host vs container memory/config),
bind-mount confusion, and network-mapping overhead.

If nothing else runs on the VPS besides Hermes and its auxiliaries (Honcho),
the VPS itself serves as the container — containers add unnecessary indirection.

### Pre-flight Audit

Before touching anything, map what's in named volumes vs bind mounts:

```bash
# From inside the container, ground truth on mounts:
cat /proc/1/mountinfo | grep -E '/opt|volume'

# From host, total data sizes:
du -sh /var/lib/docker/volumes/hermes-data/_data/sessions \
       /var/lib/docker/volumes/hermes-data/_data/state.db \
       /var/lib/docker/volumes/hermes-data/_data/checkpoints \
       /var/lib/docker/volumes/hermes-data/_data/logs \
       /var/lib/docker/volumes/hermes-data/_data/memories \
       /var/lib/docker/volumes/hermes-data/_data/kanban.db
```

Typical topology: the `/opt/data` base is a named volume (`hermes-data`), while
individual config files (config.yaml, .env, SOUL.md, auth.json) and the
skills/ directory are bind-mounted from `/root/.hermes/` on the host.

**Items that need merging (live in the named volume only):**
- sessions/ (885+ JSONL files, ~132MB)
- state.db (~42MB)
- checkpoints/ (~83MB)
- logs/ (~16MB)
- memories/ (~12KB)
- kanban.db (~100KB)
- cron/ (job definitions)
- cache/ (model catalog)
- plans/, pastes/ (user plans, clipboard history)
- gateway_state.json, context_length_cache.yaml

**Items already on host (no merge needed):**
- config.yaml, .env, SOUL.md, auth.json  (bind-mounted)
- skills/  (bind-mounted directory)

### Merge Procedure

```bash
# Stop containers first
docker compose -f /root/hermes-docker/docker-compose.yml down
rm -f /var/lib/docker/volumes/hermes-data/_data/gateway.lock \
      /var/lib/docker/volumes/hermes-data/_data/gateway.pid

SRC=/var/lib/docker/volumes/hermes-data/_data
DST=/root/.hermes

# Merge all volume-only data into host
cp -a "$SRC/sessions"/*    "$DST/sessions/"    2>/dev/null || mkdir -p "$DST/sessions"
cp -a "$SRC/memories"/*    "$DST/memories/"    2>/dev/null || mkdir -p "$DST/memories"
cp -a "$SRC/logs"/*        "$DST/logs/"        2>/dev/null || mkdir -p "$DST/logs"
cp -a "$SRC/checkpoints"/* "$DST/checkpoints/" 2>/dev/null || mkdir -p "$DST/checkpoints"
cp -a "$SRC/plans"/*       "$DST/plans/"       2>/dev/null || mkdir -p "$DST/plans"
cp -a "$SRC/pastes"/*      "$DST/pastes/"      2>/dev/null || mkdir -p "$DST/pastes"
cp -a "$SRC/cron"/*        "$DST/cron/"        2>/dev/null || mkdir -p "$DST/cron"
cp -a "$SRC/cache"/*       "$DST/cache/"       2>/dev/null || mkdir -p "$DST/cache"
cp -a "$SRC/state.db"                 "$DST/state.db"
cp -a "$SRC/kanban.db"                "$DST/kanban.db"
cp -a "$SRC/gateway_state.json"       "$DST/gateway_state.json"
cp -a "$SRC/context_length_cache.yaml" "$DST/context_length_cache.yaml"

# Fix ownership: container ran as uid 10000, host needs root
chown -R root:root \
    "$DST/sessions" "$DST/memories" "$DST/logs" "$DST/checkpoints" \
    "$DST/plans" "$DST/pastes" "$DST/cron" "$DST/cache" "$DST/skills" \
    "$DST/state.db" "$DST/kanban.db" "$DST/gateway_state.json"
chmod -R u+rwX "$DST/sessions" "$DST/memories" "$DST/logs" "$DST/checkpoints" "$DST/skills"
```

### Post-Merge: Native Hermes

```bash
# Install Hermes natively (safe — won't overwrite existing ~/.hermes/)
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Verify no /opt/data paths snuck into config
grep '/opt/data' /root/.hermes/config.yaml || echo "Clean"

# Test
/root/.local/bin/hermes doctor
/root/.local/bin/hermes chat -q "confirm you can read memory and sessions"
```

### Systemd Services (replaces Docker's restart policy)

**⚠ CRITICAL: Never write the gateway service file manually.** The gateway regenerates
its own unit file on every startup via `refresh_systemd_unit_if_needed()`. If you
write a manual unit file, the gateway detects it as "not current," overwrites it,
runs `systemctl daemon-reload`, and systemd cycles the service — creating a restart
loop at 5-minute intervals (RestartMaxDelaySec=300). Symptoms: `is-active` shows
"activating" forever, journal shows alternating "Started" / "SIGTERM" / "SIGKILL"
every few minutes, restart counter climbs past 7+.

**Always use the native installer for the gateway service:**

```bash
# Install the gateway service (generates correct unit file)
hermes gateway install

# Remove any stale system-level service that conflicts
sudo hermes gateway uninstall --system   # if present

# Start
hermes gateway start
```

For the **dashboard** (port 9119) — which is NOT part of the gateway process and must
run as a separate service — the `hermes dashboard` CLI has a Docker-container lookup
bug after decontainerization (exits with "No such container: hermes-agent"). Workaround:
use the Python module directly in the systemd unit:

```ini
# /root/.config/systemd/user/hermes-dashboard.service
[Unit]
Description=Hermes Dashboard - Web UI for config, models, sessions
After=network-online.target hermes-gateway.service
Wants=network-online.target hermes-gateway.service

[Service]
Type=simple
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python3 -m hermes_cli.main dashboard --port 9119 --host 127.0.0.1 --skip-build --no-open
WorkingDirectory=/usr/local/lib/hermes-agent
Environment="PATH=/usr/local/lib/hermes-agent/venv/bin:/usr/bin:/root/.local/bin"
Environment="VIRTUAL_ENV=/usr/local/lib/hermes-agent/venv"
Environment="HERMES_HOME=/root/.hermes"
Environment="HERMES_WEB_DIST=/usr/local/lib/hermes-agent/hermes_cli/web_dist"
Restart=always
RestartSec=5
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=default.target
```

The web UI must be pre-built once before the service can start:

```bash
cd /usr/local/lib/hermes-agent/web
npm install && npm run build
# Dist lands in hermes_cli/web_dist/
```

For the **workspace** (port 3100) — a separate Next.js/TanStack frontend that
communicates with the gateway (8642) and dashboard (9119):

```ini
# /root/.config/systemd/user/hermes-workspace.service
[Unit]
Description=Hermes Workspace - Web UI
After=network-online.target hermes-gateway.service hermes-dashboard.service

[Service]
Type=simple
ExecStart=/usr/bin/npx vite dev --port 3100 --host 127.0.0.1
WorkingDirectory=/root/hermes-workspace
Environment="PATH=/usr/bin:/root/.local/bin"
Environment="NODE_OPTIONS=--max-old-space-size=2048"
Environment="HERMES_API_URL=http://127.0.0.1:8642"
Environment="HERMES_API_TOKEN=<match-gateway-API_SERVER_KEY>"
Environment="HERMES_DASHBOARD_URL=http://127.0.0.1:9119"
Restart=always
RestartSec=5
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=default.target
```

Enable all three to survive reboots:

```bash
systemctl --user daemon-reload
systemctl --user enable hermes-gateway hermes-dashboard hermes-workspace
systemctl --user start hermes-gateway hermes-dashboard hermes-workspace
```

Verify with: `ss -tlnp | grep -E "8642|9119|3100"`

### What Stays Containerized

Honcho (the memory backend) runs in its own docker-compose stack and stays
containerized — it's a separate database/service, not part of Hermes core.
The native Hermes running on the host connects to Honcho at `localhost:8000`.

### Native Workspace Reinstallation (Post-Decontainerization)

The workspace container (`ghcr.io/outsourc-e/hermes-workspace`) is removed
along with the agent container. It must be reinstalled natively from the
GitHub repo. Full procedure at `references/native-workspace-install.md`.

**⚠ CRITICAL: The dashboard (port 9119) is a SEPARATE service from the gateway.**
In Docker, the dashboard ran as a sidecar inside the hermes-agent container.
After decontainerization, it must be started as its own process. Without it,
the workspace model picker, config editor, sessions, skills, and cron screens
are all dead — even though the gateway (8642) and workspace (3100) are running.
See `references/native-workspace-install.md` for the dashboard install procedure
and systemd service template.

Quick steps:
```bash
cd /root/hermes-workspace
git pull --ff-only origin main
# Configure .env — HERMES_API_TOKEN must match gateway's API_SERVER_KEY
# Also set HERMES_DASHBOARD_URL=http://127.0.0.1:9119
CI=true pnpm install
npx vite dev --port 3100 --host 127.0.0.1   # bypass pnpm scripts
```

Key pitfalls: pnpm build-script approval blocks `pnpm build`/`pnpm dev`;\nport 3000 is often taken by mission-control.\n\nExternal access after decontainerization: use Tailscale Serve for automatic\nHTTPS from any device on the tailnet (see hermes-onboard skill,\n`references/tailscale-serve.md`). No SSH tunnels needed, survives reboots.\n\n### Full Automation Script

A complete decontainerization script that handles all phases (preflight checks,
dependency install, Hermes install, container shutdown, volume merge, ownership
fix, systemd service) is available at `scripts/decontainerize.sh`. Run from the
VPS host as root after taking a VPS snapshot.

### Decontainerization Pitfalls

- **Config path check**: Some configs may have hardcoded `/opt/data/` paths.
  Check with `grep '/opt/data' /root/.hermes/config.yaml` after merge.
  Replace with `HERMES_HOME` relative paths if found.
- **Ownership schism**: Volume files are uid 10000. After copying to host,
  chown everything to root (or the user running Hermes) before starting.
  Otherwise Hermes will hit PermissionError on sessions, state.db, logs.
- **Stale lock files**: Clear `gateway.lock` and `gateway.pid` from the
  merged data before starting native Hermes, or it will refuse to start.
- **Two .env files**: The container had a separate `.env` at
  `/root/hermes-docker/.env` or bind-mounted from `/root/.hermes/.env`.
  After decontainerization, `/root/.hermes/.env` is the sole source.
  Verify it has all keys (DeepSeek, OpenRouter, Ollama, Groq, Telegram, etc.)
- **Auxiliary services still need ports**: If Honcho or other services ran
  in Docker, they stay containerized. Ensure the native Hermes config
  points to `localhost` (not Docker network names like `honcho-api`).
- **Systemd lingering**: If the previous systemd service was user-scoped
  (`~/.config/systemd/user/`), the new service is system-scoped. Enable
  linger if needed: `loginctl enable-linger root`.
- **`hermes dashboard` CLI fails with Docker error**: After decontainerization,
  running `hermes dashboard --port 9119` exits immediately with
  "Error response from daemon: No such container: hermes-agent". The CLI
  wrapper triggers a Docker lookup during startup. Workaround: use the Python
  module directly — `python3 -m hermes_cli.main dashboard --port 9119 --host 127.0.0.1 --skip-build --no-open`
  with `HERMES_WEB_DIST` set to the pre-built web dist path. The systemd
  service template in `references/native-workspace-install.md` uses this pattern.
- **Dashboard is a separate service from gateway**: The dashboard on port 9119
  is NOT included in the gateway process. It must be started independently.
  The workspace needs BOTH — gateway (8642) for chat and dashboard (9119) for
  models/config/sessions/skills/cron. Without the dashboard, the workspace
  model picker shows only "hermes-agent" and config/sessions screens are dead.
- **SOUL.md still references Docker topology**: After decontainerization,
  SOUL.md's Infrastructure section still describes Docker containers, bind
  mounts, and `/opt/data/` paths. Update it to reflect the native deployment
  (bare-metal, `~/.hermes/` paths, systemd services).

## Pitfalls

- **Workspace container can stop independently**: The workspace container
  (`hermes-workspace`) stops on its own — the agent and dashboard stay up but
  port 3100 returns connection refused. Symptom: workspace UI shows empty config,
  "Not configured" for all API keys, or won't load. This is NOT an auth problem.
  Restart: `cd /root/hermes-docker && docker compose up -d hermes-workspace`.
  Verify: `curl -o /dev/null -w '%{http_code}' http://127.0.0.1:3100/` should return 200.
- **Dashboard auth is session-token based, NOT Bearer token**: The dashboard
  generates a per-session token embedded in its HTML page
  (`<script>window.__HERMES_SESSION_TOKEN__="..."</script>`). The workspace
  scrapes this token at startup and uses it for `/api/skills` and similar
  endpoints. Setting `CLAUDE_DASHBOARD_TOKEN` or `CLAUDE_API_TOKEN` causes the
  workspace to skip the HTML-scrape flow and use the env var as a Bearer token —
  which the dashboard REJECTS with 401. **Never set CLAUDE_* vars** — they
  actually break dashboard auth by preventing the working fallback.
- **\\\"0/0 skills\\\" in workspace**: The container ships with only ~89 bundled skills,
  but the host may have many more (e.g., 190+). Without a bind mount from
  `/root/.hermes/skills` to `/opt/data/skills`, the dashboard API returns the
  bundled subset and the workspace UI shows \\\"0/0\\\" or a much lower count.
  Always bind-mount the host skills directory.
- **COOKIE_SECURE must be `\\\"0\\\"` not `\\\"\\\"`**: NODE_ENV=production in the workspace
  image enables the `Secure` flag on session cookies. Setting `COOKIE_SECURE: \\\"\\\"`
  does NOT disable it — browsers silently drop Secure cookies over `http://`,
  and login silently fails. Use `COOKIE_SECURE: \\\"0\\\"` explicitly.
- **`workspace-data` volume needs manual chown**: The named volume is created
  as root:root. The workspace runs as user `workspace` (uid 10010) and cannot
  write session files. After first creation, run:
  ```bash
  docker exec -u root hermes-workspace sh -c '
    mkdir -p /home/workspace/.hermes
    chown -R workspace:workspace /home/workspace
  '
  ```
  Without this, `[auth] Failed to persist session store` errors fill the logs
  and login/session state silently fails.
- **Host config files must be bind-mounted, not copied**: The entrypoint
  script copies STOCK versions of `.env`, `SOUL.md`, and `config.yaml` into
  the named volume if they don't exist. Bind-mount the host versions to
  `/opt/data/` so the container always uses the customized versions. Without
  this, `.env` has 36 keys instead of 49, `SOUL.md` is a 536-byte default
  template instead of the 3.6KB custom identity, and `auth.json` has fewer
  cached credentials.
- **Entrypoint-wrapper trap**: Custom wrapper scripts that redirect to the
  internal entrypoint (e.g., `/opt/data/entrypoint-wrapper.sh`) are brittle.
  The upstream entrypoint already handles chown, venv activation, gosu drop,
  and skill sync. Just call it directly.
- **`workspace-data` volume is required for login**: The workspace writes session
  state to `/home/workspace/.hermes/workspace-sessions.json`. Without a volume,
  that directory doesn't exist, causing `Failed to persist session store` errors.
  Always include a named volume mapped to `/home/workspace`.
- The upstream image starts in **TUI mode** if no `command:` is set.
  Always include `command: [\"gateway\", \"run\", \"--replace\"]` as an array.
- `docker compose up -d` gets flagged as a \"server command\" by some tool
  frameworks. Run it in background mode or via a script.
- The `.env` file at `/root/.hermes/.env` has all API keys; copy it to
  the docker-compose directory (Docker doesn't follow symlinks well for
  env_file context).
- **Skills permission schism**: When skills are created/patched by root on the
  host (via `skill_manage` from a different process, or by direct file edits),
  the resulting SKILL.md files are root:root with mode 0600. The container runs
  as user `hermes` (uid 10000), so those files return Permission denied on every
  session start. Fix: `chown -R 10000:10000 /root/.hermes/skills && chmod -R u+rwX /root/.hermes/skills`.
  Verify with: `find /root/.hermes/skills -name SKILL.md -not -user 10000 | wc -l` (should be 0).
  This is a recurring problem — any skill creation done outside the container
  (e.g., via `hermes curator pull` on host) resets ownership.
- Mission Control (port 3000) is already Docker on `mc-net`. Add hermes
  services to the same network so they can talk by container name.
- Named volume survives container recreation but NOT `docker compose down -v`.
  Use `docker compose down` (no -v) to preserve data.
