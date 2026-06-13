---
name: rclone-gdrive-vps
description: Mount Google Drive on a headless VPS via rclone for Docker services (qBittorrent, etc.). Covers OAuth on headless machines, rclone mount flags, VFS cache management, Docker bind-mount gotchas, and GDrive rate-limit survival.
version: 1.1.0
tags: [rclone, gdrive, vps, fuse, qbittorrent, docker, oauth]
---

# rclone + Google Drive on Headless VPS

Mount Google Drive directories on a headless VPS via rclone FUSE mount, typically to serve as storage backend for Docker containers (qBittorrent, Plex, etc.).

## Trigger

Any time you need to:
- Mount a Google Drive folder on a headless VPS
- Auth rclone to Google Drive without a browser on the VPS
- Debug a rclone mount that won't start or hangs
- Connect a Docker container to a rclone FUSE mount

## OAuth — Headless Auth Pattern

The VPS has no browser. You MUST generate the token on a machine that does.

### Step 1: Generate token on a machine WITH a browser

On the user's laptop (Windows/Mac/Linux with rclone installed):
```bash
rclone authorize drive
```
Browser opens → click Allow → JSON blob appears in terminal. Copy the full `{"access_token":"...","refresh_token":"...","expiry":"..."}` block.

If rclone isn't installed on the laptop:
```powershell
# Windows
winget install rclone
```

### Step 2: Write config on VPS

Use ONLY the token blob — do NOT add custom `client_id` or `client_secret` unless you generated the token with those specific credentials. The rclone binary has its own built-in OAuth client that can refresh tokens it issued.

```ini
[gdrive_personal]
type = drive
scope = drive
token = {"access_token":"ya29...","token_type":"Bearer","refresh_token":"1//...","expiry":"2026-...","expires_in":3599}
```

### Pitfall: Authorization codes are NOT tokens

If the user provides a URL like `http://127.0.0.1:53682/?...&code=4/0AeoWuM8...`, that `code` is an OAuth authorization code — NOT a token. It expires in ~5 minutes and is bound to the client_id that requested it. You cannot exchange it on a different machine with different credentials. Get the actual JSON token blob from the terminal, not the browser URL.

### Pitfall: Do NOT mix client credentials

If the token was issued by rclone's built-in OAuth client, do NOT add `client_id` and `client_secret` to your config. The refresh flow will fail with `unauthorized_client`. Let rclone use its own baked-in credentials.

## Mount Command

### Working minimal flags

```bash
rclone mount gdrive_personal:"Folder Name" /mount/path \
  --vfs-cache-mode writes \
  --allow-other \
  --daemon \
  --vfs-cache-max-size 18G \
  --transfers 2
```

### Flag reference

| Flag | Purpose |
|------|---------|
| `--vfs-cache-mode writes` | Cache writes locally, reads go direct to GDrive. Fastest startup. |
| `--vfs-cache-mode full` | Cache reads AND writes. MUCH slower startup (reconciles entire cache). Only use if you need local read speed. |
| `--allow-other` | Let other users (Docker containers) access the mount |
| `--allow-non-empty` | Mount over a non-empty directory (hides existing files) |
| `--daemon` | Fork to background. Hangs if GDrive API is rate-limited during init. |
| `--vfs-cache-max-size 18G` | Cap local VFS cache. Prevents disk fill. |
| `--transfers 2` | Concurrent GDrive uploads. Higher = more rate limiting. |
| `--fast-list` | Use GDrive's list API (fewer calls, but may hit different rate limits) |
| `--no-traverse` | Don't scan whole remote on startup. Faster init. |
| `--vfs-write-back 1m` | Flush writes to GDrive after 1min idle (default 5s). Longer = fewer small uploads. |
| `--vfs-cache-max-age 1h` | Delete cached files older than 1h (cleanup). |

### Do NOT use invalid flags

`--no-modtime` and `--no-checksum` do NOT exist as rclone mount flags. Using them causes silent mount failure.

## VFS Cache — Critical Operations

### Cache location

- VFS data: `/root/.cache/rclone/vfs/gdrive_personal/<remote name>/`
- VFS metadata: `/root/.cache/rclone/vfsMeta/gdrive_personal/<remote name>/`

### When mount hangs on startup

**Root cause**: Stale VFS cache from a previous session. rclone tries to reconcile every cached file against GDrive, and with rate limiting + many files, it never finishes.

**Fix**: Clear the cache before mounting:
```bash
pkill -9 rclone
fusermount -uz /mount/path
rm -rf /root/.cache/rclone/vfs /root/.cache/rclone/vfsMeta
# Then mount fresh
```

**Cost**: Any files in cache that hadn't been uploaded to GDrive yet are LOST. Only do this when the mount is broken and you accept data loss.

### Check if a file is still in cache (not yet uploaded)

```bash
cat "/root/.cache/rclone/vfsMeta/gdrive_personal/<remote>/<filename>" | grep "Dirty"
```
`"Dirty": true` means the file hasn't been uploaded to GDrive yet.

### Monitor cache size vs disk free

```bash
du -sh /root/.cache/rclone/
df -h /
```
Cache growing faster than uploads = disk will fill. Solutions:
- Decrease download speed in the consuming app (e.g., qBittorrent)
- Increase `--vfs-cache-max-size`
- Decrease `--vfs-write-back` to flush more aggressively

## Docker + rclone FUSE Mount

### The bind-mount restart rule

When a Docker container bind-mounts a rclone FUSE directory, and you unmount/remount rclone, the container's view of the directory may go stale. **Always restart the container after re-establishing the rclone mount.**

```bash
docker restart containername
```

### Verify the container sees the mount

```bash
docker exec containername df -h /container/path
```
Should show `gdrive_personal:...` as the filesystem type, not `ext2/ext3` or `overlay`.

### Hidden files under FUSE mounts

If a FUSE mount is placed over a directory that already contains files, those files are hidden (not deleted). When you unmount, they reappear. To clean them permanently:

```bash
fusermount -u /mount/path    # unmount FIRST
rm -rf /mount/path/*          # delete while unmounted
# then remount
```

## GDrive Rate Limiting

### Symptoms
- `rclone lsf` or `rclone about` times out
- Mount initialization hangs with `RATE_LIMIT_EXCEEDED` in debug logs
- Quota errors mentioning `defaultPerMinutePerProject`

### Mitigations
- Wait 60 seconds between mount attempts
- Use `--vfs-cache-mode writes` (not `full`) to minimize API calls
- Use `--fast-list` to batch directory listings
- Use `--no-traverse` to skip full remote scan on startup
- Limit `--transfers` to 1-2

## qBittorrent Integration

### Typical Docker setup

```yaml
# docker-compose excerpt
qbittorrent:
  image: lscr.io/linuxserver/qbittorrent:latest
  volumes:
    - /root/torrent/config:/config
    - /root/torrent/downloads:/downloads   # THIS is the rclone mount point
  ports:
    - "8080:8080"
    - "6881:6881/tcp"
    - "6881:6881/udp"
```

### Speed tuning for GDrive backend

Since GDrive uploads at ~15 MB/s and torrent downloads can hit 50+ MB/s, the VFS cache fills faster than it drains. Set qBittorrent speed limits:

- Global download limit: **20000 KB/s** (20 MB/s)
- Max active downloads: **2**

This keeps the cache from filling and causing download stalls.

### Restoring "Missing Files" after remount

When torrents show "Missing Files" after a mount change:
1. Verify mount is active: `docker exec qbittorrent df -h /downloads | grep gdrive`
2. Right-click torrent → Set Location → point to the correct path
3. Force Recheck

## Batch Processing — Pull / Process / Push Back

When you need to transform files on a rclone-synced directory (unzip archives, resize images, transcode media, etc.), do NOT operate directly on the FUSE mount. FUSE operations on rclone mounts are slow, fragile, and hammer the GDrive API. The reliable pattern:

1. **Pull** — `rclone copy` the files to local disk
2. **Process** — do the work locally (fast, no API calls)
3. **Push back** — `rclone copy` results up, with `--ignore-existing` to skip already-synced content

```bash
# Pull
mkdir -p /tmp/work && cd /tmp/work
rclone copy "gdrive_personal:path/to/files/" . --include "*.zip" -P

# Process (example: unzip)
for f in *.zip; do unzip -o "$f" -d "${f%.zip}/"; done

# Push back (skip what's already there)
rclone copy . "gdrive_personal:path/to/files/" --exclude "*.zip" --ignore-existing -P
```

This also makes the upload resumable — if it times out, re-run the same push command and `--ignore-existing` picks up where it left off.

### Why NOT process on the mount

- Every file stat/read/write on a FUSE mount is a GDrive API call
- `unzip` on a FUSE mount writes hundreds of small fragments, each triggering a separate upload
- Rate limiting causes stalls that look like hangs
- Partial failures leave the mount in an inconsistent state

## Directory Diff Verification — Find What's Missing

After uploading, verify that everything arrived. `rclone size` gives totals but doesn't tell you WHICH items are missing. Use `rclone lsf --dirs-only` + `comm` to diff local vs remote directories:

```bash
# List remote directories
rclone lsf "gdrive_personal:path/to/folder/" --dirs-only 2>/dev/null | sed 's|/$||' | sort > /tmp/remote_dirs.txt

# List local directories
ls -d *_slides/ | sed 's|/$||' | sort > /tmp/local_dirs.txt

# Items on LOCAL but NOT on REMOTE (need uploading)
comm -23 /tmp/local_dirs.txt /tmp/remote_dirs.txt

# Items on REMOTE but NOT on LOCAL (orphaned)
comm -13 /tmp/local_dirs.txt /tmp/remote_dirs.txt
```

**Then re-upload only the missing:**
```bash
comm -23 /tmp/local_dirs.txt /tmp/remote_dirs.txt | while read d; do
    rclone copy "$d" "gdrive_personal:path/to/folder/$d/" -P --ignore-existing
done
```

This pattern works for files too — use `rclone lsf` without `--dirs-only` and diff the lists.

### Pitfall: `--files-from` does NOT work with directories

`rclone copy --files-from -` only matches files, not directories. If you pipe directory names through it, rclone reports "There was nothing to transfer." Use the `while read` loop above instead.

## Diagnostics

```bash
# Is mount active?
cat /proc/mounts | grep rclone
mount | grep torrent

# What does the container see?
docker exec <name> df -h /downloads
docker exec <name> ls /downloads/

# GDrive usage
rclone about gdrive_personal:

# Cache size
du -sh /root/.cache/rclone/

# Upload queue
cat /tmp/rclone_mount.log | grep "queuing for upload" | tail -20

# Token still valid?
rclone about gdrive_personal: 2>&1 | head -3
# If it returns "Total:" with numbers, token is fine
```

## Alternative: Bare Disk + Cron Pipeline (No FUSE Mount)

When FUSE mount failures become chronic (rate-limit hangs, VFS cache corruption, double mounts), use the **bare disk + cron** pattern instead. This is MORE reliable than FUSE mounting for high-throughput torrent workloads.

### Architecture

```
qBittorrent → /root/torrent/downloads (bare ext4 disk, fast)
                     ↓ every 5 minutes
              rclone move (--min-age 5m)
                     ↓
              gdrive_personal:"VPS Torrents"
```

### Why This Beats FUSE Mount for Torrents

| Failure | FUSE Symptom | Bare-Disk Behavior |
|---------|-------------|-------------------|
| Rate-limit hang | `ls` empty, mount never initializes | Cron retries next tick — no user impact |
| VFS cache corruption | Mount stuck reconciling stale cache | No VFS cache at all |
| "source file being updated" | `rclone move` aborts mid-upload | `--min-age 5m` + `--ignore-times` avoids touching in-progress downloads |
| Disk fills | Mount stops accepting writes, corruption possible | Bare disk fills, cron still runs — just pause torrents |

### Setup Script

Create `/root/torrent/rclone-upload.sh`:

```bash
#!/bin/bash
# Phase 1: Copy completed files to cloud (won't fail on active downloads)
/usr/bin/rclone copy /root/torrent/downloads/ gdrive_personal:"VPS Torrents" \
  --min-age 5m \
  --ignore-times \
  --no-traverse \
  --transfers 2 \
  --drive-chunk-size 64M \
  --log-file /tmp/rclone_upload.log \
  --log-level INFO

# Phase 2: Delete local files confirmed on remote
/usr/bin/rclone delete /root/torrent/downloads/ \
  --min-age 5m
```

**CRITICAL**: Use absolute paths (`/usr/bin/rclone`, `/root/.config/rclone/rclone.conf`). Cron runs with a different `$PATH` and `$HOME`.

**CRITICAL**: Never use `rclone move` for active download directories — it aborts when file mod-time changes mid-upload. Use `rclone copy` + `rclone delete` separately.

### Cron Setup

```bash
cp /root/torrent/rclone-upload.sh ~/.hermes/scripts/rclone-upload.sh
chmod +x ~/.hermes/scripts/rclone-upload.sh
# Create cron via Hermes with no_agent=true (script IS the job, runs every 5 min)
```

### GDrive Limits Under Bare-Disk Pattern

- Shared rclone OAuth client: ~6 MB/s upload
- Dedicated Google Cloud OAuth client: 30-50 MB/s
- Set qBittorrent download limit to 20-30 MB/s to prevent local disk from filling faster than upload drains

### Consolidated Skills

This skill absorbs the following narrower siblings: `rclone-gdrive-vps-mount`, `rclone-gdrive-docker-mount`, `rclone-gdrive-qbittorrent`, `rclone-headless-mount`, `rclone-cloud-torrent-pipeline`, `torrent-cloud-pipeline`.

Support files: `scripts/rclone-upload.sh` (bare-disk upload script), `references/fuse-mount-pitfalls.md` (detailed FUSE failure modes).
