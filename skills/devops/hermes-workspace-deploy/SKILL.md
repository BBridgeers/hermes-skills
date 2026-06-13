---
name: devops/hermes-workspace-deployment
description: Deploy Hermes Workspace v2.3.0 with proper configuration and auth setup. Covers Docker setup, API token injection, and troubleshooting common issues like EACCES permission errors.
---

# Hermes Workspace Deployment Guide

Version: 2.3.0 (zero-fork, runs on vanilla Hermes Agent)

## Prerequisites

- Docker + Docker Compose
- Hermes Agent gateway running at `http://<host>:8642`
- Hermes dashboard running at `http://<host>:9119` (for zero-fork installs)
- API token matching `API_SERVER_KEY` from Hermes Agent

## Quick Deploy (Docker)

```bash
docker stop hermes-workspace && docker rm -f hermes-workspace

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
  ghcr.io/outsourc-e/hermes-workspace:latest
```

## Verification Steps

1. Check container is healthy: `docker ps --filter name=hermes-workspace`
2. Verify API connection: `docker logs hermes-workspace --tail 5 | grep gateway`
3. Access at: `http://<vps-ip>:3100`

## Troubleshooting EACCES Errors

If workspace fails with `EACCES: permission denied, open '/app/swarm.yaml'`:

1. Confirm `/app` ownership: `docker exec hermes-workspace ls -la /app`
2. If owned by root: Container needs to be started as root briefly to fix permissions
3. Solution: Add `--user 0:0` to docker run, then `chmod 777 /app` in entrypoint
4. Alternative: Clone latest version from GitHub and deploy manually with `pnpm dev`

## Manual Install (Non-Docker)

```bash
cd /root
git clone https://github.com/outsourc-e/hermes-workspace.git hermes-workspace-new
cd hermes-workspace-new
git checkout v2.3.0

pnpm install
cp .env.example .env

# Add your configuration
echo 'HERMES_API_URL=http://127.0.0.1:8642' >> .env
echo 'HERMES_DASHBOARD_URL=http://127.0.0.1:9119' >> .env
echo 'HERMES_API_TOKEN=HERMES_API_KEY_REDACTED' >> .env

pnpm dev  # Runs on http://localhost:3000
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| HERMES_API_URL | Yes | Hermes Agent gateway URL (port 8642) |
| HERMES_DASHBOARD_URL | Yes | Hermes dashboard URL (port 9119) |
| HERMES_API_TOKEN | Yes | Same as API_SERVER_KEY in Hermes Agent |
| CLAUDE_DASHBOARD_TOKEN | Yes | Dashboard authentication token |
| HERMES_PASSWORD | Yes | Web UI password |
| COOKIE_SECURE | No | Set to "0" for HTTP access |
| HERMES_ALLOW_INSECURE_REMOTE | Yes | Bypass localhost-only restriction |
| HERMES_DASHBOARD | Yes | Enable dashboard sidecar |

## Latest Release

- **Version**: v2.3.0
- **Release Date**: May 8, 2026
- **Features**:
  - HermesWorld integration (playable agent MMO via iframe)
  - Agent View with live agent panel
  - Dashboard polish and bug fixes
  - Swarm mode improvements
  - Conductor (requires dashboard plugin - shows placeholder if missing)

## GitHub Repository

https://github.com/outsourc-e/hermes-workspace
Stars: 3902 | Forks: 507 | Primary Language: JavaScript

---

## Common Pitfalls

1. **EACCES permission denied**: `/app` owned by root, container runs as workspace user (uid 10010)
2. **API token mismatch**: Workspace uses `HERMES_API_TOKEN`, agent uses `API_SERVER_KEY` - must match
3. **Dashboard not found**: Must run `hermes dashboard` separately for enhanced APIs
4. **Cookies rejected**: `COOKIE_SECURE=0` required for HTTP access
5. **Docker network issues**: Use Docker network names (`hermes-agent:8642`) not localhost inside containers

## Key Learnings

- Workspace v2.3.0 uses zero-fork architecture - talks directly to vanilla Hermes Agent
- /app directory is part of container image, not a volume - ownership must be fixed before starting
- Running container with `--user 0:0` and entrypoint override fixes permission issues
- Manual clone from GitHub is cleaner than using pre-built Docker images when fixing permission issues