# LinkedIn CDP Monitoring Setup

Connects to a visible Chromium browser on VPS via Chrome DevTools Protocol. User can watch via noVNC and interact to bypass CAPTCHAs / 2FA.

## Stack
- **Xvfb** — Virtual framebuffer on display :99
- **Chromium** — Browser with `--remote-debugging-port=9222 --remote-allow-origins=*`
- **x11vnc** — Shares display :99 on port 5900
- **noVNC** — Web VNC viewer on port 6080
- **CDP** — Python/websocket scripts connect to `ws://localhost:9222/devtools/page/...`

## Launch Sequence
```bash
# 1. Virtual display
Xvfb :99 -screen 0 1280x900x24 &

# 2. VNC bridge
x11vnc -display :99 -forever -nopw -quiet -rfbport 5900 &

# 3. Web viewer (user opens this)
websockify --web /usr/share/novnc 6080 localhost:5900 &

# 4. Browser with remote debugging
DISPLAY=:99 chromium-browser \
  --remote-debugging-port=9222 \
  --remote-allow-origins="*" \
  --no-sandbox --disable-gpu \
  --window-size=1280,900 \
  --disable-blink-features=AutomationControlled \
  --restore-last-session &
```

## User Access
- **Watch live:** `http://100.78.50.1:6080/vnc.html` (Tailscale)
- User can see everything, click, type, help with CAPTCHAs and 2FA

## Monitoring Script
- `monitor_linkedin_cdp.py` — Connects via websocket to Chromium CDP, runs JS to extract unread messages
- Cron job polls every 5 min
- State file tracks last-seen timestamps to detect new messages

## Pitfalls
- Chromium MUST have `--remote-allow-origins=*` or CDP WebSocket is rejected (403)
- Must use `--no-sandbox` when running as root
- Browser session persists with `--restore-last-session`
- If VPS reboots, all 4 processes must restart
