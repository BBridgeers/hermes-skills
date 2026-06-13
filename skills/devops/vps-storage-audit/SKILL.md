---
name: vps-storage-audit
version: 1
description: Audit and reclaim disk space on the Hermes VPS — profile every major space consumer, identify safe deletion targets, Docker volume/image/build-cache pruning, SQLite VACUUM, node_modules and cache cleanup, old kernel removal, and profile venv deduplication.
last-updated: 2026-06-01
---

# Skill: VPS Storage Audit & Cleanup

Version: 1
Triggered-by: User says "clean up disk", "free up space", "storage is full", "disk usage", "optimize storage", "what's taking up space", "nuke old stuff", or disk usage exceeds 85%

## Pattern

VPS disk fills up over time from Docker images/volumes/build cache, old kernels, profile venvs, npm/pnpm caches, SQLite database bloat, browser automation caches, duplicate project directories, and stale backups. This skill systematically profiles every space consumer and executes safe cleanups with zero data loss.

## Protocol

### Phase 1 — Disk Overview (5 seconds)

```bash
# Top-level breakdown
df -h / | tail -1
du -sh /var /root /usr /opt /home /snap 2>/dev/null | sort -rh
```

If disk usage is below 70%, report "Disk OK" and stop.

### Phase 2 — Profile Major Directories

```bash
# Root home (usually the biggest offender)
du -sh /root/* /root/.* 2>/dev/null | sort -rh | head -20

# Docker
docker system df

# Volumes
docker volume ls -q | while read v; do
  size=$(docker system df -v 2>/dev/null | grep "$v" | awk '{print $3}')
  echo "$v: $size"
done

# Hermes state
ls -lh /root/.hermes/state.db
du -sh /root/.hermes/hermes-agent/venv /root/.hermes/profiles /root/.hermes/sessions /root/.hermes/home
du -sh /root/.hermes/profiles/*/home 2>/dev/null | sort -rh | head -5
```

### Phase 3 — Identify Safe Deletion Targets

Check each category and flag for cleanup:

| Category | Check Command | Safe to Delete? |
|---|---|---|
| Old kernels (not current, not newest) | `dpkg -l \| grep linux-image \| awk '{print $2}'` | YES — keep current + one newer |
| Pre-migration backups | `du -sh /root/.hermes.pre-decontainerize` | YES — single-use, pre-decontainerize snapshot |
| Duplicate project dirs | `diff <(ls dir1 \| sort) <(ls dir2 \| sort)` | CASE-BY-CASE — verify no unique files first |
| Downloaded tarballs/archives | `find /root -maxdepth 2 -name "*.tar.gz" -o -name "*.zip"` | YES — redistributable |
| Docker build cache | `docker builder du --verbose 2>/dev/null` | YES — `docker builder prune -a -f` |
| Unused Docker volumes | `docker volume ls -q \| xargs -I{} docker volume inspect {} \| jq '.[0].Mountpoint'` | YES if not in use by active container |
| Unused Docker images | `docker image ls -f dangling=true` | YES — `docker image prune -a -f` |
| pnpm store | `du -sh /root/.local/share/pnpm` | YES — `pnpm store prune` |
| npm cache | `du -sh /root/.npm` | YES — `npm cache clean --force` |
| camoufox cache | `du -sh /root/.cache/camoufox` | YES — redistributable, deletes on cleanup |
| uv cache | `du -sh /root/.cache/uv` | PARTIAL — `uv cache clean` is safe |
| Playwright cache | `du -sh /root/.cache/ms-playwright` | ONLY if not using browser automation |
| pip cache | `du -sh /root/.cache/pip` | YES — `pip cache purge` |

### Phase 4 — Execute Cleanups

#### 4a. Old Kernel Removal

```bash
# Get current kernel
CURRENT=$(uname -r | cut -d- -f1-2)
# List all installed kernels
dpkg -l | grep linux-image | awk '{print $2}'
# Remove all except current and newest
DEBIAN_FRONTEND=noninteractive apt remove -y linux-image-6.8.0-XXX-generic linux-modules-6.8.0-XXX-generic linux-headers-6.8.0-XXX linux-headers-6.8.0-XXX-generic linux-tools-6.8.0-XXX linux-tools-6.8.0-XXX-generic
apt autoremove -y
apt clean
```

#### 4b. Docker Cleanup

```bash
# Prune build cache (reclaimable)
docker builder prune -a -f

# Prune unused volumes (check docker system df for reclaimable)
docker volume prune -f

# Remove specific unused volumes (NOT honcho or mission-control data)
docker volume rm hermes-data workspace-data 2>/dev/null

# Prune dangling images
docker image prune -a -f
```

**PITFALL**: Never prune volumes used by running containers. Check `docker ps --format "{{.Names}}"` before removing any volume. Honcho volumes (`honcho_pgdata`, `honcho_redis-data`) contain production memory data — ASK before removing.

#### 4c. Caches

```bash
# npm
npm cache clean --force 2>/dev/null

# pnpm (if installed)
pnpm store prune 2>/dev/null

# pip
pip cache purge 2>/dev/null

# uv
uv cache clean 2>/dev/null || rm -rf /root/.cache/uv

# camoufox (browser automation cache — reinstallable)
rm -rf /root/.cache/camoufox

# Playwright (only if not actively needed)
rm -rf /root/.cache/ms-playwright /root/.cache/ms-playwright-go

# Old tarballs
find /root -maxdepth 2 \( -name "*.tar.gz" -o -name "*.zip" -o -name "*.tar.xz" \) -delete
```

#### 4d. SQLite VACUUM (state.db)

```bash
# Check size
ls -lh /root/.hermes/state.db

# Install sqlite3 if missing
apt-get install -y sqlite3

# VACUUM to reclaim free pages
sqlite3 /root/.hermes/state.db "VACUUM;"

# Recheck size
ls -lh /root/.hermes/state.db
```

Typical savings: 30-50% of file size. VACUUM rewrites the entire database and rebuilds indexes — Hermes must NOT be running during VACUUM (stop gateway first).

#### 4e. Profile Venvs

Profile `home/` directories contain Python venvs that can be rebuilt:

```bash
# List profile venvs by size
du -sh /root/.hermes/profiles/*/home/* 2>/dev/null | sort -rh

# To rebuild a specific profile venv:
# 1. Save the requirements
/root/.hermes/profiles/<name>/home/bin/pip freeze > /tmp/<name>-requirements.txt
# 2. Remove the venv
rm -rf /root/.hermes/profiles/<name>/home
# 3. Rebuild (hermes init will recreate)
# OR manually: python3 -m venv /root/.hermes/profiles/<name>/home && source .../bin/activate && pip install -r /tmp/<name>-requirements.txt
```

**PITFALL**: Only rebuild venvs for profiles you can afford downtime on. The deep-researcher venv at 2.8GB is the usual suspect. Always save requirements first.

#### 4f. Stale Backups and Duplicates

```bash
# Pre-decontainerize backup (one-time use, already migrated)
rm -rf /root/.hermes.pre-decontainerize

# Duplicate workspace dirs — verify with diff first
# du -sh /root/hermes-workspace /root/hermes-workspace-new
# If hermes-workspace-new is a full duplicate, remove it
# diff <(ls /root/hermes-workspace/ | sort) <(ls /root/hermes-workspace-new/ | sort)
```

#### 4g. Voicevox Image (4.7GB)

The voicevox Docker image is the single largest image. If the voice avatar project (`hermes-av1-workforce`) is not actively in use:

```bash
docker stop voicevox_engine 2>/dev/null
docker rm voicevox_engine 2>/dev/null
docker rmi voicevox/voicevox_engine:cpu-ubuntu20.04-latest
```

**PITFALL**: Always ask the operator before removing Docker images they may still need. The voicevox image is 4.7GB — only nuke if confirmed inactive.

### Phase 5 — Final Check

```bash
df -h / | tail -1
du -sh /root /var /usr /opt 2>/dev/null | sort -rh
```

Compare to pre-cleanup numbers. Report total space reclaimed and current usage percentage.

## Failure Modes

| Problem | Cause | Fix |
|---|---|---|
| `dpkg lock` during kernel removal | Another apt process running | Wait or `kill` the process, then `dpkg --configure -a` |
| `docker builder prune` fails | No privileged access | Run as root or with sudo |
| SQLite VACUUM fails | Database locked by running process | Stop hermes-gateway first: `systemctl --user stop hermes-gateway` |
| Profile venv rebuild fails | Missing system packages | `apt-get install -y python3-venv python3-dev` |
| Disk still >85% after full cleanup | `node_modules` in project dirs | These are regenerated by `npm install` — safe to delete and rebuild |

## Examples

### Real Session (2026-06-01)
VPS at 87% disk usage. Profiling revealed:
- `.hermes.pre-decontainerize` backup: 3.9GB
- Docker build cache: 4.6GB
- Docker unused volumes (`hermes-data`): 4.6GB
- `deep-researcher` profile venv: 2.8GB
- `hermes-workspace/node_modules`: 1.8GB
- Caches (camoufox+uv+playwright+npm+pnpm): ~10GB
- `state.db` SQLite: 1.6GB
- `hermes-duplicate workspace`: 1.7GB
- voicevox Docker image: 4.7GB

**WebUI decommission cleanup**: After decommissioning hermes-webui (2026-06-03), the WebUI repo at `/root/hermes-webui/` (Python + static JS, ~53K lines) is no longer needed. Safe to remove entirely:
```bash
# Confirm WebUI service is disabled
systemctl is-enabled hermes-webui.service 2>&1  # should say "disabled"
# Remove the repo
rm -rf /root/hermes-webui
# Estimated savings: ~50-100MB depending on node_modules/pip cache
```
The `/root/hermes-webui/` directory is separate from the session archive at `/root/workspace/webui-archive/` (which preserves session data — do NOT delete the archive).

**Hermes runtime caches and snapshots** — safe to nuke at any time:
```bash
rm -rf /root/.hermes/webui              # 250MB+ — decommissioned WebUI dir, REDUNDANT with workspace archive
rm -rf /root/.hermes/state-snapshots    # 285MB+ — runtime snapshots, regenerated on next run
rm -rf /root/.hermes/sessions_backup_host  # 110MB+ — backup session data, primary copy is in ~/.hermes/sessions/
rm -rf /root/.hermes/lsp                # 107MB+ — language server protocol cache, regenerated
```
These four directories are safe, non-destructive cleanup targets. They were identified during the 2026-06-03 storage audit that freed ~5GB. The `.hermes/hermes-agent/venv` at 6.3GB is the single largest Hermes artifact — can be rebuilt with `pip install -e ~/.hermes/hermes-agent/` but requires a few minutes of downtime.

Total reclaimable: ~34GB from a 96GB disk (35% of total).