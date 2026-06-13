---
name: vps-auto-deployment
version: 1
category: devops
description: Automated git-based deployment on bare-metal VPS using polling watchers and systemd service orchestration.
---

# Skill: VPS Auto-Deployment — Git Polling Watcher

Version: 1
Category: devops
Last-updated: 2026-05-27

## Pattern

On a bare-metal VPS with multiple systemd-managed services, keep apps in sync with their GitHub remotes without cloud CI/CD. A systemd polling watcher checks repos every N seconds; on new commits it pulls and restarts the linked services. Works for both system services and user services.

## Protocol

### 1. Identify repos, branches, and services

Map each repo to its systemd service(s). Record branch names — they vary (`main` vs `master`).

```bash
# Discover repos with remotes
cd /root && find . -maxdepth 2 -type d -name .git -exec sh -c 'cd "$1/.." && echo "$(pwd) $(git remote get-url origin) [$(git branch --show-current)]"' _ {} \;
```

### 2. Write the watcher script

Place at `/usr/local/bin/repo-watcher.sh`. Template: `templates/repo-watcher.sh`.

Key design:
- `git fetch` then compare `HEAD` to `origin/<branch>` — avoids local dirty-tree false positives.
- Stash local changes before reset, pop after.
- Map repo path → branch → service list in an associative array.
- Handle both `systemctl` (system) and `XDG_RUNTIME_DIR=/run/user/0 systemctl --user` (user services).

### 3. Create the systemd unit

Place at `/etc/systemd/system/repo-watcher.service`. Template: `templates/repo-watcher.service`.

```ini
[Unit]
Description=Git Repo Auto-Pull Watcher
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/repo-watcher.sh
Restart=always
RestartSec=10
StandardOutput=append:/var/log/repo-watcher.log
StandardError=append:/var/log/repo-watcher.log

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl daemon-reload
systemctl enable --now repo-watcher.service
```

### 4. Verify loop

```bash
journalctl -u repo-watcher.service -f
tail -f /var/log/repo-watcher.log
```

Trigger a test push and confirm the log shows `FETCH → PULL → RESTART` for the correct service.

## Failure Modes

| Cause | Symptom | Fix |
|---|---|---|
| **User service without XDG_RUNTIME_DIR** | `systemctl --user restart svc` fails silently or returns `Failed to connect to bus` | Export `XDG_RUNTIME_DIR="/run/user/$(id -u)"` before every `--user` command in the watcher script. |
| **Branch name mismatch** | `FETCH FAILED` or `origin/main` not found | Verify with `git branch --show-current`. Hermes projects vary: `hermes-webui` uses `master`, others use `main`. |
| **SSH key not loaded** | `git fetch` prompts for password or fails auth | Ensure `ssh -T git@github.com` works as the user running the watcher (usually root). |
| **Service restart race** | App binds to port before old process exits | Add `sleep 2` after stop and before start, or use `systemctl restart` (atomic). |
| **Dirty tree blocks pull** | `error: Your local changes...` | Stash before reset, pop after. If pop fails, log it — do not silently drop changes. |

## Examples

### Three-repo watcher (vehicle-analyzer, hermes-webui, hermes-workspace)

```bash
#!/bin/bash
# /usr/local/bin/ag-repo-watcher.sh
set -euo pipefail

LOG="/var/log/ag-repo-watcher.log"
PIDFILE="/var/run/ag-repo-watcher.pid"
INTERVAL=30

# Map: repo_dir -> branch -> "service1 service2 ..."
declare -A REPO_BRANCH=(
  ["/root/vehicle-analyzer"]="main"
  ["/root/hermes-webui"]="master"
  ["/root/hermes-workspace"]="main"
)

declare -A REPO_SERVICES=(
  ["/root/vehicle-analyzer"]="veracar-nextjs.service fb-scraper.service veracar-scraper.service"
  ["/root/hermes-webui"]="hermes-webui.service"
  ["/root/hermes-workspace"]="hermes-workspace.service"
)

echo "$$" > "$PIDFILE"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"; }

restart_services() {
  local repo="$1"
  local services="${REPO_SERVICES[$repo]}"
  for svc in $services; do
    if [[ "$svc" == hermes-workspace.service ]]; then
      # User service needs XDG_RUNTIME_DIR
      XDG_RUNTIME_DIR="/run/user/0" systemctl --user restart "$svc" || log "WARN: failed to restart $svc"
    else
      systemctl restart "$svc" || log "WARN: failed to restart $svc"
    fi
    log "Restarted $svc"
  done
}

log "Watcher started (PID $$)"

while true; do
  for repo in "${!REPO_BRANCH[@]}"; do
    branch="${REPO_BRANCH[$repo]}"
    cd "$repo" || continue

    if ! git fetch origin "$branch" >> "$LOG" 2>&1; then
      log "FETCH FAILED: $repo"
      continue
    fi

    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/"$branch")

    if [ "$LOCAL" != "$REMOTE" ]; then
      log "UPDATE detected: $repo ($LOCAL -> $REMOTE)"
      git stash push -m "auto-stash-$(date +%s)" >> "$LOG" 2>&1 || true
      git reset --hard origin/"$branch" >> "$LOG" 2>&1
      git stash pop >> "$LOG" 2>&1 || true
      restart_services "$repo"
      log "Updated and restarted $repo"
    fi
  done
  sleep "$INTERVAL"
done
```

## Support Files

- `templates/repo-watcher.sh` — Generic polling watcher script (copy and modify repo map)
- `templates/repo-watcher.service` — Systemd unit template
- `references/vps-deployment-pitfalls.md` — Session-specific details: XDG_RUNTIME_DIR fix, branch mismatches, service mappings