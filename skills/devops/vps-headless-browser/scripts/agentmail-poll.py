#!/usr/bin/env python3
"""Check AgentMail inbox for new LinkedIn message notifications.

Polls the AgentMail API for recent messages matching LinkedIn patterns.
Tracks last-seen timestamp in a state file to avoid duplicate alerts.
Designed to be run by a cron job every 5 minutes.

SETUP:
  1. API key from https://console.agentmail.to
  2. Inbox ID: your @agentmail.to email (e.g. dfwwebdesignnow@agentmail.to)
  3. Set AGENTMAIL_API_KEY + AGENTMAIL_INBOX_ID env vars, or edit defaults below
  4. User forwards LinkedIn emails from primary inbox → AgentMail inbox

API: https://api.agentmail.to/v0 — Bearer auth, no SDK needed.
Free tier: 3 inboxes, 3,000 emails/month.
"""

import json, os, sys, urllib.request, urllib.error

API_KEY = os.environ.get("AGENTMAIL_API_KEY", "AM_API_KEY_HERE")
INBOX_ID = os.environ.get("AGENTMAIL_INBOX_ID", "inbox@agentmail.to")
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".agentmail_state.json")

LINKEDIN_SIGNALS = [
    "linkedin", "inmail", "message from", "new message",
    "sent you a message", "connection request", "recruiter",
    "job application", "inmail from", "@linkedin.com",
    "messaging-noreply@linkedin.com", "messages-noreply@linkedin.com"
]

def api_get(path):
    req = urllib.request.Request(f"https://api.agentmail.to/v0{path}",
        headers={"Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f: return json.load(f)
    return {"last_ts": None}

def save_state(ts):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_ts": ts}, f)

def main():
    if API_KEY == "AM_API_KEY_HERE":
        print("ERROR: Set AGENTMAIL_API_KEY env var or edit script.")
        sys.exit(1)
    try:
        data = api_get(f"/inboxes/{INBOX_ID}/messages?limit=10&ascending=false")
    except urllib.error.HTTPError as e:
        print(f"API ERROR: {e.code}"); sys.exit(1)

    st = load_state()
    last_ts = st["last_ts"]
    msgs = data.get("messages", [])
    new_hits, newest = [], last_ts

    for m in msgs:
        ts = m.get("timestamp","")
        if last_ts and ts <= last_ts: continue
        if newest is None or ts > newest: newest = ts
        txt = f"{(m.get('subject')or'')} {(m.get('from')or'')} {(m.get('preview')or'')}".lower()
        if any(kw in txt for kw in LINKEDIN_SIGNALS):
            new_hits.append(m)

    if not new_hits:
        if newest and newest != last_ts: save_state(newest)
        print("No new LinkedIn messages.")
        return

    lines = ["*** NEW LINKEDIN MESSAGE ***", ""]
    for i, m in enumerate(new_hits, 1):
        lines.append(f"--- #{i} ---")
        lines.append(f"From: {m.get('from','?')}")
        lines.append(f"Subject: {m.get('subject','?')}")
        lines.append(f"Preview: {(m.get('preview') or '')[:200]}")
        lines.append("")
    lines.append("⚠️ REPLY NOW — slow responses cost opportunities!")
    print("\n".join(lines))
    if newest: save_state(newest)

if __name__ == "__main__":
    main()
