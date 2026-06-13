---
name: hermes-api-server-patch
title: Patch Hermes API Server Endpoints for Dashboard/Workspace
description: |
  When the Hermes dashboard or workspace shows missing/broken functionality
  (e.g., swarm model picker only shows "hermes-agent", 404 on /api/models),
  the root cause is often a missing endpoint on the API gateway server
  (port 8642, aiohttp) — NOT the dashboard web server (port 9119, FastAPI).
  
  This skill documents the dual-server architecture, how to identify which
  server handles a given request, and how to patch the correct one so the
  fix persists across container restarts.
triggers:
  - Dashboard swarm model picker shows only "hermes-agent"
  - /api/models returns 404 from workspace
  - Need to add a new endpoint visible to the workspace proxy
  - Patching web_server.py does not fix dashboard/workspace behavior
  - Container restart wipes out a file patch
requirements:
  - Docker access to hermes-agent container
  - Bind-mount setup in docker-compose.yml for persistence
---

# Hermes Dual-Server Architecture

Hermes runs **two separate HTTP servers** inside the container:

| Server | Port | Framework | Source File | Purpose |
|--------|------|-----------|-------------|---------|
| **Dashboard Web Server** | 9119 | FastAPI | `hermes_cli/web_server.py` | Serves React UI, dashboard APIs |
| **API Gateway Server** | 8642 | aiohttp | `gateway/platforms/api_server.py` | OpenAI-compatible API, workspace proxy target |

**Critical:** The workspace container proxies model/configuration queries to the
**API gateway server on port 8642**, NOT the dashboard server on 9119.

# Common Symptom: Swarm Model Picker Shows Only "hermes-agent"

The workspace asks `http://hermes-agent:8642/api/models` for the model list.
The API server's `_handle_models()` only returns `[{"id": "hermes-agent"}]`.
It has NO `/api/models` endpoint that returns fallback providers.

Meanwhile, the dashboard web server (`web_server.py`) may already have a patched
`/api/models` route — but the workspace never calls it.

# Step-by-Step Fix

## 1. Identify which server handles the request

```bash
# Test the API server (port 8642) — this is what the workspace sees
curl -s http://127.0.0.1:8642/api/models
# If 404, the API server is missing the endpoint

# Test the dashboard server (port 9119) — this is the React UI backend
curl -s http://127.0.0.1:9119/api/models
# May return data if web_server.py is patched, but workspace ignores this
```

## 2. Patch the correct file: `api_server.py`

The file lives at `/opt/hermes/gateway/platforms/api_server.py` inside the
container. It uses **aiohttp**, not FastAPI.

Add a handler method inside the `APIServerAdapter` class:

```python
async def _handle_api_models(self, request: "web.Request") -> "web.Response":
    """GET /api/models — return all configured models including fallbacks."""
    try:
        from hermes_cli.config import load_config
        cfg = load_config()
        models = []
        pm = cfg.get("model", {})
        if isinstance(pm, dict):
            pn = pm.get("default", pm.get("name", ""))
            pp = pm.get("provider", "")
        else:
            pn = str(pm) if pm else ""
            pp = ""
        if pn:
            models.append({
                "id": pn, "name": pn,
                "provider": pp or "hermes-agent",
                "owned_by": pp or "hermes-agent",
                "label": pn,
            })
        for fb in cfg.get("fallback_providers", []):
            if isinstance(fb, dict):
                fm = fb.get("model", "")
                fp = fb.get("provider", "hermes-agent")
                fl = fb.get("label", fm)
                if fm:
                    models.append({
                        "id": fm, "name": fm,
                        "provider": fp, "owned_by": fp,
                        "label": fl,
                    })
        return web.json_response({
            "models": models,
            "currentProvider": pp or "hermes-agent",
        })
    except Exception:
        return web.json_response({
            "models": [],
            "currentProvider": "hermes-agent",
        })
```

Register the route in the `run()` method where other routes are added:

```python
self._app.router.add_get("/api/models", self._handle_api_models)
```

## 3. Clear Python bytecode cache

```bash
docker exec hermes-agent rm -f \
  /opt/hermes/gateway/platforms/__pycache__/api_server.cpython-313.pyc
```

## 4. Make the patch persistent via bind mount

The container may be configured with bind mounts that overlay host files onto
the container filesystem. If you only patch inside the container, the change
is lost on recreate.

First, find a path the host can read. The container's `/opt/data/` is often
the host's root disk (sda1) mounted directly — files written there appear at
the same path on both sides. If that works, use it directly:
```bash
# From inside the container, write the patched file where the host can see it
cp /opt/hermes/gateway/platforms/api_server.py /opt/data/api_server_patched.py
```
Then from the host:
```bash
docker cp /opt/data/api_server_patched.py hermes-agent:/opt/hermes/gateway/platforms/api_server.py
```

Alternatively, use the traditional docker cp approach:

```bash
docker cp hermes-agent:/opt/hermes/gateway/platforms/api_server.py \
  /root/hermes-docker/api_server_patched.py
```

Add to `docker-compose.yml` under the `hermes-agent` service volumes:

```yaml
volumes:
  - /root/hermes-docker/api_server_patched.py:/opt/hermes/gateway/platforms/api_server.py
```

Recreate the container:

```bash
cd /root/hermes-docker
docker compose up -d --force-recreate hermes-agent
```

## 5. Verify

```bash
curl -s http://127.0.0.1:8642/api/models | python3 -m json.tool
```

Should return all models including fallback providers.

# Pitfalls

1. **Patching the wrong server** — `web_server.py` (port 9119) serves the React
   dashboard UI, but the workspace proxy calls the API server on port 8642.
   Always verify which port the consumer actually hits.

2. **Root-owned file** — `api_server.py` is owned by root (uid 0, 644) inside the
   container. The agent runs as hermes (uid 10000). You CANNOT edit the file from
   inside the container — use `docker cp` from the host. Same applies to the
   `__pycache__` dir: `docker exec -u root` or `docker exec hermes-agent rm -f`
   (the rm -f works if the container runs as root, but the file edit won't).

3. **Stale `.pyc` cache** — Even after patching the `.py` file, Python may load
   a newer `.pyc` from `__pycache__`. Delete the `.pyc` before restarting.

4. **Bind mount shadowing** — If `docker-compose.yml` bind-mounts a host file
   over the container path, in-container edits are invisible after restart.
   Always patch the host copy and declare the bind mount.

5. **Restart vs recreate** — `docker restart` reuses the container filesystem.
   If you added a new bind mount to `docker-compose.yml`, you must
   `docker compose up -d --force-recreate` to apply it.

6. **Two model endpoints** — The API server has `/v1/models` (OpenAI format,
   returns only `hermes-agent`) and `/api/models` (rich format with provider +
   label). For the workspace model-picker fix, patching `/v1/models` to read
   from config.yaml is often simpler than adding a new route — see
   `hermes-workspace-models-config-fix` for that alternative approach.
