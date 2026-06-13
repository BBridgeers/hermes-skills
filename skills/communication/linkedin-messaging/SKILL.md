---
name: linkedin-messaging
description: Monitor and respond to LinkedIn messages via a visible Chromium browser on the VPS. Covers CDP-based message extraction, noVNC for user visibility, and draft-response workflows with mandatory user approval.
version: 1.0.0
---

# LinkedIn Messaging (CDP + visible browser)

## When to Use

- User needs to monitor LinkedIn messages for recruiter outreach
- User wants to draft and send responses to LinkedIn messages
- User wants to see the browser live and interact to bypass CAPTCHAs/2FA

## Critical Rule: NEVER SEND WITHOUT APPROVAL

**The agent MUST NOT send any LinkedIn message or response without explicit user approval.** The workflow is:

1. Agent detects new messages → alerts user
2. Agent and user discuss tone, content, approach
3. Agent drafts response → user reviews and approves
4. Agent sends via CDP

This applies to ALL LinkedIn communications — messages, InMails, connection requests, everything.

## Draft Guidelines

- Messages should be concise and direct — not robotic
- Do NOT include the user's contact info (phone, email) in drafts unless the user explicitly asks for it. The user's LinkedIn profile and message signature already contain this information.
- Draft tone should match the user's voice: professional but casual, not stiff or corporate
- Include a "sorry for the delay" when responding to old messages (>1 week)

## Prerequisites

On the VPS:
```bash
apt-get install -y chromium-browser xvfb x11vnc novnc websockify xdg-utils
pip install --break-system-packages websocket-client
```

## Setup: Start the Visible Browser

### 1. Start Xvfb, VNC, and noVNC

```bash
# Start Xvfb on display :99
Xvfb :99 -screen 0 1280x900x24 &
sleep 1

# Start x11vnc
x11vnc -display :99 -forever -nopw -quiet -rfbport 5900 &
sleep 2

# Start noVNC (serves VNC via HTTP)
websockify --web /usr/share/novnc 6080 localhost:5900 &
```

User accesses at: `http://<vps-tailscale-ip>:6080/vnc.html`

### 2. Start Chromium

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
  --restore-last-session &
```

### 3. Verify

```bash
curl -s http://localhost:9222/json/version | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('Browser','NO'))"
```

## Message Extraction via CDP

Reference: `references/cdp-extraction.md` for the full Python extraction script pattern.

The extraction uses `websocket-client` to connect to the Chromium DevTools Protocol WebSocket, then runs `Runtime.evaluate` with JavaScript to extract sidebar conversations and message bodies.

### Finding the LinkedIn tab

```python
import json, urllib.request
with urllib.request.urlopen("http://localhost:9222/json") as r:
    tabs = json.loads(r.read())
linkedin_tab = [t for t in tabs if "linkedin.com/messaging" in t.get("url","")][0]
ws_url = linkedin_tab["webSocketDebuggerUrl"]
```

### Extracting messages

Connect via `create_connection(ws_url)` from `websocket` module, then send a `Runtime.evaluate` command with JavaScript that queries the LinkedIn DOM for conversation list items, their names, previews, timestamps, and unread status.

## Monitoring Cron Job

Create a 5-minute cron job that runs the CDP monitor script and alerts on new messages:

```
cronjob action=create name=linkedin-cdp-monitor schedule="every 5 min"
  prompt="Run the LinkedIn CDP monitor. Alert on new messages. Do NOT send any responses."
  delivery=origin
```

## Pitfalls

- **Chromium must be running** — if the VPS reboots, restart Xvfb + VNC + Chromium
- **Origin check**: Chromium needs `--remote-allow-origins="*"` or WebSocket connections from non-browser origins are rejected with 403
- **Sandbox**: Running as root requires `--no-sandbox`
- **LinkedIn session expiry**: The browser session will eventually expire. User needs to re-login via noVNC.
- **DOM selectors change**: LinkedIn updates their UI frequently. If extraction breaks, use noVNC to visually inspect the current DOM structure and update selectors.
- **"Other" tab**: LinkedIn has Focused/Other tabs for messages. Non-connection messages go to Other. The extraction script may need to click into the Other tab.
