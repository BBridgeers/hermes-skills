---
name: hermes-workspace-401-fix
title: Fix Hermes Workspace Empty/Missing Data and 401 Errors
description: "Diagnose and resolve Hermes Workspace showing empty/void config, missing data on enhanced APIs (skills, sessions, memory, config), or returning 401 auth errors. Common causes include workspace container not running, token redaction in v0.12.0+, or missing API server endpoints."
tags: [hermes, workspace, 401, authentication, dashboard, container, diagnostics]
difficulty: medium
---

## Problem
Hermes Workspace enhanced API pages (/api/skills, /api/sessions, /api/memory, /api/config) show empty data or return errors. The agent dashboard may be accessible but workspace data appears void — either connection refused (container down), 401 Unauthorized (auth mismatch), or empty responses (missing endpoints).

## Root Cause
Hermes Agent v0.12.0+ redacts the dashboard session token in HTML responses for security. When the workspace container scrapes the dashboard HTML for `window.__HERMES_SESSION_TOKEN__`, it gets `"***"` instead of the real token, causing all subsequent API calls to fail with 401 Unauthorized.

## Quick Diagnosis

### Step 0: Is the workspace even running?
Many "void config" or "empty settings" reports are simply a stopped workspace container.
```bash
# Check if port 3100 is listening
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3100/api/config
# or from inside the agent container:
python3 -c "import socket; s=socket.socket(); s.settimeout(2); print('UP' if s.connect_ex(('127.0.0.1',3100))==0 else 'DOWN')"
```
If DOWN — restart it on the host:
```bash
cd /root/hermes-docker && docker compose up -d hermes-workspace
```
Only proceed to auth/debugging steps below if the workspace is confirmed running.

### Step 1: Check for auth errors
```bash
docker logs hermes-workspace | grep -E "(401|Error|error)"

# Verify dashboard is running
curl -s http://localhost:9119/ | grep "Hermes Dashboard"

# Test workspace endpoints (will likely 401)
curl -s -H "Cookie: claude-auth=..." http://localhost:3100/api/skills
```

## Solution Steps

### 1. Find the Live Dashboard Token
```bash
# Get the live token from the running agent container
docker exec hermes-agent-s8t0-hermes-agent-1 python3 -c "
import sys
sys.path.append('/opt/hermes')
from hermes_cli.web_server import _SESSION_TOKEN
print(_SESSION_TOKEN)
"
```

### 2. Configure Environment Variables
Edit `/root/hermes-docker/.env` and add:
```
CLAUDE_DASHBOARD_TOKEN=QtfA5Nc97qMwLrAnT7fNtSOXNqB1WK0QMl_wgmbkwMU
```

### 3. Update Docker Compose
Edit `/root/hermes-docker/docker-compose.yml` and modify the hermes-workspace service:
```yaml
services:
  hermes-workspace:
    environment:
      - CLAUDE_DASHBOARD_TOKEN=${CLAUDE_DASHBOARD_TOKEN:-}
      # Replace any existing HERMES_DASHBOARD_TOKEN line with:
      - HERMES_DASHBOARD_TOKEN=${CLAUDE_DASHBOARD_TOKEN:-}
```

### 4. Recreate Workspace Container
```bash
cd /root/hermes-docker
docker compose up -d --no-deps hermes-workspace
```

### 5. Verify Fix
```bash
# All these should now return 200
curl -s -H "Cookie: claude-auth=..." http://localhost:3100/api/skills | jq '. | length'
curl -s -H "Cookie: claude-auth=..." http://localhost:3100/api/models
curl -s -H "Cookie: claude-auth=..." http://localhost:3100/api/sessions
curl -s -H "Cookie: claude-auth=..." http://localhost:3100/api/gateway-status
```

## Persistent Token Sync (Optional)
The dashboard token regenerates on each agent restart. For permanent solution:

**Option A**: Startup script in agent container that exports token to shared volume
**Option B**: Host cron job that polls dashboard and updates .env file
**Option C**: Custom entrypoint that sets fixed token via additional env var

## Pitfalls
- **Workspace container down → void data, not 401s.** A stopped workspace returns connection refused, not a 401. The UI may show empty config, zero skills, blank sessions — check port 3100 before diving into auth debugging.
- Don't rely on HTML scraping for token extraction (gets redacted "***")
- The token is generated at Python module import time in web_server.py
- Workspace checks CLAUDE_DASHBOARD_TOKEN env var first, then falls back to scraping
- Memory endpoint may return 500 if /api/memory route not implemented on agent

## Verification
Success when:
- /api/skills returns 200 with skills array
- /api/models returns model capabilities
- /api/sessions shows session data
- No 401 errors in workspace logs

## References
- Workspace router code: /app/dist/server/assets/router-3Cq7OKQb.js
- Dashboard server: /opt/hermes/hermes_cli/web_server.py
- Token generation occurs at module level as random value
- Cookie auth also supported via claude-auth session cookie
