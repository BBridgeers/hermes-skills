# VPS Disk Cleanup Playbook

Result of session 2026-06-01: freed 22GB (87% → 65%) on a 96GB disk.

## Quick Audit Commands

```bash
# Top-level offenders
du -sh /var /root /usr /opt /tmp /home 2>/dev/null

# Docker total
docker system df

# Find large hidden dirs
du -sh /root/.hermes /root/.cache /root/.local /root/.npm 2>/dev/null

# Find large visible dirs
du -sh /root/*/ 2>/dev/null | sort -rh | head -15

# Docker images by size
docker image ls --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" | sort -t$'\t' -k2 -rh
```

## Cleanup Targets (Ordered by Impact)

### 1. Old Pre-Decontainerize Backup (~4GB)
```bash
rm -rf /root/.hermes.pre-decontainerize
```

### 2. Duplicate Workspaces
If `hermes-workspace-new` or similar backup dirs exist:
```bash
# Verify they're truly duplicates first
ls /root/hermes-workspace-new/ | head -5
rm -rf /root/hermes-workspace-new
```

### 3. Docker Build Cache + Unused Volumes
```bash
docker builder prune -af
docker volume ls -q | while read v; do
  # Check if volume is in use by any container
  if ! docker ps -a --filter "volume=$v" -q | grep -q .; then
    docker volume rm "$v"
  fi
done
```

### 4. Profile Caches
Each Hermes profile has a sandboxed `home/.cache/` that accumulates pip, torch, browser caches:
```bash
for p in /root/.hermes/profiles/*/; do
  du -sh "$p/home/.cache" 2>/dev/null && rm -rf "$p/home/.cache"
done
rm -rf /root/.hermes/home/.cache
```

### 5. System Caches
```bash
rm -rf /root/.cache/camoufox      # Browser automation cache (~1.4GB)
rm -rf /root/.cache/ms-playwright  # Playwright browsers (~1.2GB)
rm -rf /root/.cache/ms-playwright-go
rm -rf /root/.cache/uv             # Python UV package cache (~1.2GB)
rm -rf /root/.cache/pip             # Pip cache
rm -rf /root/.local/share/pnpm     # Pnpm store (~2.8GB)
rm -rf /root/.local/share/claude   # Claude Code data (~226MB)
rm -rf /root/.local/share/uv       # UV data (~105MB)
rm -rf /root/.npm                  # NPM cache (~1.2GB)
apt clean
```

### 6. Old Kernel Packages
```bash
CURRENT=$(uname -r)
dpkg -l | grep linux-image | awk '{print $2}' | grep -v "$CURRENT" | while read pkg; do
  # Keep the newest installed kernel too (for next reboot)
  NEWEST=$(ls /boot/vmlinuz-* 2>/dev/null | sort -V | tail -1 | grep -o '[0-9].*[0-9]')
  KERNEL_VER=$(echo "$pkg" | grep -o '[0-9]\.[0-9]\.[0-9]-[0-9]*')
  if [ "$KERNEL_VER" != "$NEWEST" ] && [ "$KERNEL_VER" != "$CURRENT" ]; then
    DEBIAN_FRONTEND=noninteractive apt remove -y "$pkg"
  fi
done
apt autoremove -y
apt clean
```

### 7. Hermes state.db Vacuum
The session database grows large. Purge old sessions then VACUUM:

```bash
# Requires hermes-gateway stopped briefly
systemctl --user stop hermes-gateway
sqlite3 /root/.hermes/state.db <<'EOF'
DELETE FROM messages WHERE session_id IN (SELECT id FROM sessions WHERE started_at < strftime('%s','now','-14 days'));
DELETE FROM sessions WHERE started_at < strftime('%s','now','-14 days');
VACUUM;
EOF
systemctl --user start hermes-gateway
```

Note: If state.db doesn't shrink after VACUUM, the data is legit (not fragmentation). 3K+ sessions with 70K+ messages legitimately occupy ~1.5GB.

### 8. Ghost Directories
Check for abandoned project dirs, empty dated dirs, old tarballs:
```bash
find /root -maxdepth 1 \( -name "*.tar.gz" -o -name "*.zip" -o -name "*.tar.xz" \) -delete
# Review before deleting project dirs
ls -d /root/aionui-web /root/aiavatarkit /root/backup_before_fix 2>/dev/null
```

### 10. Torrent Download Backlog
If `/root/torrent/downloads/` is large (>10GB) and the rclone-upload cron failed:
```bash
# Check what's accumulated
du -sh /root/torrent/downloads/

# If qBittorrent is actively downloading, pause all torrents first, then drain:
rclone copy /root/torrent/downloads/ gdrive_personal:"VPS Torrents" \
  --config /root/.config/rclone/rclone.conf \
  --ignore-times --no-traverse --transfers 2 --drive-chunk-size 64M

# After copy completes, delete local:
rclone delete /root/torrent/downloads/ --config /root/.config/rclone/rclone.conf --min-age 5m
```
See `torrent-cloud-pipeline` skill for the full architecture.

### 9. Do NOT Delete (Without Confirmation)
- `/root/.hermes/hermes-agent/venv` (6.3GB) — Required for Hermes runtime
- `/root/.hermes/node` (673MB) — Node runtime for Hermes
- `/root/hermes-workspace/node_modules` — Needed for builds
- `/root/vehicle-analyzer/`, `/root/veracar-app/` — Active projects
- VoiceVox Docker image (4.67GB) — Used by hermes-avatar
- `/root/honcho/` — Active co-tenant service

## Expected Savings (Per Session)

| Target | Typical Size |
|---|---|
| Pre-decontainerize backup | 3-4GB |
| Docker build cache | 3-5GB |
| Unused Docker volumes | 2-5GB |
| Profile caches | 3-4GB |
| System caches (pnpm, pip, uv, playwright) | 5-8GB |
| Old kernels (3+) | 1-2GB |
| Duplicate workspaces | 1-2GB |
| state.db old sessions | 0.5-1GB |