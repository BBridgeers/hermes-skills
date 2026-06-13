#!/usr/bin/env python3
"""Monitor LinkedIn messages via Chrome DevTools Protocol.
Connects to already-running Chromium browser on VPS.
User watches live at noVNC: http://100.78.50.1:6080/vnc.html

Usage: python3 monitor_linkedin_cdp.py
Output: prints unread message summary to stdout
State: saved to .linkedin_cdp_state.json in working directory
"""
import json
import os
import sys
import time
import urllib.request
from websocket import create_connection

CHROMIUM_HTTP = "http://localhost:9222"
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".linkedin_cdp_state.json")


def find_linkedin_tab():
    """Find the LinkedIn messaging tab."""
    with urllib.request.urlopen(f"{CHROMIUM_HTTP}/json") as r:
        tabs = json.loads(r.read())
    for t in tabs:
        url = t.get("url", "")
        if "linkedin.com/messaging" in url:
            return t
    return None


def cdp_evaluate(ws, expression):
    """Run JS in the page and return the result."""
    msg = json.dumps({
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {"expression": expression, "returnByValue": True}
    })
    ws.send(msg)
    result = json.loads(ws.recv())
    if "result" in result and "result" in result["result"]:
        return result["result"]["result"].get("value")
    return None


def extract_messages():
    """Extract conversation list from LinkedIn messaging page."""
    tab = find_linkedin_tab()
    if not tab:
        return {"error": "LinkedIn tab not found. Chromium may need restart."}

    ws_url = tab["webSocketDebuggerUrl"]
    ws = create_connection(ws_url, timeout=10)

    try:
        # Use innerText for reliable extraction (avoids DOM duplication issues)
        js = "document.body.innerText"
        raw = cdp_evaluate(ws, js)
    finally:
        ws.close()

    if not raw:
        return {"error": "No data from LinkedIn"}

    # Parse the text dump to extract conversations
    lines = raw.split("\n")
    conversations = []
    current = None
    linkedin_keywords = ["inmail", "message", "sent", "opportunity", "job", "hire", "position", "role"]

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Skip navigation/UI chrome
        if line in ("Home", "My Network", "Jobs", "Messaging", "Notifications", "Me",
                     "Focused", "Other", "Search messages", "Compose a new message"):
            # "Other" with "new messages" is useful
            if "new message" in line.lower():
                conversations.append({"name": line, "preview": "", "time": "", "isUnread": True, "link": ""})
            continue

        # Check for date patterns (e.g., "May 20", "Apr 8", "Mar 27")
        if len(line) <= 8 and any(m in line for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
            if current:
                current["time"] = line
            continue

        # Check if this looks like a name (short, capitalized first letter, no common words)
        words = line.split()
        if (2 <= len(words) <= 3 and
            all(w[0].isupper() for w in words if w[0].isalpha()) and
            not any(kw in line.lower() for kw in ["new", "you", "the", "and", "for", "view", "status"])):
            if current:
                conversations.append(current)
            current = {"name": line, "preview": "", "time": "", "isUnread": False, "link": ""}
            continue

        # Message preview - check for recruiter keywords
        if current and any(kw in line.lower() for kw in linkedin_keywords):
            current["preview"] = line
            current["isUnread"] = True

    if current and current.get("name"):
        conversations.append(current)

    # Deduplicate
    seen = set()
    unique = []
    for c in conversations:
        key = c.get("name", "")
        if key and key not in seen:
            seen.add(key)
            unique.append(c)

    # Count unread
    unread_count = sum(1 for c in unique if c.get("isUnread"))

    return {
        "unread_count": unread_count,
        "threads": unique,
        "notification_count": 0
    }


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_threads": [], "last_check": None}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def main():
    data = extract_messages()

    if "error" in data:
        print(f"⚠️ {data['error']}")
        sys.exit(1)

    state = load_state()
    unread = data.get("unread_count", 0)
    threads = data.get("threads", [])

    lines = []

    if unread > 0:
        lines.append(f"🔴 LINKEDIN: {unread} unread messages")
        lines.append("")
        for t in threads:
            if t.get("isUnread"):
                name = t.get("name", "?")[:60]
                preview = t.get("preview", "")[:120]
                time_str = t.get("time", "")
                lines.append(f"🔵 {name}")
                if preview:
                    lines.append(f"   {preview}")
                if time_str:
                    lines.append(f"   {time_str}")
                lines.append("")
    else:
        lines.append("✅ LinkedIn: no new messages.")

    # Detect new threads
    old_names = {t.get("name", "") for t in state.get("last_threads", [])}
    new_names = {t.get("name", "") for t in threads} - old_names
    if new_names:
        lines.insert(0, "🚨 NEW MESSAGE(S)! 🚨")

    save_state({
        "last_threads": threads,
        "last_check": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "unread_count": unread
    })

    print("\n".join(lines))
    print(f"\n👁️ Live view: http://100.78.50.1:6080/vnc.html")


if __name__ == "__main__":
    main()
