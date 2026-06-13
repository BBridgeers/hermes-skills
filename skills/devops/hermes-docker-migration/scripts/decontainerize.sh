#!/usr/bin/env bash
# =============================================================================
# Hermes Decontainerization Script
# Run as root on the VPS host (SSH in, NOT inside the container)
#
# PREREQUISITE: Take a VPS snapshot in your Hostinger control panel.
# =============================================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
log()  { echo -e "${GREEN}[+]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

HERMES_HOME="/root/.hermes"
VOLUME_SRC="/var/lib/docker/volumes/hermes-data/_data"
DOCKER_DIR="/root/hermes-docker"

# ── Phase 0: Preflight ──────────────────────────────────────────────────────

if [ "$(id -u)" -ne 0 ]; then
    err "Must run as root"
fi

echo ""
warn "PREREQUISITE: Take a full VPS snapshot before proceeding."
warn "If you haven't done this yet, press Ctrl+C NOW."
read -rp "Have you taken a VPS snapshot? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    err "Take a snapshot first, then re-run this script."
fi

log "Phase 0: Preflight checks"

docker info >/dev/null 2>&1 || err "Docker is not running"
[ -d "$VOLUME_SRC" ] || err "Volume $VOLUME_SRC not found"
[ -f "$HERMES_HOME/config.yaml" ] || err "$HERMES_HOME/config.yaml not found"

log "Preflight OK. Data sizes:"
du -sh "$VOLUME_SRC/sessions" "$VOLUME_SRC/state.db" "$VOLUME_SRC/checkpoints" "$VOLUME_SRC/logs" 2>/dev/null || true

# ── Phase 1: Install Dependencies ───────────────────────────────────────────

log "Phase 1: Installing system deps"
apt update -qq
apt install -y -qq curl python3 python3-pip python3-venv nodejs npm tmux
log "Python: $(python3 --version)"
log "Node:   $(node --version)"

# ── Phase 2: Install Hermes ─────────────────────────────────────────────────

log "Phase 2: Installing Hermes natively"
if [ -x "$HERMES_HOME/hermes-agent/bin/python" ] || [ -x "/root/.local/bin/hermes" ]; then
    log "Hermes already installed, skipping install script"
else
    curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
fi

# ── Phase 3: Stop Containers ────────────────────────────────────────────────

log "Phase 3: Stopping containers"
cd "$DOCKER_DIR" 2>/dev/null && docker compose down 2>/dev/null || {
    docker stop hermes-agent hermes-workspace 2>/dev/null || true
}
rm -f "$VOLUME_SRC/gateway.lock" "$VOLUME_SRC/gateway.pid" 2>/dev/null || true

# ── Phase 4: Merge Volume Data ──────────────────────────────────────────────

log "Phase 4: Merging volume data → $HERMES_HOME"

merge_dir() {
    if [ -d "$1" ]; then
        mkdir -p "$2"
        cp -a "$1"/* "$2/" 2>/dev/null || true
        log "  $1 → $2 ($(du -sh "$1" | cut -f1))"
    fi
}
merge_file() {
    if [ -f "$1" ]; then
        cp -a "$1" "$2"
        log "  $1 → $2"
    fi
}

merge_dir  "$VOLUME_SRC/sessions"     "$HERMES_HOME/sessions"
merge_dir  "$VOLUME_SRC/memories"     "$HERMES_HOME/memories"
merge_dir  "$VOLUME_SRC/logs"         "$HERMES_HOME/logs"
merge_dir  "$VOLUME_SRC/checkpoints"  "$HERMES_HOME/checkpoints"
merge_dir  "$VOLUME_SRC/plans"        "$HERMES_HOME/plans"
merge_dir  "$VOLUME_SRC/pastes"       "$HERMES_HOME/pastes"
merge_dir  "$VOLUME_SRC/cron"         "$HERMES_HOME/cron"
merge_dir  "$VOLUME_SRC/cache"        "$HERMES_HOME/cache"

merge_file "$VOLUME_SRC/state.db"                  "$HERMES_HOME/state.db"
merge_file "$VOLUME_SRC/kanban.db"                 "$HERMES_HOME/kanban.db"
merge_file "$VOLUME_SRC/gateway_state.json"        "$HERMES_HOME/gateway_state.json"
merge_file "$VOLUME_SRC/context_length_cache.yaml" "$HERMES_HOME/context_length_cache.yaml"
merge_file "$VOLUME_SRC/response_store.db"         "$HERMES_HOME/response_store.db"
merge_file "$VOLUME_SRC/auth.json"                 "$HERMES_HOME/auth.json.backup"

# ── Phase 5: Fix Ownership ──────────────────────────────────────────────────

log "Phase 5: Fixing ownership"
chown -R root:root \
    "$HERMES_HOME/sessions" "$HERMES_HOME/memories" "$HERMES_HOME/logs" \
    "$HERMES_HOME/checkpoints" "$HERMES_HOME/plans" "$HERMES_HOME/pastes" \
    "$HERMES_HOME/cron" "$HERMES_HOME/cache" "$HERMES_HOME/skills" \
    "$HERMES_HOME/state.db" "$HERMES_HOME/kanban.db" "$HERMES_HOME/gateway_state.json" \
    "$HERMES_HOME/context_length_cache.yaml" "$HERMES_HOME/response_store.db" 2>/dev/null || true
chmod -R u+rwX "$HERMES_HOME/sessions" "$HERMES_HOME/memories" "$HERMES_HOME/logs" \
    "$HERMES_HOME/checkpoints" "$HERMES_HOME/skills" 2>/dev/null || true

# ── Phase 6: Verify Config ──────────────────────────────────────────────────

log "Phase 6: Checking for container paths in config"
if grep -q '/opt/data' "$HERMES_HOME/config.yaml"; then
    warn "Found /opt/data references — review manually:"
    grep -n '/opt/data' "$HERMES_HOME/config.yaml"
else
    log "Clean — no /opt/data paths in config.yaml"
fi

# ── Phase 7: Systemd Service ────────────────────────────────────────────────

log "Phase 7: Creating systemd service"
cat > /etc/systemd/system/hermes-gateway.service << 'EOF'
[Unit]
Description=Hermes Agent Gateway
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
EnvironmentFile=/root/.hermes/.env
ExecStart=/root/.local/bin/hermes gateway run --replace
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
log "Service created"

# ── Done ────────────────────────────────────────────────────────────────────

echo ""
echo "=============================================================="
echo " Migration complete. Next steps (run MANUALLY):"
echo "=============================================================="
echo ""
echo "  1. Test:"
echo "     /root/.local/bin/hermes doctor"
echo "     /root/.local/bin/hermes chat -q 'confirm memory and sessions work'"
echo ""
echo "  2. Start gateway:"
echo "     systemctl enable --now hermes-gateway"
echo "     systemctl status hermes-gateway"
echo "     journalctl -u hermes-gateway -f"
echo ""
echo "  3. After 24h stable, clean Docker:"
echo "     cd /root/hermes-docker && docker compose down -v"
echo "     docker rmi nousresearch/hermes-agent:latest ghcr.io/outsourc-e/hermes-workspace:latest"
echo ""
echo "  4. Take another VPS snapshot."
echo "=============================================================="
