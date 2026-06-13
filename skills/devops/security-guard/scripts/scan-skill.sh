#!/usr/bin/env bash
set -euo pipefail

# scan-skill.sh — Security scanner for Hermes SKILL.md files
# Adapted from Aeon's skill-security-scan/scan.sh
#
# Usage:
#   ./scripts/scan-skill.sh <path-to-SKILL.md>
#   ./scripts/scan-skill.sh skills/devops/hermes-heartbeat/SKILL.md
#   ./scripts/scan-skill.sh --all              # Scan all Hermes skills
#   ./scripts/scan-skill.sh --all --json        # JSON output
#
# Exit codes:
#   0 = PASS (no HIGH findings)
#   1 = FAIL (HIGH severity findings detected)
#   2 = Usage error

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="${SKILLS_DIR:-$HOME/.hermes/skills}"

# Colors
if [[ -t 1 ]]; then
  RED='\033[0;31m'; YELLOW='\033[0;33m'; GREEN='\033[0;32m'; NC='\033[0m'
else
  RED=''; YELLOW=''; GREEN=''; NC=''
fi

JSON_OUTPUT=false
SCAN_ALL=false
FILES=()

usage() {
  sed -n '4,12p' "$0" | sed 's/^# //'
  exit 2
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) SCAN_ALL=true; shift ;;
    --json) JSON_OUTPUT=true; shift ;;
    --help|-h) usage ;;
    -*) echo "Unknown option: $1" >&2; usage ;;
    *) FILES+=("$1"); shift ;;
  esac
done

if [[ "$SCAN_ALL" == "true" ]]; then
  while IFS= read -r f; do
    FILES+=("$f")
  done < <(find "$SKILLS_DIR" -maxdepth 3 -name "SKILL.md" -type f 2>/dev/null | sort)
fi

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No files to scan. Use --all or specify paths." >&2
  usage
fi

# --- Pattern definitions (same as security-guard/references/injection-patterns.md) ---

HIGH_PATTERNS=(
  'eval\s' 'eval\(' '`[^`]*\$' '\$\([^)]*\$'
  'curl.*\$[A-Z_]' 'wget.*\$[A-Z_]' 'curl.*\$\{' 'wget.*\$\{'
  'curl.*--data.*secret' 'curl.*--data.*token' 'curl.*--data.*password' 'curl.*--data.*api.key'
  'printenv.*\|.*curl' 'printenv.*\|.*wget' 'env\s.*\|.*curl' 'cat.*/proc/.*environ'
  '\$TELEGRAM_BOT_TOKEN' '\$DISCORD_BOT_TOKEN' '\$SLACK_BOT_TOKEN'
  '\$GITHUB_TOKEN.*curl' '\$GITHUB_TOKEN.*wget'
  '\$OPENROUTER_API_KEY' '\$ANTHROPIC_API_KEY' '\$DEEPSEEK_API_KEY'
  '[Ii]gnore\s+(all\s+)?previous\s+instructions' '[Ii]gnore\s+(all\s+)?prior\s+instructions'
  '[Yy]ou\s+are\s+now\s+' '[Ff]orget\s+(all\s+)?(your\s+)?instructions'
  '[Dd]isregard\s+(all\s+)?previous' '[Oo]verride\s+(all\s+)?rules'
  'rm\s+-rf\s+/' 'rm\s+-rf\s+\*' 'rm\s+-rf\s+~'
  'mkfs\.' 'dd\s+if=.*of=/dev/' ':(){.*};:'
  'git\s+push\s+--force\s+origin\s+main' 'git\s+push\s+-f\s+origin\s+main'
)

MEDIUM_PATTERNS=(
  '\.\./\.\.' '/etc/passwd' '/etc/shadow' '~/.ssh' '~/.gnupg' '~/.aws' '~/.config'
  'curl\s+http://' 'wget\s+http://'
  'chmod\s+777' 'chmod\s+-R\s+777'
  'git\s+push\s+--force' 'git\s+push\s+-f\b' 'git\s+reset\s+--hard' 'git\s+clean\s+-fd'
  'base64\s+-d' 'base64\s+--decode'
  'kill\s+-9' 'killall' 'pkill'
)

LOW_PATTERNS=(
  'find\s+/\s' 'cat\s+/etc/' 'tee\s+/\s' '>\s+/'
)

# --- Scanner ---

TOTAL_PASS=0; TOTAL_WARN=0; TOTAL_FAIL=0

scan_file() {
  local file="$1"
  local skill_name; skill_name=$(basename "$(dirname "$file")")
  local dir_name; dir_name=$(basename "$(dirname "$(dirname "$file")")")
  local label="${dir_name}/${skill_name}"

  if [[ ! -f "$file" ]]; then
    echo -e "${RED}ERROR${NC}: File not found: $file" >&2
    return 1
  fi

  local highs=(); local mediums=(); local lows=()

  for pattern in "${HIGH_PATTERNS[@]}"; do
    local matches; matches=$(grep -nE "$pattern" "$file" 2>/dev/null || true)
    if [[ -n "$matches" ]]; then
      while IFS= read -r match; do
        local line_num="${match%%:*}"; local line_content="${match#*:}"; line_content="${line_content:0:100}"
        highs+=("L${line_num}: ${line_content}")
      done <<< "$matches"
    fi
  done

  for pattern in "${MEDIUM_PATTERNS[@]}"; do
    local matches; matches=$(grep -nE "$pattern" "$file" 2>/dev/null || true)
    if [[ -n "$matches" ]]; then
      while IFS= read -r match; do
        local line_num="${match%%:*}"; local line_content="${match#*:}"; line_content="${line_content:0:100}"
        mediums+=("L${line_num}: ${line_content}")
      done <<< "$matches"
    fi
  done

  for pattern in "${LOW_PATTERNS[@]}"; do
    local matches; matches=$(grep -nE "$pattern" "$file" 2>/dev/null || true)
    if [[ -n "$matches" ]]; then
      while IFS= read -r match; do
        local line_num="${match%%:*}"; local line_content="${match#*:}"; line_content="${line_content:0:100}"
        lows+=("L${line_num}: ${line_content}")
      done <<< "$matches"
    fi
  done

  local status="PASS"
  if [[ ${#highs[@]} -gt 0 ]]; then status="FAIL"; TOTAL_FAIL=$((TOTAL_FAIL + 1))
  elif [[ ${#mediums[@]} -gt 0 ]]; then status="WARN"; TOTAL_WARN=$((TOTAL_WARN + 1))
  else TOTAL_PASS=$((TOTAL_PASS + 1)); fi

  if [[ "$JSON_OUTPUT" == "true" ]]; then
    local json_highs; json_highs=$(printf '%s\n' "${highs[@]}" | jq -R -s 'split("\n") | map(select(length > 0))' 2>/dev/null || echo '[]')
    local json_mediums; json_mediums=$(printf '%s\n' "${mediums[@]}" | jq -R -s 'split("\n") | map(select(length > 0))' 2>/dev/null || echo '[]')
    local json_lows; json_lows=$(printf '%s\n' "${lows[@]}" | jq -R -s 'split("\n") | map(select(length > 0))' 2>/dev/null || echo '[]')
    jq -n --arg skill "$label" --arg status "$status" --arg file "$file" \
      --argjson high "$json_highs" --argjson medium "$json_mediums" --argjson low "$json_lows" \
      '{skill: $skill, status: $status, file: $file, high: $high, medium: $medium, low: $low}'
  else
    case "$status" in
      FAIL) echo -e "${RED}[FAIL]${NC} $label" ;;
      WARN) echo -e "${YELLOW}[WARN]${NC} $label" ;;
      PASS) echo -e "${GREEN}[PASS]${NC} $label" ;;
    esac
    for h in "${highs[@]}"; do echo -e "  ${RED}HIGH${NC}: $h"; done
    for m in "${mediums[@]}"; do echo -e "  ${YELLOW}MED${NC}: $m"; done
    for l in "${lows[@]}"; do echo -e "  ${GREEN}LOW${NC}: $l"; done
  fi
}

echo "Hermes Skill Security Scanner"
echo "=============================="
echo "Scanning ${#FILES[@]} file(s)..."
echo ""

for file in "${FILES[@]}"; do
  scan_file "$file"
done

echo ""
echo "=============================="
TOTAL=$((TOTAL_PASS + TOTAL_WARN + TOTAL_FAIL))
echo "Scanned: $TOTAL | Pass: $TOTAL_PASS | Warn: $TOTAL_WARN | Fail: $TOTAL_FAIL"

if [[ $TOTAL_FAIL -gt 0 ]]; then exit 1; fi
exit 0
