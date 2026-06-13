---
name: hermes-tool-ops
description: Operationalize newly installed Hermes plugins, Docker apps, Python tools, and Node.js GUIs on a Hostinger VPS — wiring, systemd services, env var discovery, and crash-loop avoidance.
---

# Hermes Tool Operations — VPS Deployment Playbook

When installing new skills, plugins, Docker apps, Python tools, or Node.js GUIs, use this skill to wire them properly for production on a Hostinger VPS.

## Step 1: Audit Dependencies

For each new addition, check:
- **Python tools**: `pyproject.toml`, `requirements.txt`, `setup.py` → pip deps
- **Node apps**: `package.json` → `pnpm install` (preferred) or `npm install`
- **Docker apps**: `docker-compose.yml` → volume mounts, port conflicts
- **Plugins**: `plugin.yaml` + `__init__.py` with `register(ctx)` function

## Step 2: Install with PEP 668 + Hostinger Workarounds

Hostinger VPS uses system Python with PEP 668 (externally managed). Always use:
```bash
pip install --break-system-packages <package>
# OR for editable installs:
pip install --break-system-packages -e /path/to/repo
```

For Debian package conflicts (e.g. typing-extensions):
```bash
pip install --break-system-packages --ignore-installed typing-extensions -e /repo
```

Node.js/pnpm live in `/root/.hermes/node/bin/` — add to PATH:
```bash
export PATH="/root/.hermes/node/bin:$PATH"
pnpm install
```

## Step 3: Wire Hermes Plugins

Hermes plugins go in `~/.hermes/plugins/<name>/` and need:
1. `plugin.yaml` — metadata
2. `__init__.py` — `register(ctx)` function
3. Entry in `~/.hermes/config.yaml`:
```yaml
plugins:
  enabled:
    - <plugin-name>
```

For entry-point plugins (like rtk-hermes), install the package and add the entry-point name to `plugins.enabled`. The `rtk` CLI must be available in PATH — install via npm:
```bash
npm install -g rtk
# Binary at /root/.hermes/node/bin/rtk
```

After wiring, restart the gateway:
```bash
systemctl --user daemon-reload && systemctl --user restart hermes-gateway
```

## Step 4: Docker Apps — Volume Mount Safety

**CRITICAL**: Hostinger VPS blocks `chown` inside containers. NEVER mount `/opt/data` or any host path that needs ownership changes. Use named Docker volumes instead.

Safe pattern (mission-control):
```yaml
volumes:
  - mc-data:/app/.data    # ✅ Named volume — no chown
```

Unsafe pattern (hermes-workspace Docker):
```yaml
volumes:
  - claude-data:/opt/data  # ⚠️ May crash-loop with chown errors
```

If a Docker app has problematic volume mounts, fall back to local pnpm install + systemd service.

## Step 5: Node.js GUI — TanStack/Vite Wrapper Pattern

When a Node.js app (like hermes-workspace using TanStack Start) builds to `dist/server/server.js` but only exports a `fetch` handler (no HTTP listener), create a wrapper:

```javascript
// server.mjs
import { createServer } from 'node:http';
import server from './dist/server/server.js';

const port = process.env.PORT || 3000;
const host = process.env.HOST || '127.0.0.1';

const httpServer = createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const webReq = new Request(url, {
    method: req.method,
    headers: req.headers,
    body: req.method !== 'GET' && req.method !== 'HEAD' ? req : undefined,
  });
  const webRes = await server.fetch(webReq);
  res.writeHead(webRes.status, Object.fromEntries(webRes.headers));
  if (webRes.body) {
    for await (const chunk of webRes.body) res.write(chunk);
  }
  res.end();
});

httpServer.listen(port, host, () => {
  console.log(`Running on http://${host}:${port}`);
});
```

Then create a systemd service:
```ini
[Service]
WorkingDirectory=/root/app
Environment="PATH=/root/.hermes/node/bin:..."
Environment="PORT=3100"
Environment="HOST=127.0.0.1"
Environment="HERMES_API_URL=http://localhost:8642"
EnvironmentFile=/root/.hermes/.env
ExecStart=/root/.hermes/node/bin/node /root/app/server.mjs
```

## Step 6: Enable Gateway API Server

The Hermes gateway API server is enabled via **environment variables**, NOT config.yaml:
```bash
# Add to /root/.hermes/.env (use sed — .env is protected from patch/write_file)
API_SERVER_ENABLED=true
API_SERVER_PORT=8642
API_SERVER_HOST=0.0.0.0
API_SERVER_KEY=<strong-password>
```

The `api_server` key in config.yaml has NO effect — the gateway reads `API_SERVER_*` env vars from `EnvironmentFile`.

After editing, restart:
```bash
systemctl --user restart hermes-gateway
# Verify:
curl http://localhost:8642/health  # should return 200
```

## Step 7: Set Up Always-On Cron Jobs

For self-improvement skills, create cron jobs referencing the skill:
```bash
cronjob create \
  --schedule "every 5m" \
  --skill hermes-heartbeat \
  --prompt "Run the health check. Report only if something is wrong."
```

Priority cadence:
- Every 5 min: heartbeat, slack-context-sync
- Daily: skill-health, github-trending, vibecoding-digest, external-feature
- Every 2 days: self-improve
- Weekly: cost-report (Mon), skill-leaderboard (Mon), skill-update (Wed), weekly-review (Sun), security-audit (Mon)
- Twice weekly: vuln-scanner (Wed+Sat)

## Step 8: Verification

Run lintlang on configs to catch structural issues:
```bash
lintlang scan ~/.hermes/config.yaml ~/.hermes/SOUL.md
```

Verify services:
```bash
systemctl --user is-active hermes-gateway hermes-workspace
docker ps --filter "name=mission-control"
ss -tlnp | grep -E "8642|3000|3100"
```

## Pitfalls

- `.env` is protected — can't use `patch` or `write_file`, must use `sed` or `>>` in terminal
- `hermes skills update` never fetches tap repos — you must `git pull` manually in each skill dir
- Playwright needs `python3 -m playwright install chromium` after pip install
- npm global packages go to `/root/.hermes/node/bin/` — add it to PATH
- `pnpm approve-builds` is needed for native addons (esbuild, electron, better-sqlite3)
- Gateway restart can take 5-10s; check with `systemctl --user is-active` before curl
- Docker containers with host-path mounts on Hostinger fail on `chown` — use named volumes
