#!/bin/bash
# Hybrid rename: YYYY-MM-DD Subject-Slug -- IG-SHORTCODE
# Extracts date + shortcode + caption from .md OCR files, slugs caption into folder name.
# Usage: cd {account}_posts && bash hybrid_rename.sh [--dry-run] [--apply]
#
# --dry-run (default): preview renames, no changes
# --apply: execute rclone moveto on Drive

set -euo pipefail

DRY_RUN=true
ACCOUNT="${ACCOUNT:-theaethervault}"  # override via env

for arg in "$@"; do
    case "$arg" in
        --apply) DRY_RUN=false ;;
        --dry-run) DRY_RUN=true ;;
        *) ACCOUNT="$arg" ;;
    esac
done

DRIVE_BASE="gdrive_personal:Instagram_Scrapes/${ACCOUNT}/slides"

for md in *.md; do
    dir="${md%.md}_slides"
    [ ! -d "$dir" ] && continue

    shortcode=$(head -1 "$md" | sed 's/^# //' | tr -d '\r\n')
    date=$(grep -m1 "Date" "$md" | grep -oP '\d{4}-\d{2}-\d{2}' || echo "unknown-date")
    caption=$(sed -n '/^## Caption/{n;n;p}' "$md" | head -1 | tr -d '\r\n')

    # Slug: strip punctuation, first 6 words, lowercase, hyphenated
    slug=$(echo "$caption" | tr -c '[:alnum:] ' ' ' | tr -s ' ' | \
            cut -d' ' -f1-6 | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
    slug="${slug#-}"   # strip leading hyphen
    slug="${slug%-}"   # strip trailing hyphen
    [ -z "$slug" ] && slug="untitled"

    new_name="${date} ${slug} -- ${shortcode}"

    if $DRY_RUN; then
        echo "DRY RUN: ${dir} → ${new_name}"
    else
        echo "RENAMING: ${dir} → ${new_name}"
        rclone moveto "${DRIVE_BASE}/${dir}" "${DRIVE_BASE}/${new_name}" -P
    fi
done
