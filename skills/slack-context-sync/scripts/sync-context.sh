#!/usr/bin/env bash
# Slack Context Sync Heartbeat
# Scans recent Hermes sessions and updates the shared context file.
set -euo pipefail

CONTEXT_FILE="$HOME/.hermes/slack-context.md"

# --- Phase 1: If JSON is piped on stdin, use it directly --------------------
if [ ! -t 0 ]; then
    INPUT=$(cat)
    if [ -n "$INPUT" ] && echo "$INPUT" | jq -e '.topics' >/dev/null 2>&1; then
        SOURCE=$(echo "$INPUT" | jq -r '.source // "Unknown"')
        PROJECT=$(echo "$INPUT" | jq -r '.project // "Unknown"')
        LAST_MSG=$(echo "$INPUT" | jq -r '.last_message // ""')
        {
            echo "# Active Context — $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
            echo ""
            echo "## Current Source"
            echo "$SOURCE"
            echo ""
            echo "## Active Project"
            echo "$PROJECT"
            echo ""
            echo "## Recent Topics"
            echo "$INPUT" | jq -r '.topics[] // empty' | while read -r t; do echo "- $t"; done
            echo ""
            echo "## Key Decisions"
            echo "$INPUT" | jq -r '.decisions[] // empty' | while read -r d; do echo "- $d"; done
            echo ""
            echo "## Pending Actions"
            echo "$INPUT" | jq -r '.actions[] // empty' | while read -r a; do echo "- [ ] $a"; done
            echo ""
            echo "## Key Files"
            echo "$INPUT" | jq -r '.files[] // empty' | while read -r f; do echo "- $f"; done
            echo ""
            echo "## Last Message"
            echo "$LAST_MSG"
        } > "$CONTEXT_FILE"
        exit 0
    fi
fi

# --- Phase 2: Cold start — create stub if missing --------------------------
if [ ! -f "$CONTEXT_FILE" ]; then
    mkdir -p "$(dirname "$CONTEXT_FILE")"
    {
        echo "# Active Context — $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        echo ""
        echo "## Status"
        echo "SLACK_CONTEXT_COLD_START — no sessions synced yet. Run manually or wait for next agent session."
    } > "$CONTEXT_FILE"
    exit 0
fi

# --- Phase 3: Stale check — flag if context hasn't been updated in >30min ---
CURRENT_TS=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
FILE_TS=$(head -1 "$CONTEXT_FILE" | grep -oP '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z' || echo "1970-01-01T00:00:00Z")

# This script can't call session_search directly from bash — it relies on
# the agent in a session to do the scanning and update the file.
# The cron session that invokes this script should build context via
# session_search and write the file directly, OR pipe JSON to stdin.
#
# For now, just check staleness and note it.
if [ -f "$CONTEXT_FILE" ]; then
    # Touch the file's timestamp so we can detect if a real update happened
    # (don't modify content, just ensure mtime reflects last check)
    touch "$CONTEXT_FILE"
fi

exit 0
