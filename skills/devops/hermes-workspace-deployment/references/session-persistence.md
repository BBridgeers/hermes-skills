# Session Persistence Architecture - Implementation

## Problem Solved

User reported: "I don't have to like fucking put something in every fucking time I want the session to stay open do I"

**Answer**: NO - sessions should persist automatically across tab switches and browser restarts.

## Root Cause

The workspace was using `sessionStorage.removeItem()` and `sessionStorage.getItem()` instead of `localStorage` equivalents. The `sessionStorage` API is tab-scoped - it clears automatically when the tab closes or switches.

**Expected**: Sessions survive tab switches, browser restarts, workspace restarts
**Actual (before fix)**: Sessions lost on tab switch

## Solution: Three-Layer Fix

### Layer 1: Gateway Heartbeat Endpoint (Already Existed, Was Broken)

**Endpoint**: `GET /api/session/heartbeat?key=<session_key>`

**Fixed** (api_server.py line 922):
- Changed from `gateway_runner._session_db.list_sessions()` (method doesn't exist in `hermes_state.SessionDB`)
- To `gateway_runner._session_db.list_sessions_rich()` (correct method, returns dict list)

**Returns**:
```json
{
  "active": true,
  "session_key": "abc123",
  "session_id": "xyz789",
  "created_at": 1234567890.123,
  "last_message_at": 1234567900.456,
  "message_count": 42
}
```

### Layer 2: Workspace Recovery Functions

Added to `src/lib/gateway-api.ts`:

```typescript
// TTL for localStorage (60 min) - prevents disk bloat
const SESSION_TTL_MS = 60 * 60 * 1000

export async function checkSessionHeartbeat(sessionKey: string): Promise<{
  active: boolean
  sessionKey?: string
  error?: string
} | null> {
  try {
    const response = await fetch(makeEndpoint(`/api/session/heartbeat?key=${encodeURIComponent(sessionKey)}`))
    if (!response.ok) return null
    return await response.json()
  } catch {
    return null
  }
}

export function setLocalSessionMetadata(sessionKey: string, lastSeen: number): void {
  if (typeof localStorage === 'undefined') return
  try {
    localStorage.setItem(`session_meta_${sessionKey}`, JSON.stringify({ key: sessionKey, lastSeen }))
  } catch {
    // Ignore errors (private mode, etc.)
  }
}

export async function reconnectOrphanedSessions(sessions: Array<GatewaySession>): Promise<void> {
  for (const session of sessions) {
    const heartbeat = await checkSessionHeartbeat(session.sessionKey)
    if (heartbeat?.active) {
      setLocalSessionMetadata(session.sessionKey, Date.now())
    } else if (heartbeat && !heartbeat.active) {
      if (typeof localStorage !== 'undefined') {
        try { localStorage.removeItem(`session_meta_${session.sessionKey}`) } catch {}
      }
    }
  }
}

export function cleanupStaleSessionMetadata(): void {
  if (typeof localStorage === 'undefined') return
  const now = Date.now()
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key?.startsWith('session_meta_')) {
        const raw = localStorage.getItem(key)
        if (raw) {
          try {
            const parsed = JSON.parse(raw)
            if (parsed.lastSeen && now - parsed.lastSeen > SESSION_TTL_MS) {
              localStorage.removeItem(key)
            }
          } catch { localStorage.removeItem(key) }
        }
      }
    }
  } catch {}
}
```

### Layer 3: React Query Hook Integration

Added to `src/screens/chat/hooks/use-chat-sessions.ts`:

```typescript
// Session recovery on startup and periodic refresh
useEffect(() => {
  if (sessionsQuery.data) {
    // Reconnect orphaned sessions (check gateway via heartbeat)
    reconnectOrphanedSessions(sessionsQuery.data as any).catch(() => {
      // Silently fail - this is just cleanup, not critical
    })
  }
}, [sessionsQuery.data])
```

## Architecture Flow

```
1. Workspace opens or sessions refetch every 5s
   ↓
2. fetchSessions() → /api/sessions (gateway returns all active sessions)
   ↓
3. useEffect fires → reconnectOrphanedSessions(sessions)
   ↓
4. For each session:
   - checkSessionHeartbeat(sessionKey) → /api/session/heartbeat?key=<key>
   - If active: setLocalSessionMetadata(sessionKey, Date.now())
   - If inactive: remove localStorage metadata
   ↓
5. localStorage now contains only valid gateway sessions
   ↓
6. Every 60 minutes: cleanupStaleSessionMetadata() removes old entries
```

## Files Modified

| File | Changes |
|------|---------|
| `hermes-agent/gateway/platforms/api_server.py` | Fixed heartbeat handler to use `list_sessions_rich()` with dict access |
| `hermes-workspace/src/lib/gateway-api.ts` | Added 5 session recovery functions with TTL cleanup |
| `hermes-workspace/src/screens/chat/hooks/use-chat-sessions.ts` | Added useEffect to call recovery on session fetch |
| `hermes-workspace/src/stores/chat-store.ts` | Changed from sessionStorage to localStorage (not shown - was done in previous fix) |

## How to Verify

```bash
# Check heartbeat endpoint works
curl -s "http://127.0.0.1:8642/api/session/heartbeat?key=main"
# Should return 404 for non-existent session, not 500 error

# Verify localStorage has session metadata (in browser console)
localStorage.getItem('session_meta_main')

# Test tab switch persistence
# 1. Open workspace with active session
# 2. Switch to another tab and back
# 3. Session should still be available
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Heartbeat returns 404 | Gateway not running or route not registered | Restart gateway |
| Heartbeat returns 500 | Wrong SessionDB class used | Use `list_sessions_rich()` instead of `list_sessions()` |
| Sessions not reconnecting | Network error, endpoint unreachable | Check browser console, verify `/api/session/heartbeat` accessible |
| localStorage not persisting | Browser settings, private mode | Check browser settings |

## SessionDB Classes Reference

| Class | Location | Purpose | Key Methods |
|-------|----------|---------|-------------|
| `gateway.session.SessionDB` | `gateway/session.py` | Gateway-specific session storage | `list_sessions()`, `get_transcript_path()` |
| `hermes_state.SessionDB` | `hermes_state.py` | State database (FTS5 search, metadata) | `list_sessions_rich()`, `create_session()`, `append_message()` |

**Gateway's `_session_db`**: Uses `hermes_state.SessionDB`

**Fix**: Use `list_sessions_rich()` which returns dicts, not `list_sessions()` which doesn't exist in `hermes_state.SessionDB`.