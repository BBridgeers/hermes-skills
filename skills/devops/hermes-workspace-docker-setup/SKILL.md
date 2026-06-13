---
name: hermes-workspace-docker-setup
description: Complete Docker Compose setup for hermes-agent + hermes-workspace — covers entrypoint quirks, dashboard auth (HTML-scrape token flow), skills bind-mounting, lock file cleanup, and debugging "0 skills" / login failures.
triggers:
  - hermes workspace not showing skills
  - workspace shows 0/0 skills
  - workspace can't login / password not working
  - hermes-agent crash-looping in Docker
  - docker compose setup for hermes-agent + workspace
  - dashboard /api/skills returns 401
  - CLAUDE_DASHBOARD_TOKEN
---

# Hermes Workspace Docker Setup

End-to-end Docker Compose config for hermes-agent + hermes-workspace on a VPS, with all known quirks documented.

## Docker Compose Architecture

Two services on a shared Docker network (`mc-net`):
- **hermes-agent** — `nousresearch/hermes-agent:latest`, ports 8642 (gateway) + 9119 (dashboard)
- **hermes-workspace** — `ghcr.io/outsourc-e/hermes-workspace:latest`, port 3000 (mapped to host)

## 1. Agent Service — Critical Entrypoint/Command Pattern

The hermes-agent Docker image has a specific entrypoint contract. You MUST use the internal entrypoint script directly — wrapper scripts that call it indirectly cause `ModuleNotFoundError: No module named 'hermes_agent'`.

**Correct:**
```yaml
hermes-agent:
  image: nousresearch/hermes-agent:latest
  entrypoint: /usr/bin/tini -g -- /opt/hermes/docker/entrypoint.sh
  command: ["gateway", "run", "--replace"]
```

**Wrong (causes crash-loop):**
```yaml
  entrypoint: /usr/bin/tini -g -- /opt/data/entrypoint-wrapper.sh
  # "python3 -m hermes_agent.cli" doesn't exist in the image
```

The internal entrypoint handles: gosu privilege drop, venv activation, config bootstrap, skills sync, and dashboard side-process launch.

## 2. Dashboard — Must Be Explicitly Enabled

Add to agent environment:
```yaml
environment:
  - HERMES_DASHBOARD=1
```

Without this, the dashboard doesn't start and the workspace falls back to "portable" mode (no sessions, skills, config, memory, jobs).

## 3. Ports — Bind to localhost for Security

```yaml
ports:
  - "127.0.0.1:8642:8642"
  - "127.0.0.1:9119:9119"
```

UFW handles external access. Binding to 127.0.0.1 prevents exposure if UFW is ever down.

## 4. Volumes — Skills Must Be Bind-Mounted

The image ships only ~89 bundled skills. Your real skills (190+) live on the host at `/root/.hermes/skills/`. Bind-mount them:

```yaml
volumes:
  - hermes-data:/opt/data
  - /root/.hermes/config.yaml:/opt/data/config.yaml
  - /root/.hermes/skills:/opt/data/skills    # ← CRITICAL for skills
```

If skills are missing, the workspace shows "0/0 skills" even though the API is detected.

## 5. Workspace Service — Full Config

```yaml
hermes-workspace:
  image: ghcr.io/outsourc-e/hermes-workspace:latest
  depends_on:
    hermes-agent:
      condition: service_healthy
  volumes:
    - workspace-data:/home/workspace   # Required for session persistence
  environment:
    HERMES_API_URL: http://hermes-agent:8642
    HERMES_DASHBOARD_URL: http://hermes-agent:9119
    HERMES_API_TOKEN: ${API_SERVER_KEY:-}
    HERMES_DASHBOARD_TOKEN: ${API_SERVER_KEY:-}
    HERMES_PASSWORD: ${HERMES_PASSWORD:-HERMES_WORKSPACE_PASSWORD_REDACTED}
    COOKIE_SECURE: "0"                 # Required for plain-HTTP deployments
```

### Volume for session persistence

The workspace writes sessions to `/home/workspace/.hermes/workspace-sessions.json`. Without a volume, this directory doesn't exist and login fails silently. Declare the volume:

```yaml
volumes:
  workspace-data:
    name: workspace-data
```

### COOKIE_SECURE

Plain-HTTP deployments (no TLS) MUST have `COOKIE_SECURE=0`. Without it, browsers silently drop session cookies and login fails with no error.

## 6. API Server Key

The agent's `API_SERVER_KEY` must be in the `.env` file:
```
API_SERVER_KEY=your-secret-key
```

The workspace passes it as `HERMES_API_TOKEN` and `HERMES_DASHBOARD_TOKEN`. When the gateway binds to 127.0.0.1, `API_SERVER_KEY` may not be required by the agent, but the workspace needs it for API calls.

## 7. Stale Lock Files

The agent writes `/opt/data/gateway.lock` in the named volume. If the container crashes or restarts uncleanly, this file persists with wrong ownership and blocks restart with:
```
PermissionError: [Errno 13] Permission denied: '/opt/data/gateway.lock'
```

**Fix:** Clear it before restarting:
```bash
docker run --rm -v hermes-data:/opt/data alpine rm -f /opt/data/gateway.lock
```

## 8. Dashboard Auth — The HTML-Scrape Quirk

The dashboard's `/api/skills` endpoint does NOT accept Bearer tokens or API keys for auth. It only accepts session tokens that are generated and injected into the `/` HTML page:

```html
<script>window.__HERMES_SESSION_TOKEN__="ZRjBwUc...";</script>
```

The workspace uses a "legacy HTML-scrape token flow" that:
1. Fetches `/` from the dashboard
2. Extracts `__HERMES_SESSION_TOKEN__` from the HTML
3. Uses that token for subsequent API calls

**Critical:** Do NOT set `CLAUDE_DASHBOARD_TOKEN` – it overrides the HTML-scrape flow and causes all dashboard API calls to return 401 Unauthorized. The dashboard session token is per-process and generated at startup.

## 9. Debugging "0 Skills" in Workspace

Full diagnostic chain:

```bash
# 1. Check if dashboard is running
curl -s http://127.0.0.1:9119/api/status

# 2. Check skills count in container
docker exec hermes-agent bash -c "find /opt/data/skills/ -name 'SKILL.md' | wc -l"

# 3. Test dashboard skills API with scraped token
TOKEN=$(curl -s http://127.0.0.1:9119/ | sed -n 's/.*__HERMES_SESSION_TOKEN__="\([^"]*\)".*/\1/p')
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:9119/api/skills | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Skills: {len(d)}')"

# 4. Check workspace connectivity mode
docker logs hermes-workspace | grep 'gateway.*mode='
# Should show: mode=zero-fork enhanced=[..., skills, ...]
```

If step 3 returns 0 skills: skills directory is wrong or empty in the container.
If step 3 returns N skills but workspace shows 0: auth issue (check step 4, remove CLAUDE_DASHBOARD_TOKEN).

## 10. Restart Procedure

```bash
cd /root/hermes-docker

# Clear stale locks
docker run --rm -v hermes-data:/opt/data alpine rm -f /opt/data/gateway.lock

# Force recreate everything
docker compose up -d --force-recreate

# Verify
curl -s http://127.0.0.1:8642/health
docker logs hermes-workspace | grep 'gateway.*mode='
```

## Pitfalls

- **Wrapper entrypoint scripts** — the image's `entrypoint.sh` must be entrypoint PID 1. Wrappers break the venv/gosu chain.
- **CLAUDE_DASHBOARD_TOKEN** — setting this env var kills the HTML-scrape auth. Just use `HERMES_DASHBOARD_TOKEN` and let the scrape flow work.
- **HERMES_DASHBOARD=1 missing** — dashboard won't start, workspace falls to portable mode.
- **COOKIE_SECURE not set to "0"** — browsers silently drop session cookies on plain HTTP.
- **No workspace-data volume** — `/home/workspace` doesn't exist, session writes fail, login fails.
- **Skills not bind-mounted** — only 89 bundled skills appear instead of full 190+.
- **0.0.0.0 API bind without key** — agent refuses to start without API_SERVER_KEY on non-loopback bind.
