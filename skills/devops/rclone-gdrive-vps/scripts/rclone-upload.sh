#!/bin/bash
# rclone-upload.sh — Move completed torrent downloads to cloud storage
# Designed for cron deployment (every 5 min, no_agent=true)
#
# Flags:
#   --min-age 5m          Skip files still being written by torrent client
#   --delete-empty-src-dirs Clean up empty folders after move
#   --transfers 2         Limit concurrent uploads to avoid rate limits
#   --drive-chunk-size 64M Fewer API calls per large file
#
# Usage:
#   Set REMOTE_NAME and REMOTE_PATH below, then deploy via cron.
#   Local path is /root/torrent/downloads/ by default — change SRC below.

REMOTE_NAME="gdrive_personal"
REMOTE_PATH="VPS Torrents"
SRC="/root/torrent/downloads/"

/usr/bin/rclone move "$SRC" "${REMOTE_NAME}:${REMOTE_PATH}" \
  --min-age 5m \
  --delete-empty-src-dirs \
  --transfers 2 \
  --drive-chunk-size 64M \
  --log-file /tmp/rclone_upload.log \
  --log-level INFO \
  --stats 30s

# Summary for cron delivery
echo "=== $(date) ==="
echo "Remote used: $(/usr/bin/rclone about ${REMOTE_NAME}: 2>/dev/null | grep Used)"
echo "Local free: $(df -h "$SRC" | tail -1 | awk '{print $4}')"
echo "Files remaining: $(find "$SRC" -type f -mmin +5 | wc -l) ready for next upload"
