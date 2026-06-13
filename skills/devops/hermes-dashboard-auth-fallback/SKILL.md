---
name: devops/hermes-dashboard-auth-fallback
title: Fix "Unauthorized" between Hermes Agent Gateway and Workspace Dashboard
description: |
  When the workspace dashboard loads but API calls (/, /api, /api/models, /api/sessions)
  return {"detail":"Unauthorized"}, the root cause is usually mismatched authentication
  tokens between CLAUDE_DASHBOARD_TOKEN and API_SERVER_KEY in the env files.
triggers:
  - Workspace UI loads but API endpoints return 401
  - Agent logs show repeated 401 errors from workspace
  - curl to /api from workspace returns {"detail":"Unauthorized"}
requirements:
  - Docker access to Hermes containers
  - Access to host .env files
---

# Hermes Authentication Token Synchronization

Hermes runs two auth-related tokens that must match:

| Token | Source | Purpose |
|-------|--------|---------|
| CLAUDE_DASHBOARD_TOKEN | ~/.hermes/.env + docker-compose .env_file | Dashboard/Workspace authentication |
| API_SERVER_KEY | ~/.hermes/.env + environment override | API gateway server auth |

The workspace container expects **both** tokens to be identical. If they differ,
the dashboard serves HTML (successful GET) but the API gateway rejects POST/PUT
requests with 401.

# Diagnostic Steps

## 1. Verify container environment variables

docker exec hermes-agent printenv CLAUDE_DASHBOARD_TOKEN API_SERVER_KEY

Both values should be identical. If they differ, that's the root cause.

## 2. Check host.env files match

grep -E 'CLAUDE_DASHBOARD_TOKEN|API_SERVER_KEY' /root/.hermes/.env /root/.hermes-docker/.env

Example output:
/root/.hermes/.env:API_SERVER_KEY=HERMES_API_KEY_REDACTED
/root/.hermes/.env:CLAUDE_DASHBOARD_TOKEN=hermes...2026
/root/.hermes/.env:HERMES_FIXED_SESSION_TOKEN=p43PFw...03R0

/root/.hermes-docker/.env:API_SERVER_KEY=HERMES_API_KEY_REDACTED
/root/.hermes-docker/.env:CLAUDE_DASHBOARD_TOKEN=hermes...2026
/root/.hermes-docker/.env:HERMES_FIXED_SESSION_TOKEN=p43PFw...03R0

Notice CLAUDE_DASHBOARD_TOKEN is masked (hermes...2026) but in reality
contains the wrong token (p43PFw...03R0) while API_SERVER_KEY is correct.

## 3. Test dashboard API directly

# The dashboard HTML endpoint (this may work even if API is broken)
curl -s http://127.0.0.1:9119

# The API gateway endpoint (this will fail with 401 if tokens don't match)
curl -s -H "Authorization: Bearer HERMES_API_KEY_REDACTED" http://127.0.0.1:9119/api

If HTML loads but /api returns <!doctype html> (no structured response), the
dashboard is using the wrong session token internally.

# Fix Procedure

## Step 1: Align tokens in host .env files

Set CLAUDE_DASHBOARD_TOKEN and HERMES_FIXED_SESSION_TOKEN to match API_SERVER_KEY:

sed -i 's/CLAUDE_DASHBOARD_TOKEN=.*/CLAUDE_DASHBOARD_TOKEN=HERMES_API_KEY_REDACTED/' /root/.hermes/.env
sed -i 's/HERMES_FIXED_SESSION_TOKEN=.*/HERMES_FIXED_SESSION_TOKEN=HERMES_API_KEY_REDACTED/' /root/.hermes/.env
sed -i 's/CLAUDE_DASHBOARD_TOKEN=.*/CLAUDE_DASHBOARD_TOKEN=HERMES_API_KEY_REDACTED/' /root/.hermes-docker/.env
sed -i 's/HERMES_FIXED_SESSION_TOKEN=.*/HERMES_FIXED_SESSION_TOKEN=HERMES_API_KEY_REDACTED/' /root/.hermes-docker/.env

## Step 2: Verify tokens exist in docker-compose.yml

Ensure the hermes-agent service in docker-compose.yml has:

environment:
  CLAUDE_DASHBOARD_TOKEN: ${CLAUDE_DASHBOARD_TOKEN:-}
  API_SERVER_KEY: ${API_SERVER_KEY:-}
  HERMES_FIXED_SESSION_TOKEN: ${HERMES_FIXED_SESSION_TOKEN:-}

## Step 3: Restart containers

cd /root/.hermes-docker
docker compose restart hermes-agent hermes-workspace

## Step 4: Verify fix

# Gateway API should no longer return Unauthorized
curl -s -H "Authorization: Bearer HERMES_API_KEY_REDACTED" http://127.0.0.1:9119/api

# If the above returns HTML or 404 (not Unauthorized), the auth is working
# Workspace UI should now be able to list skills, sessions, and config

# Pitfalls

1. **Masked secrets in .env** — The .env file shows *** or hermes...2026 for
   long tokens. Always compare the actual values after docker exec printenv,
   not what's displayed in the file editor.

2. **Stale container env** — docker compose restart is required. docker compose
   up -d without --force-recreate won't re-read the .env file if the container
   already exists.

3. **Dashboard HTML scapes the token** — The HTML includes <script>window.__HERMES_SESSION_TOKEN__="p43PFw..."</script>.
   If you see a different token here than in printenv CLAUDE_DASHBOARD_TOKEN,
   the container didn't pick up the new value.

4. **Whitespace or trailing newline corruption** — The HERMES_FIXED_SESSION_TOKEN
   value is used in the HTML session. If the token has trailing whitespace, the
   workspace will send a different auth header than what the dashboard expects.

5. **Two different auth schemes** — The dashboard uses CLAUDE_DASHBOARD_TOKEN
   for session-based auth, while the API gateway uses API_SERVER_KEY as a Bearer
   token. When the workspace acts as a proxy, it sends Authorization: Bearer
   <CLAUDE_DASHBOARD_TOKEN>, so both must be identical.

# Key Learnings

- The Hermes workspace expects CLAUDE_DASHBOARD_TOKEN to match the API server's
  API_SERVER_KEY. They are not separate credentials — they are the same token
  used in two different contexts.
- Docker Compose read .env files per-service, not globally. Both hermes-agent
  and hermes-workspace read /root/.hermes-docker/.env independently.
- The container's --env-file setting pulls values from /root/.hermes-docker/.env,
  not /root/.hermes/.env. Both must be aligned to the same value.

# Quick Recovery Command

If you encounter the error, run (replace HERMES_API_KEY_REDACTED with your actual key):

for f in /root/.hermes/.env /root/.hermes-docker/.env; do
  sed -i 's/CLAUDE_DASHBOARD_TOKEN=.*/CLAUDE_DASHBOARD_TOKEN=HERMES_API_KEY_REDACTED/' "$f"
  sed -i 's/HERMES_FIXED_SESSION_TOKEN=.*/HERMES_FIXED_SESSION_TOKEN=HERMES_API_KEY_REDACTED/' "$f"
done
cd /root/.hermes-docker && docker compose restart hermes-agent hermes-workspace