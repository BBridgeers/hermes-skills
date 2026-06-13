# Stale VFS Cache Mount Hang — Reproduction & Fix

## Symptom

`rclone mount ... --daemon` returns immediately (exit 0), process appears in `ps aux`, but:
- `/proc/mounts` shows NO rclone or FUSE entry for the mount point
- `ls /mount/path` shows the underlying directory (not the remote)
- `stat -f /mount/path` shows `ext2/ext3` filesystem, not `fuse.rclone`
- In debug logs: endless `RATE_LIMIT_EXCEEDED` and `Added virtual directory entry vAddFile` lines

The daemon is stuck reconciling a stale VFS cache against GDrive, and with rate limiting + many cached files, it never finishes the mount initialization.

## Reproduction

1. Have a previous rclone session that used `--vfs-cache-mode full` with many files (80+)
2. Kill rclone (or it crashes) leaving cache in `/root/.cache/rclone/vfs/`
3. Try to remount with `--vfs-cache-mode full` or even `--vfs-cache-mode writes`
4. Mount hangs during directory listing, never attaches FUSE

## Fix

```bash
# 1. Kill all rclone
pkill -9 rclone

# 2. Force unmount any stale FUSE
fusermount -uz /mount/path

# 3. Clear the VFS cache (DESTRUCTIVE — loses unuploaded data)
rm -rf /root/.cache/rclone/vfs /root/.cache/rclone/vfsMeta

# 4. Mount fresh — should complete within seconds
rclone mount gdrive_personal:"Remote Folder" /mount/path \
  --vfs-cache-mode writes \
  --allow-other \
  --daemon \
  --vfs-cache-max-size 18G \
  --transfers 2

# 5. Verify
cat /proc/mounts | grep rclone
# Should show: gdrive_personal:Remote\040Folder /mount/path fuse.rclone ...
```

## Why cache reconciliation is so slow

With `--vfs-cache-mode full`, rclone stores both data AND metadata locally. On remount, it:
1. Lists every cached file
2. For each file, queries GDrive API to compare fingerprints
3. Re-adds each file as a virtual directory entry

With 80+ files and GDrive rate limits (840k queries/min/project), each fingerprint check gets rate-limited with exponential backoff. At 1-2 seconds per file × 80 files = 80-160 seconds just for reconciliation. If rate limits are already exhausted from the mount itself, it takes even longer and may never complete within a reasonable timeout.

## Prevention

- Use `--vfs-cache-mode writes` instead of `full` unless you specifically need local read caching
- Use `--vfs-cache-max-age 1h` to auto-clean old cache entries
- Before unmounting, let uploads drain: check `rclone about` for stable "Used" size
