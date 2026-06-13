# Workspace Model Picker Auth Debugging

## How the Workspace Resolves Models

The workspace (port 3100) `/api/models` route (`src/routes/api/models.ts`) merges
from three sources in order:

```
1. models.json (local file, PRIMARY)          — 100+ user-configured models
2. Gateway /v1/models (if gateway supports it) — current provider's models
3. Local discovery (Ollama, etc.)              — locally-running models
```

The `/api/model/info` route determines runtime switching capability — when
the dashboard returns no model-info payload, the workspace falls back to gateway
capabilities, which is just the default provider's models. This is the
`[model-info] falling back to gateway capabilities` log line.

## Auth Middleware Trace

File: `src/server/auth-middleware.ts`

```typescript
export function isAuthenticated(request: Request): boolean {
  // No password configured? No auth needed — ALL requests pass
  if (!isPasswordProtectionEnabled()) {
    return true
  }
  // Otherwise check for valid claude-auth cookie
  const cookieHeader = request.headers.get('cookie')
  const token = getSessionTokenFromCookie(cookieHeader)
  if (!token) return false
  return isValidSessionToken(token)
}
```

`isPasswordProtectionEnabled()` checks `HERMES_PASSWORD` then `CLAUDE_PASSWORD` env vars.

Session tokens are 32-byte hex strings stored in `/root/.hermes/workspace-sessions.json`
with 30-day TTL. The cookie name is `claude-auth`.

## Debugging Workflow

When the model picker shows too few models:

1. **Check models.json is populated:**
   ```bash
   python3 -c "import json; print(len(json.load(open('/root/.hermes/models.json'))))"
   ```
   Should be 100+. If not, run the sync script.

2. **Check workspace logs for fallback:**
   ```bash
   journalctl --user -u hermes-workspace --no-pager -n 30 | grep 'model-info'
   ```
   If you see `falling back to gateway capabilities`, the auth path is broken.

3. **Query /api/models directly:**
   ```bash
   # Find valid token
   cat /root/.hermes/workspace-sessions.json | python3 -c "import sys,json; t=list(json.load(sys.stdin)['tokens'].keys())[-1]; print(t)"
   
   # Query with token
   curl -s http://localhost:3100/api/models -H "Cookie: claude-auth=<TOKEN>"
   ```

4. **Check service environment:**
   ```bash
   systemctl --user cat hermes-workspace | grep -i pass
   ```
   If `HERMES_PASSWORD` is set, the UI needs authentication.

5. **Gateway vs workspace:**
   - Gateway `/v1/models` (port 8642) only returns current provider's models
   - Workspace `/api/models` (port 3100) returns the full merged catalog
   - Dashboard `/api/models` (port 9119) returns "Unauthorized" — not the model source

## Session Token File Format

`/root/.hermes/workspace-sessions.json`:
```json
{
  "tokens": {
    "<32-byte-hex>": <expiry-unix-ms>,
    ...
  }
}
```

Tokens are auto-generated on workspace login. The file is written with 0600 permissions.
