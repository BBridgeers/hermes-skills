#!/usr/bin/env python3
"""
Extract token usage from Hermes session files into a CSV for cost-report.

Reads ~/.hermes/sessions/ (both .json and .jsonl files) and builds
token-usage.csv with columns: date, skill, model, input_tokens, output_tokens,
cache_read, cache_creation, source

Two strategies:
  1. Direct extraction: if session messages contain usage/usage_metadata blocks
     with input_tokens/output_tokens, use those directly. Source = "provider".
  2. Heuristic estimation: count characters in user/system messages for input,
     assistant messages for output, divide by 4. Source = "estimated".
"""

import argparse
import csv
import json
import os
import sys
import glob
from datetime import datetime, timedelta

HERMES_HOME = os.path.expanduser("~/.hermes")
SESSIONS_DIR = os.path.join(HERMES_HOME, "sessions")
DATA_DIR = os.path.join(HERMES_HOME, "data")

# Maximum date range to scan
MAX_DAYS_BACK = 365


def extract_usage_from_session(filepath: str) -> list[dict]:
    """Parse one session file and return list of usage rows."""
    rows = []

    try:
        # Determine file type
        if filepath.endswith(".jsonl"):
            with open(filepath) as f:
                lines = f.readlines()
        elif filepath.endswith(".json"):
            with open(filepath) as f:
                data = json.load(f)
            # session JSON has a messages array
            messages = data.get("messages", [])
            if not messages:
                return rows
            rows = _parse_messages(messages, data)
            return rows
        else:
            return rows

        # Parse JSONL
        # JSONL files have one JSON object per line
        messages = []
        session_meta = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get("role") == "session_meta":
                    session_meta = obj
                else:
                    messages.append(obj)
            except json.JSONDecodeError:
                continue

        if not messages:
            return rows

        rows = _parse_messages(messages, session_meta)
    except Exception:
        return rows

    return rows


def _parse_messages(messages: list[dict], session_meta: dict) -> list[dict]:
    """Extract usage rows from a list of messages."""
    rows = []
    model = session_meta.get("model", "unknown")
    if isinstance(session_meta, dict) and not model:
        model = "unknown"

    # Try to find session date
    session_date = None
    # Check session_meta / messages for timestamps
    if isinstance(session_meta, dict):
        for key in ("session_start", "timestamp", "created_at"):
            val = session_meta.get(key)
            if val:
                try:
                    session_date = val[:10]  # YYYY-MM-DD
                    break
                except Exception:
                    pass
    if not session_date:
        for msg in messages:
            ts = msg.get("timestamp", "")
            if ts:
                try:
                    session_date = ts[:10]
                    break
                except Exception:
                    pass
    if not session_date:
        return rows  # Can't date this session

    # Strategy 1: Look for explicit usage data in messages
    total_input = 0
    total_output = 0
    total_cache_read = 0
    total_cache_write = 0
    found_usage = False

    for msg in messages:
        # Provider usage data may be in 'usage' or 'usage_metadata' field
        usage = msg.get("usage") or msg.get("usage_metadata") or msg.get("token_usage")
        if usage and isinstance(usage, dict):
            found_usage = True
            total_input += int(usage.get("input_tokens") or usage.get("prompt_tokens") or 0)
            total_output += int(usage.get("output_tokens") or usage.get("completion_tokens") or 0)
            details = usage.get("prompt_tokens_details") or {}
            total_cache_read += int(details.get("cached_tokens") or 0)
            total_cache_write += int(details.get("cache_creation_input_tokens") or 0)

    if found_usage and (total_input > 0 or total_output > 0):
        # Try to infer skill from first user message
        skill = _infer_skill(messages)
        rows.append({
            "date": session_date,
            "skill": skill,
            "model": model,
            "input_tokens": total_input,
            "output_tokens": total_output,
            "cache_read": total_cache_read,
            "cache_creation": total_cache_write,
            "source": "provider",
        })
        return rows

    # Strategy 2: Heuristic estimation from message lengths
    input_chars = 0
    output_chars = 0
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if isinstance(content, list):
            # Multi-part content — sum text parts
            content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
        if not isinstance(content, str):
            continue
        if role in ("user", "system", "tool"):
            input_chars += len(content)
        elif role == "assistant":
            output_chars += len(content)

    if input_chars > 0 or output_chars > 0:
        skill = _infer_skill(messages)
        rows.append({
            "date": session_date,
            "skill": skill,
            "model": model,
            "input_tokens": max(1, input_chars // 4),
            "output_tokens": max(1, output_chars // 4),
            "cache_read": 0,
            "cache_creation": 0,
            "source": "estimated",
        })

    return rows


def _infer_skill(messages: list[dict]) -> str:
    """Heuristically infer which skill was used from the first user message."""
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if not isinstance(content, str):
                content = ""
            content_lower = content.lower()

            # Look for explicit skill references
            skill_keywords = {
                "code review": "code-review",
                "review this": "code-review",
                "pr workflow": "github-pr-workflow",
                "pull request": "github-pr-workflow",
                "github issue": "github-issues",
                "cost report": "cost-report",
                "architecture diagram": "architecture-diagram",
                "browser": "browser-harness",
                "spotify": "spotify",
                "minecraft": "minecraft-modpack-server",
                "pdf": "ocr-and-documents",
                "powerpoint": "powerpoint",
                "pptx": "powerpoint",
                "arxiv": "arxiv",
                "youtube": "youtube-content",
                "skill health": "skill-health",
                "heartbeat": "hermes-heartbeat",
                "test": "test-driven-development",
                "debug": "systematic-debugging",
                "plan": "plan",
                "email": "himalaya",
                "notion": "notion",
                "linear": "linear",
                "memory": "obsidian",
                "gif": "gif-search",
                "ascii": "ascii-art",
                "pixel art": "pixel-art",
                "fine-tun": "fine-tuning-with-trl",
                "huggingface": "huggingface-hub",
                "deepseek": "deepseek-direct",
                "twitter": "xurl",
                "x.com": "xurl",
            }
            for keyword, skill in skill_keywords.items():
                if keyword in content_lower:
                    return skill

            # Check for context patterns
            if "cost" in content_lower and "report" in content_lower:
                return "cost-report"
            if "fix" in content_lower or "bug" in content_lower:
                return "systematic-debugging"
            if "implement" in content_lower or "feature" in content_lower:
                return "test-driven-development"

            return "general-chat"
    return "uncategorized"


def main():
    parser = argparse.ArgumentParser(
        description="Extract token usage from Hermes session files"
    )
    parser.add_argument(
        "--days", type=int, default=7,
        help="Number of days of history to extract (default: 7)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output CSV path (default: ~/.hermes/data/token-usage.csv)"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Extract all available history (ignores --days)"
    )
    args = parser.parse_args()

    output_path = args.output or os.path.join(DATA_DIR, "token-usage.csv")

    if not os.path.isdir(SESSIONS_DIR):
        print(f"COST_REPORT_SKIP: no sessions directory at {SESSIONS_DIR}", file=sys.stderr)
        sys.exit(1)

    cutoff_date = None
    if not args.all:
        cutoff_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    # Collect all session files
    all_files = sorted(
        glob.glob(os.path.join(SESSIONS_DIR, "*.json"))
        + glob.glob(os.path.join(SESSIONS_DIR, "*.jsonl")),
        key=os.path.getmtime,
        reverse=True,
    )

    all_rows = []
    seen_dates = set()  # Track unique session dates to avoid duplicates

    for filepath in all_files:
        filename = os.path.basename(filepath)
        # Skip non-session files
        if filename in ("sessions.json", "channel_directory.json"):
            continue
        # Skip .json files that have a matching .jsonl (prefer .jsonl)
        if filename.endswith(".json"):
            jsonl_path = filepath.replace(".json", ".jsonl")
            if os.path.exists(jsonl_path):
                continue  # Skip, we'll read the .jsonl version

        rows = extract_usage_from_session(filepath)
        for row in rows:
            if row["date"] and row["date"] not in seen_dates:
                if cutoff_date is None or row["date"] >= cutoff_date:
                    all_rows.append(row)
                # Track seen even if outside window to prevent duplicates
                seen_dates.add(row["date"])

    # Also read session_*.json files that contain full message arrays
    # (these are session metadata files with embedded messages)
    session_meta_files = sorted(
        glob.glob(os.path.join(SESSIONS_DIR, "session_*.json")),
        key=os.path.getmtime,
        reverse=True,
    )
    for filepath in session_meta_files:
        filename = os.path.basename(filepath)
        session_id = filename.replace("session_", "").replace(".json", "")
        # Skip if we already have a .jsonl for this session
        jsonl_path = os.path.join(SESSIONS_DIR, f"{session_id}.jsonl")
        if os.path.exists(jsonl_path):
            continue
        rows = extract_usage_from_session(filepath)
        for row in rows:
            if row["date"] and row["date"] not in seen_dates:
                if cutoff_date is None or row["date"] >= cutoff_date:
                    all_rows.append(row)
                seen_dates.add(row["date"])

    if not all_rows:
        print(f"COST_REPORT_WARN: no usage data found in sessions", file=sys.stderr)
        # Still write an empty CSV with headers
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "date", "skill", "model", "input_tokens", "output_tokens",
                "cache_read", "cache_creation", "source"
            ])
            writer.writeheader()
        print(f"Empty CSV written to {output_path}")
        return

    # Sort by date
    all_rows.sort(key=lambda r: r["date"])

    # Write CSV
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "date", "skill", "model", "input_tokens", "output_tokens",
            "cache_read", "cache_creation", "source"
        ])
        writer.writeheader()
        writer.writerows(all_rows)

    provider_count = sum(1 for r in all_rows if r.get("source") == "provider")
    estimated_count = sum(1 for r in all_rows if r.get("source") == "estimated")
    print(
        f"Extracted {len(all_rows)} rows "
        f"(provider: {provider_count}, estimated: {estimated_count}) "
        f"→ {output_path}"
    )


if __name__ == "__main__":
    main()
