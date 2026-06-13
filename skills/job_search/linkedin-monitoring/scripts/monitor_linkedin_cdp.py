#!/usr/bin/env python3
"""Monitor LinkedIn messages via Chrome DevTools Protocol.
Connects to the already-running Chromium browser on the VPS.
User can watch live at noVNC: http://100.78.50.1:6080/vnc.html
"""
import json
import os
import sys
import time
import urllib.request
from websocket import create_connection

CHROMIUM_HTTP = "http://localhost:9222"
STATE_FILE = "/root/workspace/job_search/.linkedin_cdp_state.json"

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
        "params": {
            "expression": expression,
            "returnByValue": True
        }
    })
    ws.send(msg)
    result = json.loads(ws.recv())
    if "result" in result and "result" in result["result"]:
        return result["result"]["result"].get("value")
    return None

def extract_messages():
    """Extract unread message info from LinkedIn messaging page."""
    tab = find_linkedin_tab()
    if not tab:
        return {"error": "LinkedIn tab not found. Is user logged in?"}
    
    ws_url = tab["webSocketDebuggerUrl"]
    ws = create_connection(ws_url, timeout=10)
    
    try:
        js = """
        (function() {
            let result = {unread_count: 0, unread_threads: [], current_url: location.href};
            
            let unreadBadge = document.querySelector('.msg-conversation-listitem--unread-badge, [data-unread-count]');
            if (unreadBadge) {
                let count = parseInt(unreadBadge.textContent) || 0;
                result.unread_count = count;
            }
            
            let conversations = document.querySelectorAll('.msg-conversations-container__conversations-list .msg-conversation-listitem');
            conversations.forEach(conv => {
                let name = conv.querySelector('.msg-conversation-card__participant-names, .msg-conversation-listitem__participant-names, .t-16.t-black.t-bold')?.textContent?.trim() || '';
                let preview = conv.querySelector('.msg-conversation-card__message-snippet, .msg-conversation-listitem__message-snippet-body')?.textContent?.trim() || '';
                let time = conv.querySelector('.msg-conversation-card__time-stamp, .msg-conversation-listitem__time-stamp, .conversation-insights__time')?.textContent?.trim() || '';
                let isUnread = conv.querySelector('[class*="unread"], .msg-conversation-card--unread') !== null;
                let link = conv.querySelector('a')?.getAttribute('href') || '';
                
                if (isUnread || name) {
                    result.unread_threads.push({name, preview, time, isUnread, link});
                }
            });
            
            if (result.unread_threads.length === 0) {
                let items = document.querySelectorAll('[data-conversation-url], [class*="conversation"]');
                items.forEach(item => {
                    let text = item.textContent?.trim()?.substring(0, 200) || '';
                    result.unread_threads.push({name: text, preview: '', time: '', isUnread: false, link: ''});
                });
            }
            
            let notifBadge = document.querySelector('.notification-badge__count, .nav-item__badge');
            if (notifBadge) {
                result.notification_count = parseInt(notifBadge.textContent) || 0;
            }
            
            return JSON.stringify(result);
        })()
        """
        
        raw = cdp_evaluate(ws, js)
        return json.loads(raw) if raw else {"error": "No data from LinkedIn"}
    finally:
        ws.close()

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
        tab = find_linkedin_tab()
        if not tab:
            sys.exit(1)
        return
    
    state = load_state()
    unread = data.get("unread_count", 0)
    threads = data.get("unread_threads", [])
    notifs = data.get("notification_count", 0)
    
    lines = []
    
    if unread > 0 or len(threads) > 0:
        lines.append(f"🔴 LINKEDIN: {unread} unread | {notifs} notifications")
        lines.append("")
        for i, t in enumerate(threads[:10], 1):
            name = t.get("name", "Unknown")[:60]
            preview = t.get("preview", "")[:100]
            time_str = t.get("time", "")
            unread_mark = "🔵" if t.get("isUnread") else "  "
            lines.append(f"{unread_mark} {name}")
            if preview:
                lines.append(f"   {preview}")
            if time_str:
                lines.append(f"   {time_str}")
            lines.append("")
        
        if not threads and unread > 0:
            lines.append("(Could not extract thread details — check live view)")
    else:
        lines.append(f"✅ LinkedIn: 0 unread | {notifs} notifications")
    
    old_threads = state.get("last_threads", [])
    new_names = {t.get("name", "") for t in threads} - {t.get("name", "") for t in old_threads}
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
