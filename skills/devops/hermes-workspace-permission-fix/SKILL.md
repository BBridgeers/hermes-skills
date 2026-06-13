---
name: hermes-workspace-permission-fix
title: Fix EACCES Permission Denied Error in Hermes Workspace Swarm Agent
description: Resolve EACCES permission errors when Hermes Workspace tries to write to /app/swarm.yaml due to container filesystem ownership issues
tags: [hermes, workspace, permissions, eaves, docker, swarm-agent]
difficulty: medium
---

## Problem
When creating a Swarm Agent in Hermes Workspace, the action fails with:
```
EACCES: permission denied, open '/app/swarm.yaml'
```

The workspace container is healthy but cannot write the swarm configuration file to `/app/swarm.yaml`.

## Root Cause
The workspace container image is configured to run as user `workspace` (uid 10010), but the `/app` directory inside the container is owned by `root:root` with permissions `755`. The workspace user cannot write to root-owned directories.

```
drwxr-xr-x  1 root      root      4096 May  4 05:38 .
drwxr-xr-x  1 workspace workspace 4096 May  4 05:38 dist
-rw-r--r--  1 workspace workspace 3849 May  4 05:36 package.json
```

When the container starts as `workspace` user, it cannot `chmod` or `chown` the `/app` directory to make it writable.

## Diagnosis

### Check Container User
```bash
docker exec hermes-workspace id
# Expected: uid=10010(workspace) gid=999(workspace) groups=999(workspace)
```

### Check Directory Permissions
```bash
docker exec hermes-workspace ls -la /app
# /app should show root:root ownership, not writable by workspace user
```

### Check Container Logs
```bash
docker logs hermes-workspace | grep -i "eacc\|permission\|swarm"
# Look for "chmod: Operation not permitted" or "cannot create /app/swarm.yaml"
```

## Solution

### Option A: Start Container as Root, Fix Permissions, Then Switch User
```bash
# Stop existing workspace
docker stop hermes-workspace && docker rm hermes-workspace

# Run with --user 0:0 to start as root, fix permissions, then exec as workspace
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
```

### Option B: Modify Docker Compose to Include Permission Fix
Edit `/root/hermes-docker/docker-compose.yml`:

```yaml
services:
  hermes-workspace:
    image: ghcr.io/outsourc-e/hermes-workspace:latest
    command: ["sh", "-c", "chmod 777 /app && node server-entry.js"]
    user: "0:0"
    # ... rest of configuration
```

Then:
```bash
cd /root/hermes-docker && docker compose up -d hermes-workspace
```

### Option C: Pre-create with Custom Image (Permanent Fix)
If you maintain a custom workspace image:

```dockerfile
FROM ghcr.io/outsourc-e/hermes-workspace:latest
RUN chmod 777 /app
USER workspace
```

Then build and use this image in your compose file.

## Verification
After applying the fix:

```bash
# Verify /app is now writable
docker exec hermes-workspace sh -c "touch /app/swarm.yaml && echo 'Success' && rm /app/swarm.yaml"

# Check logs for successful startup
docker logs hermes-workspace --tail 5

# Try creating a Swarm Agent in the browser - should work without EACCES error
```

## Pitfalls
- The workspace container restarts if the entrypoint fails - check `docker ps -a` to see if it exited
- Changing `/app` permissions to `777` is a security risk - in production, use `chown workspace:workspace /app` instead
- The `chmod` command must run as root, so use `--user 0:0` or modify the entrypoint
- If you don't specify a custom command, the default `node server-entry.js` will fail if `/app` isn't writable
- Renamed or recreated workspace containers lose the `/app` fixing - use a custom image for persistence

## Alternative Workarounds
If you can't modify the container:
1. Use `/home/workspace/swarm.yaml` instead (already writable)
2. Disable swarm.yaml file creation (requires config change)
3. Use an init container that fixes permissions before workspace starts

## References
- Workspace Docker image: `ghcr.io/outsourc-e/hermes-workspace:latest`
- Default container user: `workspace` (uid 10010)
- `/app` directory is part of the container image, not a mount
- `/home/workspace` is the only writable volume (`workspace-data`)
", "file_content": "---\nname: hermes-workspace-permission-fix\ntitle: Fix EACCES Permission Denied Error in Hermes Workspace Swarm Agent\ndescription: Resolve EACCES permission errors when Hermes Workspace tries to write to /app/swarm.yaml due to container filesystem ownership issues\ntags: [hermes, workspace, permissions, eaves, docker, swarm-agent]\ndifficulty: medium\n---\n\n## Problem\nWhen creating a Swarm Agent in Hermes Workspace, the action fails with:\n```\nEACCES: permission denied, open '/app/swarm.yaml'\n```\n\nThe workspace container is healthy but cannot write the swarm configuration file to `/app/swarm.yaml`.\n\n## Root Cause\nThe workspace container image is configured to run as user `workspace` (uid 10010), but the `/app` directory inside the container is owned by `root:root` with permissions `755`. The workspace user cannot write to root-owned directories.\n\n```\ndrwxr-xr-x  1 root      root      4096 May  4 05:38 .\ndrwxr-xr-x  1 workspace workspace 4096 May  4 05:38 dist\n-rw-r--r--  1 workspace workspace 3849 May  4 05:36 package.json\n```\n\nWhen the container starts as `workspace` user, it cannot `chmod` or `chown` the `/app` directory to make it writable.\n\n## Diagnosis\n\n### Check Container User\n```bash\ndocker exec hermes-workspace id\n# Expected: uid=10010(workspace) gid=999(workspace) groups=999(workspace)\n```\n\n### Check Directory Permissions\n```bash\ndocker exec hermes-workspace ls -la /app\n# /app should show root:root ownership, not writable by workspace user\n```\n\n### Check Container Logs\n```bash\ndocker logs hermes-workspace | grep -i \"eacc\|permission\|swarm\"\n# Look for \"chmod: Operation not permitted\" or \"cannot create /app/swarm.yaml\"\n```\n\n## Solution\n\n### Option A: Start Container as Root, Fix Permissions, Then Switch User\n```bash\n# Stop existing workspace\ndocker stop hermes-workspace && docker rm hermes-workspace\n\n# Run with --user 0:0 to start as root, fix permissions, then exec as workspace\ndocker run -d \\\n  --name hermes-workspace \\\n  -p 3100:3000 \\\n  --network mission-control_mc-net \\\n  --hostname hermes-workspace \\\n  --env HERMES_API_URL=http://hermes-agent:8642 \\\n  --env HERMES_DASHBOARD_URL=http://hermes-agent:9119 \\\n  --env HERMES_API_TOKEN=HERMES_API_KEY_REDACTED \\\n  --env HERMES_DASHBOARD_TOKEN=HERMES_API_KEY_REDACTED \\\n  --env CLAUDE_DASHBOARD_TOKEN=HERMES_API_KEY_REDACTED \\\n  --env HERMES_PASSWORD=HERMES_WORKSPACE_PASSWORD_REDACTED \\\n  --env HERMES_ALLOW_INSECURE_REMOTE=1 \\\n  --env COOKIE_SECURE=0 \\\n  --volume workspace-data:/home/workspace \\\n  --user 0:0 \\\n  ghcr.io/outsourc-e/hermes-workspace:latest \\\n  sh -c \"chmod 777 /app && chown -R workspace:workspace /app && node server-entry.js\"\n```\n\n### Option B: Modify Docker Compose to Include Permission Fix\nEdit `/root/hermes-docker/docker-compose.yml`:\n\n```yaml\nservices:\n  hermes-workspace:\n    image: ghcr.io/outsourc-e/hermes-workspace:latest\n    command: [\"sh\", \"-c\", \"chmod 777 /app && node server-entry.js\"]\n    user: \"0:0\"\n    # ... rest of configuration\n```\n\nThen:\n```bash\ncd /root/hermes-docker && docker compose up -d hermes-workspace\n```\n\n### Option C: Pre-create with Custom Image (Permanent Fix)\nIf you maintain a custom workspace image:\n\n```dockerfile\nFROM ghcr.io/outsourc-e/hermes-workspace:latest\nRUN chmod 777 /app\nUSER workspace\n```\n\nThen build and use this image in your compose file.\n\n## Verification\nAfter applying the fix:\n\n```bash\n# Verify /app is now writable\ndocker exec hermes-workspace sh -c \"touch /app/swarm.yaml && echo 'Success' && rm /app/swarm.yaml\"\n\n# Check logs for successful startup\ndocker logs hermes-workspace --tail 5\n\n# Try creating a Swarm Agent in the browser - should work without EACCES error\n```\n\n## Pitfalls\n- The workspace container restarts if the entrypoint fails - check `docker ps -a` to see if it exited\n- Changing `/app` permissions to `777` is a security risk - in production, use `chown workspace:workspace /app` instead\n- The `chmod` command must run as root, so use `--user 0:0` or modify the entrypoint\n- If you don't specify a custom command, the default `node server-entry.js` will fail if `/app` isn't writable\n- Renamed or recreated workspace containers lose the `/app` fixing - use a custom image for persistence\n\n## Alternative Workarounds\nIf you can't modify the container:\n1. Use `/home/workspace/swarm.yaml` instead (already writable)\n2. Disable swarm.yaml file creation (requires config change)\n3. Use an init container that fixes permissions before workspace starts\n\n## References\n- Workspace Docker image: `ghcr.io/outsourc-e/hermes-workspace:latest`\n- Default container user: `workspace` (uid 10010)\n- `/app` directory is part of the container image, not a mount\n- `/home/workspace` is the only writable volume (`workspace-data`)\n", "file_path": "SKILL.md"}