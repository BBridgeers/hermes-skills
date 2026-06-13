---
name: linkedin-monitoring
description: Monitor LinkedIn messages in real-time using a visible Chromium browser on VPS with CDP control. User can watch via noVNC and help bypass CAPTCHA/2FA. Extracts unread messages, detects new ones, alerts user. Alert-only mode — never auto-respond.
---

# LinkedIn Message Monitoring

Visible Chromium browser on VPS with CDP control + noVNC watch. User sees everything and can interact to bypass auth walls. Polls every 5 minutes for new messages.

## When to Use

- Monitoring LinkedIn for new recruiter/connection messages
- Any site with login, CAPTCHA, or 2FA that headless browsers can't handle
- User wants to SEE what the agent is doing and help with auth

## Architecture

```
Chromium (DISPLAY=:99)  ←── CDP ws://localhost:9222  ←── Python monitor script
        ↓
   Xvfb :99  ←── x11vnc :5900  ←── websockify :6080  ←── user's browser (noVNC)
```

## Stack Components

| Component | Port | Purpose |
|-----------|------|---------|
| Xvfb | :99 (display) | Virtual framebuffer |
| Chromium | 9222 (CDP) | Browser with remote debugging |
| x11vnc | 5900 | VNC server for Xvfb |
| websockify/noVNC | 6080 | Web-based VNC viewer |

## Quick Start (if stack is down)

```bash
# 1. Start display + VNC
Xvfb :99 -screen 0 1280x900x24 &
x11vnc -display :99 -forever -nopw -quiet -rfbport 5900 &
websockify --web /usr/share/novnc 6080 localhost:5900 &

# 2. Start Chromium (must have these flags)
DISPLAY=:99 chromium-browser \
  --remote-debugging-port=9222 \
  --remote-allow-origins="*" \
  --no-sandbox \
  --disable-gpu \
  --no-first-run \
  --no-default-browser-check \
  --window-size=1280,900 \
  --disable-blink-features=AutomationControlled \
  --restore-last-session &

# 3. Verify
curl -s http://localhost:9222/json/version | grep Browser
```

## Monitoring Script

`/root/workspace/job_search/monitor_linkedin_cdp.py`

- Connects to Chromium via CDP WebSocket
- Finds LinkedIn messaging tab
- Runs JS to extract unread message threads
- Tracks seen state in `/.linkedin_cdp_state.json`
- Reports new messages with "🚨 NEW MESSAGE(S)!" header
- Prints live view URL

## Cron Job

`bef1d45a146f` — runs every 5 minutes, delivers to origin (WebUI).

## Credentials Management

**Never type LinkedIn credentials via CDP.** User must log in manually via noVNC. After login, Chromium maintains session. Use `--restore-last-session` to survive restarts.

## DOM Notes

LinkedIn messaging DOM is complex and uses shadow DOM heavily. Key observations:
- `document.querySelectorAll` often fails on messaging elements (shadow DOM isolation)
- `document.body.innerText` works for broad text extraction
- `document.createTreeWalker` with `NodeFilter.SHOW_ELEMENT` can walk all elements
- "Other" tab for non-connection messages may not appear in standard DOM queries
- Screen coordinates approach may be needed for clicking into non-standard elements

## User Preferences

**ALERT-ONLY. NEVER auto-respond.** Workflow:
1. Cron detects new message → alerts user
2. User + agent discuss response: tone, verbiage, feel
3. Agent drafts response
4. User approves
5. Agent sends via CDP

**All draft responses must include:**
- Cell: (682) 300-6828
- Email: blake.bridgers2@outlook.com
- Encouragement to text for faster call coordination

## Pitfalls

- Chromium must have `--remote-allow-origins="*"` or CDP WebSocket rejects connections (403 Forbidden)
- Running as root requires `--no-sandbox`
- LinkedIn may log out after extended idle — check tab URL before trying to extract
- If Chromium crashes, Xvfb/x11vnc/websockify stay running; just restart Chromium with `--restore-last-session`
- **Restart**: `pkill -f chromium-browser` then relaunch with same flags
- **Sidebar deduplication**: LinkedIn DOM duplicates entries 5-6×. Dedupe by name+timestamp, not count
- **"Other" tab**: Non-connection messages land here. May need coordinate clicks or user assist via noVNC
- **Name abbreviations**: Recruiter initials (e.g. "R P") shown in DOM; full names in message signature
- **State file**: Track `last_threads` by name set, not count, to detect actual new conversations
- **noVNC port 6080**: Hostinger firewall blocks by default. Tailscale IP bypasses

## Verification

```bash
# Is Chromium running?
curl -s http://localhost:9222/json | python3 -c "import json,sys; print(len(json.load(sys.stdin)),'tabs')"

# Is LinkedIn tab loaded?
curl -s http://localhost:9222/json | python3 -c "import json,sys; [print(t['title'][:60]) for t in json.load(sys.stdin) if 'linkedin' in t.get('url','')]"

# Run monitor
python3 /root/workspace/job_search/monitor_linkedin_cdp.py
```

## Dependencies

- chromium-browser, xvfb, x11vnc, novnc, websockify (apt)
- websocket-client (pip)
- Python 3.10+

## Linked Files

- `references/response-templates.md` — Recruiter response templates with contact info
- `scripts/monitor_linkedin_cdp.py` — CDP-based LinkedIn message extractor
