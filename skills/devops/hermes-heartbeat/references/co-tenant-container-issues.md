# Co-Tenant Container Issues

## fb-scraper Created (port 8765 conflict)

**Date first observed**: 2026-06-02
**Container**: `fb-scraper`
**Status**: `Created` (never started)
**Error**: `failed to bind host port 0.0.0.0:8765/tcp: address already in use`

**Root cause**: A native Python process (`python3`, PID varies) is already listening on port 8765 (localhost only). The Docker container cannot bind the same port.

**Impact**: P2 WATCH — the container is not running and not consuming CPU, but:
- `docker ps -a` shows it as `Created` indefinitely
- The co-tenant container consumes metadata space
- If the native process dies, the container won't auto-start

**Resolution options**:
1. If the native process on 8765 is the primary, remove the Docker container: `docker rm fb-scraper`
2. If the Docker version is preferred, stop the native process and restart the container: `docker start fb-scraper`
3. If both are needed, change the Docker container's port mapping

**Detection**: Check `docker ps -a` for `Created` status, then `docker inspect <name> --format '{{.State.Status}} {{.State.Error}}'` for the reason.

**Classification**: P2 WATCH (co-tenant, not Hermes core). Do not auto-fix — flag only.

**Resolution**: 2026-06-05 — Container removed. No longer appears in `docker ps -a`. Issue resolved.