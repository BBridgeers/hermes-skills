---
name: hermes-workspace-auth-setup
title: Hermes Workspace Authentication Setup Guide
description: Configure correct environment variables for Workspace to authenticate with Agent Gateway using Bearer tokens, session tokens, or password mode
tags: [hermes, workspace, authentication, docker, env-vars, bearer-token]
difficulty: medium
---

# Hermes Workspace Authentication Setup Guide

## Problem
Hermes Workspace returns `Unauthorized` errors or fails to connect to the Agent Gateway when environment variables are misconfigured. TheWorkspace expects specific env vars for different auth modes.

## Auth Modes Overview

| Mode | Use Case | Required Env Vars |
|------|----------|-------------------|
| **Bearer Token** | API integrations, programmatic access | `HERMES_API_TOKEN`, `CLAUDE_DASHBOARD_TOKEN`, `HERMES_PASSWORD` |
| **Password** | Web UI login, manual access | `HERMES_PASSWORD` or `CLAUDE_PASSWORD` |
| **Insecure** | Dev/testing, no UI | `HERMES_ALLOW_INSECURE_REMOTE=1` |

## Environment Variable Reference

### Required Core Variables
| Variable | Purpose | Value |
|----------|---------|-------|
| `HERMES_API_URL` | Agent Gateway API | `http://hermes-agent:8642` |
| `HERMES_DASHBOARD_URL` | Agent Dashboard | `http://hermes-agent:9119` |
| `HERMES_API_TOKEN` | Bearer token for API calls | `your-api-key-here` |
| `CLAUDE_DASHBOARD_TOKEN` | Dashboard auth token | Same as `HERMES_API_TOKEN` |
| `HERMES_PASSWORD` | Password protection mode | Any string (or remove to disable) |

### Security Bypass Variables
| Variable | Purpose |
|----------|---------|
| `COOKIE_SECURE=0` | Allow cookies over HTTP (required for LAN access) |
| `HERMES_ALLOW_INSECURE_REMOTE=1` | Skip password requirement warning |

## Docker Compose Example

```yaml
services:
  hermes-workspace:
    image: ghcr.io/outsourc-e/hermes-workspace:latest
    container_name: hermes-workspace
    ports:
      - "3100:3000"
    environment:
      - HERMES_API_URL=http://hermes-agent:8642
      - HERMES_DASHBOARD_URL=http://hermes-agent:9119
      - HERMES_API_TOKEN=HERMES_API_KEY_REDACTED
      - CLAUDE_DASHBOARD_TOKEN=HERMES_API_KEY_REDACTED
      - HERMES_PASSWORD=HERMES_WORKSPACE_PASSWORD_REDACTED
      - COOKIE_SECURE=0
    depends_on:
      - hermes-agent
    networks:
      - mc-net
```

## Manual Docker Run Example

```bash
docker run -d \
  --name hermes-workspace \
  -p 3100:3000 \
  --network mission-control_mc-net \
  -e HERMES_API_URL=http://hermes-agent:8642 \
  -e HERMES_DASHBOARD_URL=http://hermes-agent:9119 \
  -e HERMES_API_TOKEN=HERMES_API_KEY_REDACTED \
  -e CLAUDE_DASHBOARD_TOKEN=HERMES_API_KEY_REDACTED \
  -e HERMES_PASSWORD=HERMES_WORKSPACE_PASSWORD_REDACTED \
  -e COOKIE_SECURE=0 \
  -v workspace-data:/home/workspace \
  ghcr.io/outsourc-e/hermes-workspace:latest
```

## Authentication Flow

### With `HERMES_API_TOKEN` Set
1. Workspace checks for `HERMES_PASSWORD` - if set, enables password mode
2. Workspace uses `HERMES_API_TOKEN` as the session token
3. Bearer token auth on `/api/*` endpoints works
4. Session cookies are still set for web UI

### Without `HERMES_API_TOKEN`
1. Workspace uses password-based session creation
2. User must login via web UI at `http://vps:3100`
3. Bearer token auth fails (no token exchange)

### With `HERMES_ALLOW_INSECURE_REMOTE=1` and no password
1. Workspace runs without password requirement
2. No login UI shown
3. Bearer token auth depends on token presence

## Diagnosis Checklist

Step 0 (MANDATORY FIRST STEP): Is the workspace container even running?

```bash
# Check if port 3100 is listening — if this fails with "Connection refused",
# the workspace container is DOWN. Auth/env debugging is IRRELEVANT until
# the container is running again. Jump to "Pitfall 5: Workspace container down."
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3100/api/config
```

Only proceed past Step 0 if the workspace responds (200/401/403). If you get
000 or "Connection refused", the container is down — see Pitfall 5.

```bash
# 1. Verify workspace is running
docker ps --format '{{.Names}}: {{.Status}}' | grep hermes-workspace

# 2. Check auth env vars are set
docker exec hermes-workspace env | grep -E 'HERMES_API_TOKEN|CLAUDE_DASHBOARD_TOKEN|HERMES_PASSWORD'

# 3. Test agent gateway directly
curl -s -H "Authorization: Bearer HERMES_API_KEY_REDACTED" http://127.0.0.1:8642/api/models

# 4. Check workspace logs for auth errors
docker logs hermes-workspace | grep -E "(401|Unauthorized|error)" | tail -20

# 5. Verify dashboard is accessible
curl -s http://127.0.0.1:9119 | grep "Hermes Dashboard"
```

## Common Pitfalls

### Pitfall 1: Duplicate Env Var Entries
Docker Compose treats duplicate keys as overridden (last one wins). This can cause hard-to-debug issues:

```yaml
# WRONG - multiple HERMES_API_TOKEN entries
environment:
  - HERMES_API_TOKEN: ${API_SERVER_KEY:-}
  - HERMES_API_TOKEN: HERMES_API_KEY_REDACTED  # Overwrites above

# CORRECT - single entry
environment:
  - HERMES_API_TOKEN=HERMES_API_KEY_REDACTED
```

### Pitfall 2: Environment Variable Substitution Failure
Using `${VAR:-default}` when `VAR` is set but empty in `.env` file will use empty string, not the default:

```bash
# If .env has empty line: API_SERVER_KEY=
# Then ${API_SERVER_KEY:-default} evaluates to empty, not "default"

# FIX: Set a value in .env
API_SERVER_KEY=HERMES_API_KEY_REDACTED
```

### Pitfall 3: Cookie Security on HTTP Access
If `COOKIE_SECURE=0` is missing, browsers silently reject cookies over plain HTTP (no TLS):

```yaml
# MUST be present for LAN access without HTTPS
- COOKIE_SECURE=0
```

### Pitfall 4: CLAUDE_* Env Vars Break Dashboard Token Flow
Setting `CLAUDE_DASHBOARD_TOKEN` or `CLAUDE_API_TOKEN` causes the workspace
to skip the HTML-scrape token flow and use the env var as a Bearer token —
which the dashboard REJECTS with 401. Only set `HERMES_API_TOKEN`.

### Pitfall 5: Workspace Container Not Running (Port 3100 Connection Refused)

Symptom: Workspace UI shows "void" / empty config, API keys marked "Not configured",
or the page doesn't load at all. `curl http://127.0.0.1:3100/api/config` returns
"Connection refused."

This is NOT an auth problem. The workspace container is simply down. The gateway
(8642) and dashboard (9119) may be running fine, but without the workspace
container, the config page can't render.

Restart from the VPS host:

```bash
cd /root/hermes-docker
docker compose up -d hermes-workspace
# If that fails, fully recreate:
docker compose up -d --force-recreate hermes-workspace
```

Verify it came up:

```bash
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3100/
# Should return 200 (login page) or 302 (redirect)
```

This is a recurring issue — the workspace container can stop after Docker host
restarts or when the agent container is recreated without also recreating the
workspace.

### Pitfall 6: Docker Network vs Localhost
Workspace container needs Docker network names, not `localhost`:

```yaml
# WRONG - won't resolve inside container
- HERMES_API_URL=http://127.0.0.1:8642

# CORRECT - uses Docker DNS
- HERMES_API_URL=http://hermes-agent:8642
```

## Verification

After setup, these endpoints should work:

```bash
# Dashboard (uses CLAUDE_DASHBOARD_TOKEN)
curl -s -H "Authorization: Bearer HERMES_API_KEY_REDACTED" http://127.0.0.1:9119/api/models

# Workspace enhanced APIs (uses HERMES_API_TOKEN as session)
docker exec hermes-workspace curl -s http://localhost:3000/api/skills

# Agent Gateway (uses HERMES_API_KEY in .env)
curl -s http://127.0.0.1:8642/api/health
```

## Security Recommendations

1. **Never commit** `.env` files with real tokens to Git
2. **Use strong passwords** for `HERMES_PASSWORD` in production
3. **Restrict ports** with firewall rules (UFW, security groups)
4. **Use HTTPS in production** and set `COOKIE_SECURE=1`
5. **Rotate tokens periodically** and restart workspace container