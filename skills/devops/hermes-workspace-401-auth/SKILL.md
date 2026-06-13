---
name: hermes-workspace-401-auth
description: Hermes Workspace enhanced APIs (skills, config, sessions, memory) return 401 Unauthorized when accessed with Bearer token - they use session-based auth instead, not Authorization header.
version: 1.0.0
author: Hermes Agent
license: MIT
---
# Hermes Workspace 401 Authentication Fix

## Problem
Hermes Workspace enhanced APIs (`/api/skills`, `/api/config`, `/api/sessions`, `/api/memory`) return `401 Unauthorized` when accessed via `curl -H "Authorization: Bearer <token>"`. The dashboard (port 9119) works fine with the same token.

## Root Cause
Hermes Workspace's enhanced API routes use **session-based authentication** (cookies or password), NOT Bearer token authentication. The `/api/skills` route checks `isAuthenticated(request)` which:
1. Checks if password protection is disabled → return true
2. Looks for session token from cookie header
3. Validates the session token

Bearer token in Authorization header is NOT checked.

## Dashboard vs Workspace Auth

### Dashboard (hermes-agent:9119)
- Accepts `CLAUDE_DASHBOARD_TOKEN` env var
- Uses `_SESSION_TOKEN` generated from env var
- Validates Bearer token in Authorization header

### Workspace (workspace:3100)
- Session-based auth only
- Uses `HERMES_PASSWORD` or `CLAUDE_PASSWORD` for password protection
- Uses session cookies (like a normal web app)

## Solution Options

### Option 1: Web UI Login (Recommended)
1. Open `http://<vps-ip>:3100` in browser
2. Login with `HERMES_PASSWORD` (if set) or go through passwordless flow
3. Session cookie is automatically set
4. Subsequent API calls work

### Option 2: Set Password Protection
Add to `docker-compose.yml` workspace environment:
```yaml
HERMES_PASSWORD: your-password-here
# or
CLAUDE_PASSWORD: your-password-here
```

## Verification

Dashboard works (Bearer token supported):
```bash
curl http://127.0.0.1:9119/api/skills -H "Authorization: Bearer <token>"
# Returns 200 OK
```

Workspace expects session auth:
```bash
curl http://127.0.0.1:3100/api/skills -H "Authorization: Bearer <token>"
# Returns 401 Unauthorized (expected behavior)
```

## Key Files
- `/app/dist/server/assets/router-3Cq7OKQb.js` - Contains `isAuthenticated()` check
- `isPasswordProtectionEnabled()` - Checks for HERMES_PASSWORD/CLAUDE_PASSWORD
- `getSessionTokenFromCookie()` - Extracts token from cookie header

## Common Misconception
The workspace's `CLAUDE_DASHBOARD_TOKEN` env var is used for OUTGOING requests TO the dashboard, not for INCOMING requests TO the workspace. It's for the workspace to authenticate itself when calling the dashboard, not for users to call the workspace.