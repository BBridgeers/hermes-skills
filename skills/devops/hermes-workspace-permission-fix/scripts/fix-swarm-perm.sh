# Fix EACCES Permission Denied in Hermes Workspace

## The Problem
When creating a Swarm Agent, workspace fails with:
```
EACCES: permission denied, open '/app/swarm.yaml'
```

## Quick Fix (Run on VPS)
```bash
# Stop and remove workspace
docker stop hermes-workspace && docker rm hermes-workspace

# Run with --user 0:0 to fix /app permissions at startup
docker run -d \
  --name hermes-workspace \
  -p 3100:3000 \
  --network mission-control_mc-net \
  --hostname hermes-workspace \
  --env HERMES_API_URL=http://hermes-agent:8642 \
  --env HERMES_DASHBOARD_URL=http://hermes-agent:9119 \
  --env HERMES_API_TOKEN=HERMES_API_KEY_REDACTED \
  --env HERMES_DASHBOARD_TOKEN=HERMES_API_KEY_REDACTED \
  --env CLAUDE_DASHBOARD_TOKEN=HERMES_API_KEY_REDACTED \
  --env HERMES_PASSWORD=HERMES_WORKSPACE_PASSWORD_REDACTED \
  --env HERMES_ALLOW_INSECURE_REMOTE=1 \
  --env COOKIE_SECURE=0 \
  --volume workspace-data:/home/workspace \
  --user 0:0 \
  ghcr.io/outsourc-e/hermes-workspace:latest \
  sh -c "chmod 777 /app && chown -R workspace:workspace /app && node server-entry.js"

# Verify /app is writable
docker exec hermes-workspace sh -c "touch /app/swarm.yaml && echo 'Success'"
```

## After Fix
- Workspace should now show all 5 models in the picker
- Swarm Agent creation should work without EACCES error
- Access workspace at: `http://VPS_IP_REDACTED:3100`