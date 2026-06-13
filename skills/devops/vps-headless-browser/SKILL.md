---
name: vps-headless-browser
description: Visible, interactable Chromium on a headless VPS — Xvfb + noVNC for user watching/interacting + CDP remote debugging for agent control. Use when the user wants to SEE and CLICK in a browser running on the VPS, or when headless automation hits CAPTCHA/2FA/bot walls.
---

# VPS Headless Browser (Visible + CDP)

Full stack for a real Chromium browser on a headless VPS that the user can **watch and interact with** via noVNC while the agent controls it via CDP.

## When to Use

- User says "I can't see what you're doing" or wants to click/interact with the browser
- **PREFERRED over built-in browser tools (browser_navigate/browser_snapshot) for ANY site with login, CAPTCHA, 2FA, or bot detection** — the user MUST be able to see and aid in bypassing auth walls
- Sites with aggressive bot detection (LinkedIn, Facebook, banking portals, etc.)
- User wants a persistent logged-in browser session on the VPS
- Any time the built-in headless tools hit a block — fall back to this immediately rather than fighting

## Companion: AgentMail Polling

For sites where browser automation isn't possible (LinkedIn inbox, etc.), use the email-forwarding + AgentMail polling pattern instead. The script at `scripts/agentmail-poll.py` monitors an AgentMail inbox for forwarded notification emails. Deploy it as a cron job:

```bash
# Create cron job to poll every 5 minutes
cronjob action=create name="inbox-monitor" schedule="every 5 min" \
  prompt="Run scripts/agentmail-poll.py and display output. If 'No new messages', respond quietly." \
  workdir="/path/to/workspace"
```

**Setup**: User forwards notification emails from their primary inbox (Outlook, Gmail) to an AgentMail inbox. The script polls the AgentMail API and alerts on matching keywords.

## Architecture

```
User's Laptop                    VPS
┌─────────────┐                 ┌──────────────────────────────┐
│  Browser     │    noVNC (6080) │  websockify → x11vnc → Xvfb │
│  (watching)  │◄───────────────│         :99 display          │
│              │     Tailscale   │              ▲               │
│              │                 │       Chromium (DISPLAY=:99) │
└─────────────┘                 │        CDP port 9222         │
                                │              ▲               │
                                │         Agent (localhost)    │
                                └──────────────────────────────┘
```

## Installation

```bash
apt-get update -qq && apt-get install -y -qq \
  chromium-browser xvfb x11vnc novnc websockify xdg-utils
```

## Launch Sequence

Execute in this order. Each step must succeed before the next.

### 1. Xvfb (virtual display)

```bash
Xvfb :99 -screen 0 1280x900x24 &
```

### 2. x11vnc (VNC server on the virtual display)

```bash
x11vnc -display :99 -forever -nopw -quiet -rfbport 5900 &
```

### 3. websockify (noVNC bridge — VNC → HTTP)

```bash
websockify --web /usr/share/novnc 6080 localhost:5900 &
```

### 4. Chromium (on virtual display, CDP enabled)

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
  --restore-last-session \
  <target-url> &
```

**Flag notes:**
- `--remote-allow-origins="*"` — **MANDATORY** for CDP WebSocket connections from scripts. Without it, `websocket-client` gets `403 Forbidden` with `Rejected an incoming WebSocket connection from the <origin> origin`.
- `--restore-last-session` — Survives Chromium crashes/restarts. Reopens tabs the user had open.

## Access

| Role | URL / Port | Notes |
|------|-----------|-------|
| **User watches/clicks** | `http://<vps-tailscale-ip>:6080/vnc.html` | Open in any browser. Tailscale bypasses cloud firewalls. |
| **Agent controls** | `http://localhost:9222` | CDP. Tabs at `/json`, WebSocket at tab's `webSocketDebuggerUrl` |

## Verifying It Works

```bash
# Check processes
ps aux | grep -E "Xvfb|x11vnc|websockify|chromium" | grep -v grep

# Check ports
ss -tlnp | grep -E "5900|6080|9222"

# Verify CDP
curl -s http://localhost:9222/json/version
```

## Pitfalls

- **`--no-sandbox` required** when running as root. Without it Chromium crashes with `Running as root without --no-sandbox is not supported`.
- **`--remote-allow-origins="*"` required** for CDP WebSocket automation. Without it, Python scripts using `websocket-client` get `403 Forbidden` — `Rejected an incoming WebSocket connection from the <origin> origin`. The flag allows WebSocket connections from non-browser origins.
- **`xdg-utils` required** or Chromium spams `xdg-settings: not found` and may fail silently.
- **`--disable-gpu`** avoids GPU rendering errors on VPS without a real GPU.
- **Hostinger cloud firewall**: Port 6080 must be opened in Hostinger panel AND UFW. Tailscale bypasses this — user can access via Tailscale IP without opening ports.
- **Xvfb must start first** — Chromium needs the DISPLAY to exist before launching.
- **Persistent sessions**: If Chromium crashes, restart from step 4. The user's cookies/sessions persist in the Chromium profile directory. Use `--restore-last-session` to auto-restore tabs.
- **Multiple Chromium instances**: Can conflict. Check `ps aux | grep chromium` before launching.
- **Backgrounding in terminal tool**: The terminal tool rejects `&` in foreground mode. Use `terminal(background=true)` for Chromium launch. For Xvfb/x11vnc/websockify, you can chain them in one background call since they're daemons.

## CDP Quick Reference

```python
import json, urllib.request

# List tabs
tabs = json.loads(urllib.request.urlopen("http://localhost:9222/json").read())

# Find a specific tab
for t in tabs:
    if "linkedin.com" in t.get("url", ""):
        ws_url = t["webSocketDebuggerUrl"]
        # Use ws_url with a WebSocket library to send CDP commands
```

## Security

- x11vnc runs with `-nopw` (no password). Only safe because it's bound to localhost and accessed via websockify which proxies locally. Do NOT expose port 5900 to the internet.
- noVNC on 6080: accessible via Tailscale mesh only (recommended) or open to internet via firewall rules (less secure).

## CDP Monitoring Script Pattern

When building a polling script that checks a page via CDP (LinkedIn messages, dashboards, etc.), use this pattern:

```python
import json, urllib.request, time
from websocket import create_connection

# Find the target tab
tabs = json.loads(urllib.request.urlopen("http://localhost:9222/json").read())
target = next((t for t in tabs if "target-domain.com" in t.get("url", "")), None)

if not target:
    print("Tab not found")
    sys.exit(1)

# Connect via WebSocket and run JS
ws = create_connection(target["webSocketDebuggerUrl"], timeout=10)
ws.send(json.dumps({
    "id": 1,
    "method": "Runtime.evaluate",
    "params": {"expression": "document.title", "returnByValue": True}
}))
result = json.loads(ws.recv())
data = result["result"]["result"].get("value")
ws.close()
```

**State tracking**: Save last-seen message IDs/timestamps to a JSON file. Compare on each poll. Only alert on new items.

**Cron deployment**: Use `cronjob action=create` with `enabled_toolsets=["terminal"]` and `workdir` pointing to the script's directory. 5-minute intervals recommended for inbox/messaging monitoring.

See `scripts/monitor-linkedin-cdp.py` for a complete working example that extracts LinkedIn messaging unread counts and thread previews.