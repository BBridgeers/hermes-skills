---
name: linkedin-automation
description: Monitor and respond to LinkedIn messages via headless Chromium + noVNC + CDP. Sets up visible browser on VPS that user can watch and interact with to bypass CAPTCHAs and 2FA.
---

# LinkedIn Automation

Headless Chromium on VPS with noVNC for visual oversight. User watches live and can click/interact. Agent controls via Chrome DevTools Protocol (CDP) WebSocket. Used for monitoring LinkedIn messages and drafting responses.

## When to Use

- User needs LinkedIn message monitoring (recruiter inbox)
- User wants to SEE what the agent is doing (no blind automation)
- User needs to help bypass CAPTCHAs, 2FA, or login walls
- User wants draft-review-send workflow for LinkedIn responses

## Prerequisites

```bash
apt-get install -y chromium-browser xvfb x11vnc novnc websockify xdg-utils
pip install --break-system-packages websocket-client
```

## Setup

### 1. Start Xvfb + VNC + noVNC

```bash
Xvfb :99 -screen 0 1280x900x24 &
x11vnc -display :99 -forever -nopw -quiet -rfbport 5900 &
websockify --web /usr/share/novnc 6080 localhost:5900 &
```

### 2. Launch Chromium with CDP

```bash
DISPLAY=:99 chromium-browser \
  --remote-debugging-port=9222 \
  --remote-allow-origins="*" \
  --no-first-run \
  --no-default-browser-check \
  --no-sandbox \
  --disable-gpu \
  --window-size=1280,900 \
  --disable-blink-features=AutomationControlled \
  https://www.linkedin.com/messaging &
```

### 3. User watches at

`http://<vps-ip>:6080/vnc.html` (over Tailscale: `http://100.78.50.1:6080/vnc.html`)

## CDP Control

The agent controls Chromium via WebSocket at `ws://localhost:9222/devtools/page/<page-id>`.

**Find LinkedIn tab:**
```python
import json, urllib.request
with urllib.request.urlopen("http://localhost:9222/json") as r:
    tabs = json.loads(r.read())
linkedin = [t for t in tabs if "linkedin.com/messaging" in t.get("url", "")]
```

**Execute JavaScript in page:**
```python
from websocket import create_connection
ws = create_connection(tab["webSocketDebuggerUrl"], timeout=10)
msg = json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": js_code, "returnByValue": True}})
ws.send(msg)
result = json.loads(ws.recv())
ws.close()
```

**Take screenshot:**
```python
msg = json.dumps({"id": 1, "method": "Page.captureScreenshot", "params": {"format": "png"}})
ws.send(msg)
# result["result"]["data"] is base64 PNG
```

## LinkedIn DOM Notes

- **Sidebar duplicates entries** — same conversation appears 5-6 times in `querySelectorAll('.msg-conversation-listitem')`. Deduplicate by name or use the first match.
- **Names are often abbreviated** — "R P" instead of full name. User can see full names via noVNC. Ask user if DOM returns initials.
- **"Other" tab is hard to reach** — TreeWalker and querySelector often fail. `document.body.innerText` works but "Other" text may be in shadow DOM. Use screenshot + user interaction as fallback.
- **innerText is reliable** — `document.body.innerText` gives a clean text dump of the entire messaging page for finding messages that aren't in the current DOM view.
- **Selectors to try (in order):**
  1. `.msg-conversation-listitem` — sidebar items
  2. `.msg-s-message-list` — current thread messages
  3. `document.body.innerText` — full page text dump

## Message Response Protocol (CRITICAL)

**NEVER send a message without user approval.** The workflow is:

1. **Alert only** — cron job detects new messages, reports them to user
2. **Draft** — agent drafts a response, user reviews
3. **Revise** — user provides feedback on tone, language, content
4. **Approve** — user explicitly says to send
5. **Execute** — agent sends via CDP or user sends manually

**When drafting LinkedIn messages:**
- Do NOT include phone number or email in the draft body — it's in the user's LinkedIn signature
- Keep drafts concise and direct
- Match the user's casual-but-professional tone
- Always apologize briefly for late replies if the message is more than 3 days old

## Cron Job for Monitoring

Use a Python script that:
1. Connects to existing Chromium via CDP
2. Runs `document.body.innerText` to get full page content
3. Extracts conversation names, previews, timestamps
4. Compares against state file (`.linkedin_cdp_state.json`) to detect new messages
5. Reports new conversations to user

Script reference: `scripts/monitor_linkedin_cdp.py`

## Pitfalls

- **Chromium must run as root** — needs `--no-sandbox` flag
- **WebSocket origin check** — needs `--remote-allow-origins="*"` flag
- **`websocket-client` package required** — `pip install --break-system-packages websocket-client`
- **State file dedup** — state tracking prevents false "NEW MESSAGE" alerts after first run
- **Browser crashes on exit** — Chromium may leave zombie processes; use `pkill -f chromium-browser` before restarting
- **Firewall** — noVNC port 6080 needs Hostinger cloud firewall AND UFW opened. Tailscale bypasses cloud firewall.
