# Slack Gateway Diagnostics (Native & Docker)

## Socket Mode Failure — `apps.connections.open` Returns HTTP 200

**Symptom**: Gateway logs repeat:
```
ERROR slack_bolt.AsyncApp: Failed to retrieve WSS URL: The request to the Slack API failed.
(url: https://slack.com/api/apps.connections.open, status: 200)
```

**Root cause**: The App-Level Token (`xapp-...`) is valid (HTTP 200, not 401/403) but the Socket Mode session is stale — often because the app was reinstalled or the gateway was restarted without a clean session handoff.

**Fix**: Restart the gateway. Do NOT replace tokens.

```bash
systemctl --user restart hermes-gateway   # native
docker compose up -d hermes-agent          # Docker
```

## Diagnostic Pattern — Test Both Tokens Individually

Before assuming a token is bad, test each one independently:

```bash
# 1. Test Bot Token (xoxb-...)
curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" https://slack.com/api/auth.test
# Expected: {"ok":true,"team":"...","user":"hermes",...}

# 2. Test App Token (xapp-...) for Socket Mode
curl -s -H "Authorization: Bearer $SLACK_APP_TOKEN" -X POST \
  https://slack.com/api/apps.connections.open
# Expected: {"ok":true,"url":"wss://wss-primary.slack.com/..."}
```

| Auth test result | App test result | Action |
|---|---|---|
| `ok: true` | `ok: true` + WSS URL | **Restart gateway** — session stale, tokens fine |
| `ok: true` | `ok: false` / `invalid_auth` | App Token needs regeneration in Slack App Settings |
| `ok: false` / `invalid_auth` | `ok: true` | Bot Token needs regeneration (OAuth & Permissions page) |
| Both fail | Both fail | App likely deleted or tokens revoked — full re-setup needed |

## Bot Token `auth.test` vs App Token `apps.connections.open`

- **Bot Token** (`xoxb-...`): Used for REST API calls (sending messages, reading channels). Tested via `auth.test`.
- **App Token** (`xapp-...`): Used ONLY for Socket Mode WebSocket connections. Tested via `apps.connections.open`. Socket Mode is what Hermes uses — the App Token MUST have the `connections:write` scope.

These are generated in DIFFERENT sections of the Slack App dashboard:
- Bot Token: **OAuth & Permissions** → "Bot User OAuth Token"
- App Token: **Basic Information** → "App-Level Tokens"

Reinstalling the app regenerates the Bot Token but does NOT regenerate the App Token. If you reinstalled and Socket Mode broke, check the App Token.

## Native Install — Gateway Restart

```bash
systemctl --user restart hermes-gateway
journalctl --user -u hermes-gateway -f   # watch for Slack connection
```

After restart, confirm connectivity:
```bash
hermes gateway status    # should show active
```

To verify Slack is fully connected (not just gateway running), send a test message or check that Slack targets appear:
```bash
# From within Hermes session, or via terminal:
# send_message action=list should show slack:* targets
```

## OAuth Env Var Conflict — `SLACK_CLIENT_ID` Triggers Unwanted OAuth Mode

**Symptom**: Gateway logs show BOTH of these:
```
WARNING slack_bolt.AsyncApp: As `installation_store` or `authorize` has been used,
  `token` (or SLACK_BOT_TOKEN env variable) will be ignored.
ERROR slack_bolt.AsyncMultiTeamsAuthorization: Although the app should be installed
  into this workspace, the AuthorizeResult (returned value from authorize) for it was not found.
```

Despite having valid `SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN`, the Slack connection
fails to authorize. The gateway may still show as "running" but Slack messages
are not processed.

**Root cause**: `SLACK_CLIENT_ID` and `SLACK_CLIENT_SECRET` are set as environment
variables. In slack_bolt's `AsyncApp.__init__` (v1.27.0+, `async_app.py` lines
291–301), when both env vars are present AND no explicit `oauth_settings` was
passed, slack_bolt auto-creates an `AsyncOAuthSettings()` with a default
installation store. This triggers lines 341–343:
```python
if (self._async_installation_store is not None or self._async_authorize is not None) and self._token is not None:
    self._token = None  # bot token DISCARDED
```
Once the bot token is discarded, the gateway tries to use OAuth-based
authorization, but no OAuth installation data exists — the app was set up for
Socket Mode, not OAuth. The `AsyncMultiTeamsAuthorization` middleware then
rejects every incoming event because it can't find the workspace in the
(empty) installation store.

**Fix**: Comment out or remove these three env vars from `~/.hermes/.env`:
```
SLACK_CLIENT_ID
SLACK_CLIENT_SECRET
SLACK_SIGNING_SECRET     # also unnecessary for Socket Mode
```
Socket Mode only needs `SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN`. The OAuth
credentials are only needed if you're running an HTTP-based OAuth installation
flow (where Slack redirects users to your server to authorize).

After removing the vars, restart the gateway:
```bash
systemctl --user restart hermes-gateway
```

Verify with `tail -f ~/.hermes/logs/gateway.log` — you should see:
```
[Slack] Authenticated as @hermes in workspace ... (team: ...)
[Slack] Socket Mode connected (1 workspace(s))
✓ slack connected
```
and NO `AsyncMultiTeamsAuthorization` errors.

**Detection**: `grep 'SLACK_CLIENT_ID' ~/.hermes/.env` — if it returns a hit and
you're using Socket Mode, this is the culprit.
