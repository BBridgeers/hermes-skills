#!/bin/bash
# Generic git polling watcher for VPS auto-deployment.
# Copy to /usr/local/bin/repo-watcher.sh, customize REPO_BRANCH and REPO_SERVICES, then:
#   chmod +x /usr/local/bin/repo-watcher.sh
#   systemctl enable --now repo-watcher.service

set -euo pipefail

LOG="/var/log/repo-watcher.log"
PIDFILE="/var/run/repo-watcher.pid"
INTERVAL=30

# === CONFIGURE THESE ===
declare -A REPO_BRANCH=(
  ["/path/to/repo1"]="main"
  ["/path/to/repo2"]="master"
)

declare -A REPO_SERVICES=(
  ["/path/to/repo1"]="app1.service"
  ["/path/to/repo2"]="app2.service"
)
# =======================

echo "$$" > "$PIDFILE"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"; }

restart_services() {
  local repo="$1"
  local services="${REPO_SERVICES[$repo]}"
  for svc in $services; do
    # Detect user-scoped services and set XDG_RUNTIME_DIR
    if systemctl --user list-unit-files "$svc" &>/dev/null; then
      XDG_RUNTIME_DIR="/run/user/$(id -u)" systemctl --user restart "$svc" || log "WARN: failed to restart $svc"
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
