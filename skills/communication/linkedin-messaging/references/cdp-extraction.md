# LinkedIn CDP Message Extraction

## Full extraction script pattern

```python
#!/usr/bin/env python3
"""Monitor LinkedIn messages via Chrome DevTools Protocol."""
import json, os, sys, time, urllib.request
from websocket import create_connection

CHROMIUM_HTTP = "http://localhost:9222"
STATE_FILE = "/root/workspace/job_search/.linkedin_cdp_state.json"

def find_linkedin_tab():
    with urllib.request.urlopen(f"{CHROMIUM_HTTP}/json") as r:
        tabs = json.loads(r.read())
    for t in tabs:
        if "linkedin.com/messaging" in t.get("url", ""):
            return t
    return None

def cdp_evaluate(ws, expression):
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
    tab = find_linkedin_tab()
    if not tab:
        return {"error": "LinkedIn tab not found"}
    
    ws = create_connection(tab["webSocketDebuggerUrl"], timeout=10)
    
    js = """
    (function() {
        let result = {unread_count: 0, threads: [], notification_count: 0};
        
        // Get sidebar conversations
        let items = document.querySelectorAll('.msg-conversation-listitem, [class*="conversation-card"]');
        items.forEach(conv => {
            let name = conv.querySelector('[class*="participant-names"], [class*="name"] span')?.textContent?.trim() || '';
            let preview = conv.querySelector('[class*="message-snippet"], [class*="snippet"]')?.textContent?.trim() || '';
            let time = conv.querySelector('[class*="time-stamp"], time')?.textContent?.trim() || '';
            let isUnread = !!conv.querySelector('[class*="unread"]');
            let link = conv.querySelector('a[href*="/messaging/thread/"]')?.getAttribute('href') || '';
            
            if (name) {
                result.threads.push({name, preview, time, isUnread, link});
            }
        });
        
        // Notification count
        let badge = document.querySelector('.notification-badge__count, .nav-item__badge');
        if (badge) result.notification_count = parseInt(badge.textContent) || 0;
        
        return JSON.stringify(result);
    })()
    """
    
    try:
        raw = cdp_evaluate(ws, js)
        ws.close()
        return json.loads(raw) if raw else {"error": "No data"}
    finally:
        ws.close()
```

## Known selectors (LinkedIn UI changes frequently)

- Conversation items: `.msg-conversation-listitem`, `[class*="conversation-card"]`
- Participant names: `[class*="participant-names"]`, `[class*="name"] span`, `.t-16.t-black.t-bold`
- Message preview: `[class*="message-snippet"]`, `[class*="snippet"]`
- Timestamp: `[class*="time-stamp"]`, `time`
- Unread indicator: `[class*="unread"]`
- Thread link: `a[href*="/messaging/thread/"]`

## Fallback: Full page text dump

When selectors fail, use `document.body.innerText` to get all visible text and parse manually.
