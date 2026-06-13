---
name: visible-headless-browser
description: Set up a visible Chromium browser on a headless VPS using Xvfb + x11vnc + noVNC. User can watch and interact via web browser while you control via CDP. Use when automation hits bot walls (LinkedIn, CAPTCHAs, 2FA) and the user needs to see and click.
version: 1.0.0
---

# Visible Headless Browser

When a headless VPS needs a browser the user can SEE and CLICK on — for bypassing bot detection, CAPTCHAs, 2FA, LinkedIn, or any site that blocks headless automation.

## When to Use
- LinkedIn automation (aggressive bot detection)
- Sites with CAPTCHAs or 2FA the user must solve
- The user wants to watch what you're doing in real-time
- CDP control needed while keeping the user in the loop

## Setup (One-Time)

```bash
apt-get update && apt-get install -y chromium-browser xvfb x11vnc novnc websockify xdg-utils
```

## Launch Sequence

```bash
# 1. Start virtual display
Xvfb :99 -screen 0 1280x900x24 &
sleep 1

# 2. Start VNC server on the virtual display
x11vnc -display :99 -forever -nopw -quiet -rfbport 5900 &
sleep 2

# 3. Start noVNC web interface (port 6080)
websockify --web /usr/share/novnc 6080 localhost:5900 &
sleep 1

# 4. Launch Chromium on the virtual display with remote debugging
DISPLAY=:99 chromium-browser \
  --remote-debugging-port=9222 \
  --remote-allow-origins="*" \
  --no-first-run \
  --no-default-browser-check \
  --no-sandbox \
  --disable-gpu \
  --window-size=1280,900 \
  --disable-blink-features=AutomationControlled \
  https://TARGET_URL &
```

## Access
- **User watches:** `http://<tailscale-ip>:6080/vnc.html` (via Tailscale mesh — bypasses cloud firewall)
- **CDP control:** `http://localhost:9222/json` — connect via WebSocket for JS execution, clicks, navigation

## CDP Control Pattern (Python)

```python
import json, urllib.request
from websocket import create_connection

# Find the target tab
with urllib.request.urlopen("http://localhost:9222/json") as r:
    tabs = json.loads(r.read())

tab = next(t for t in tabs if "target-site.com" in t.get("url", ""))

# Connect WebSocket and evaluate JS
ws = create_connection(tab["webSocketDebuggerUrl"], timeout=15)
msg = json.dumps({
    "id": 1,
    "method": "Runtime.evaluate",
    "params": {"expression": "document.title", "returnByValue": True}
})
ws.send(msg)
result = json.loads(ws.recv())
ws.close()
```

## Persistence
For reboot survival, add all 4 processes to systemd services. The Chromium process uses `--restore-last-session` to maintain login state.

## Pitfalls
- Chromium needs `--no-sandbox` when running as root
- WebSocket connections rejected without `--remote-allow-origins="*"`
- Tailscale IP access bypasses Hostinger cloud firewall — no panel config needed
- Port 6080 only needs to be open on the Tailscale interface, not public internet
- LinkedIn DOM is heavily obfuscated — standard querySelector often fails. Fall back to `document.body.innerText` for text extraction, or coordinate-based clicks via screenshot analysis.
