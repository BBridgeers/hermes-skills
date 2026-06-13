---
name: hermes-gateway-platform-install
description: Add a new messaging platform (Discord, SMS, etc.) to Hermes gateway Docker stack — env vars, port exposure, dependency management, Discord intent/permissions pitfalls, and teardown.
---

# Hermes Gateway Platform Install (Docker)

Use when: adding a new gateway platform that requires a Python dependency not
in the upstream `nousresearch/hermes-agent` image (e.g. `aiohttp` for SMS/Twilio).

## Platform: Discord

### Auto-enable
Discord auto-enables when `DISCORD_BOT_TOKEN` is set in the `.env`. No port
exposure needed — Discord uses outbound websocket, not inbound webhooks.
`discord.py` is bundled in the Docker image, so no dependency install needed.

### Env vars
```
DISCORD_BOT_TOKEN=<token from Discord Developer Portal>
DISCORD_ALLOWED_USERS=<comma-separated user IDs, optional>
```

### Discord Bot setup (user steps)
1. https://discord.com/developers/applications → New Application
2. Bot page → Reset Token (copy for DISCORD_BOT_TOKEN)
3. **CRITICAL**: Enable MESSAGE CONTENT INTENT under "Privileged Gateway Intents"
   - Without this: `discord connect timed out after 30s` — Discord's gateway
     rejects connections that request message content without this intent.
4. OAuth2 → URL Generator → check `bot` scope
5. Permissions needed (under Text Permissions):
   - View Channels (General section — this IS the "Read Messages" permission)
   - Send Messages
   - Read Message History
   "Read Messages" as a separate permission does NOT exist in Discord's OAuth2
   UI — users will look for it and not find it. Direct them to "View Channels"
   under General Permissions instead.
   Permissions integer: 68608 (1024 + 2048 + 65536)
6. Open the generated URL → select server → authorize
7. User must also create a Discord server if they don't have one (click + in
   left sidebar → Create My Own)

### Connection flow
- Initial connect may fail if the bot isn't in a server yet or intents are off
- Gateway has a built-in reconnection watcher: retries every 30s up to 20 attempts
- Watch the log: `tail -f gateway.log | grep discord`
- Successful connect: `[Discord] Connected as BOT_NAME#1234`
- After connect: `[Discord] Safely reconciled N slash command(s)`
- `/skill list` slash command is registered automatically with all loaded skills

### Troubleshooting
- **`discord connect timed out after 30s`** → Message Content Intent NOT enabled.
  User must go to Bot page and toggle it ON, then gateway auto-retries.
- **User can't find "Read Messages" permission** → It doesn't exist. It's called
  "View Channels" under General Permissions at the top of the list.
- **No server in dropdown** → User hasn't created a Discord server yet.
- **Bot connects but messages ignored** → Message Content Intent still off,
  or bot doesn't have View Channels permission.
- **Token in screenshot** → Regenerate it after setup is complete. The token is
  visible in screenshots shared during setup.

## Platform: SMS (Twilio)

Many platforms are already coded in `/opt/hermes/gateway/platforms/` inside the
container. The config auto-enables them when their required env vars are present.
Check `gateway/config.py` for the trigger vars (e.g. `TWILIO_ACCOUNT_SID` for SMS).

SMS auto-enables when `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` are set AND
`aiohttp` is importable. No gateway config.yaml changes needed — platform
discovery is env-var-driven. Required env vars:

```
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX          # E.164 format, required for outbound
SMS_WEBHOOK_URL=https://your-domain/webhooks/twilio  # public URL Twilio POSTs to
SMS_ALLOWED_USERS=+1XXXXXXXXXX           # comma-separated, lock down inbound
SMS_HOME_CHANNEL=+1XXXXXXXXXX            # for cron/heartbeat delivery (optional)
```

Optional env vars:
```
SMS_WEBHOOK_PORT=8080                    # default 8080
SMS_WEBHOOK_HOST=127.0.0.1              # default 127.0.0.1
SMS_ALLOW_ALL_USERS=true                 # open to anyone (unsafe)
SMS_INSECURE_NO_SIGNATURE=true           # skip Twilio signature validation (dev only)
```

### Verify readiness from inside the container
```bash
python3 -c "from gateway.platforms.sms import check_sms_requirements; print(check_sms_requirements())"
# Returns True when TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and aiohttp are all present
```

### Network-mode considerations

**host network mode** (`network_mode: host` in docker-compose.yml):
The SMS webhook binds directly to the host's network interfaces. Port exposure
in docker-compose.yml is irrelevant — no docker-proxy is involved. The webhook
listener's bind address (`SMS_WEBHOOK_HOST`) maps directly to the host interface:
- `127.0.0.1` → localhost only (good for SSH-tunneled access)
- `0.0.0.0` → all host interfaces (reachable from outside; secure with UFW)
- No docker-proxy routing, no port mapping needed

**bridged network mode** (default Docker networking):
Ports must be exposed in docker-compose.yml AND `SMS_WEBHOOK_HOST` must be
`0.0.0.0` (not 127.0.0.1) so Docker's proxy can forward external traffic to
the container IP. Outbound SMS (Twilio REST API) works regardless — only
inbound webhook delivery is affected.

## 2. Install Missing Python Dependencies

### Check first — many deps are now in-image
Recent hermes-agent Docker images include `aiohttp` and other common gateway
dependencies. Verify before installing:

```bash
docker exec hermes-agent python3 -c "import aiohttp; print(aiohttp.__version__)"
# If this prints a version and no error, skip the apt install step below
```

The Docker image is Debian-based with an **externally managed** Python — `pip install`
is blocked. Use `apt` instead:

```bash
# Find the Debian package name
docker exec hermes-agent apt-cache search python3-aiohttp

# Install it
docker exec hermes-agent apt-get install -y -qq python3-aiohttp

# Verify
docker exec hermes-agent python3 -c "import aiohttp; print(aiohttp.__version__)"
```

Common packages:
- `python3-aiohttp` — async HTTP (needed by SMS, WhatsApp webhook adapters)
- `python3-lxml` — XML parsing
- `python3-dnspython` — DNS lookups

## 3. Persist the Install Across Restarts

The named volume at `/opt/data` survives restarts. Add the install check to the
entrypoint wrapper so it runs on every boot:

```bash
# Find the volume mount point on the host
docker volume inspect hermes-data | grep Mountpoint

# Edit entrypoint-wrapper.sh (create it if it doesn't exist)
# Add BEFORE the `exec` line:
python3 -c "import aiohttp" 2>/dev/null || apt-get install -y -qq python3-aiohttp 2>/dev/null
```

Full entrypoint wrapper template:
```bash
#!/bin/bash
# Fix /root permissions before dropping privileges
chmod 755 /root 2>/dev/null || true
# Install deps for gateway platforms
python3 -c "import aiohttp" 2>/dev/null || apt-get install -y -qq python3-aiohttp 2>/dev/null
exec /opt/hermes/docker/entrypoint.sh "$@"
```

## 4. Add Env Vars and Ports

Add the platform's env vars to the `.env` file. The path depends on your setup:

- **Docker**: add to the host `.env` file passed via `--env-file` or referenced
  in docker-compose.yml's `env_file:` directive
- **Container-internal (bind-mount)**: if `~/.hermes/.env` is bind-mounted to
  `/opt/data/.env`, you can write directly to `/opt/data/.env` from inside the
  container and changes persist on the host

### Ports (host network mode — `network_mode: host`)
No docker-compose.yml port changes needed. The webhook binds directly to the
host interface specified by `SMS_WEBHOOK_HOST`. Use `127.0.0.1` to stay
localhost-only (access via SSH tunnel) or `0.0.0.0` to make it reachable on
the public interface (secure with UFW).

### Ports (bridged network mode — default Docker)
Expose the port in docker-compose.yml:
```yaml
ports:
  - "0.0.0.0:8080:8080"   # SMS webhook
```
For webhook-based platforms, set `SMS_WEBHOOK_HOST=0.0.0.0` (NOT 127.0.0.1)
so Docker's proxy can forward external traffic to the container's eth0 IP.

## 5. Restart CORRECTLY

**DO NOT use `docker compose restart`** — it reuses the container's original
environment snapshot and won't pick up new `.env` variables. Use:

```bash
docker compose up -d hermes-agent
```

This detects the config change and recreates the container with fresh env vars.

## 6. Verify

```bash
# Check container picks up env vars
docker exec hermes-agent env | grep TWILIO

# Check gateway log for platform connection
tail -20 /var/lib/docker/volumes/hermes-data/_data/logs/gateway.log | grep sms

# Should see: "✓ sms connected" and "Gateway running with N platform(s)"

# Test webhook port (for webhook-based platforms)
curl -s http://localhost:8080/health
```

## Pitfalls

- **`network_mode: host` changes everything**: Port exposure in docker-compose.yml
  is irrelevant. Webhook bind addresses map directly to host interfaces. No
  docker-proxy involved. Outbound connections use the host's network directly.
  The gateway log file path may differ from bridged-mode setups.
- **Container-internal execution limits**: If you're inside the container
  (not on the VPS host), `docker` commands and `docker exec` are unavailable.
  SSH to the host may also be unavailable (no key). Modify host files via
  bind-mounts (e.g., `/opt/data/.env` → `~/.hermes/.env`) and restart the
  gateway process directly: `pkill -f "hermes gateway run"` (the entrypoint
  wrapper at PID 1 restarts it).
- **`pip` is blocked**: The container uses Debian Python (PEP 668 externally-managed).
  Always use `apt-get install python3-<name>`. `--break-system-packages` works but
  won't survive restarts unless persisted.
- **`docker compose restart` ignores env_file changes**: It keeps the env snapshot
  from container creation time. Use `up -d` to recreate.
- **127.0.0.1 binding breaks Docker port forwarding** (bridged mode only): The
  docker-proxy forwards to the container's eth0 IP, not 127.0.0.1. Webhook
  listeners must bind to `0.0.0.0`. Does NOT apply to `network_mode: host`.
- **apt installs are ephemeral without entrypoint wrapper**: Each container
  recreate wipes them. The `hermes-data` named volume persists, so anything
  in the entrypoint wrapper on the volume survives.
- **Port exposure order matters** (bridged mode): Port changes in docker-compose.yml
  are only applied on `up`, not `restart`.
- **Gateway log goes to a file**: Console output (`docker logs`) only shows the
  startup banner. Real platform connection logs are in
  `/opt/data/logs/gateway.log` (accessible via the named volume).
- **A2P 10DLC blocks US SMS even for Twilio trial accounts**: Error `30034` —
  "US A2P 10DLC - Message from an Unregistered Number". Twilio will receive
  inbound SMS but refuse ALL outbound SMS to US numbers. Registration as a
  Sole Proprietor takes 1-3 business days and may involve fees. For personal
  use, Discord or other IP-based messaging platforms are simpler alternatives.
- **Bind-mount file operations**: Files bind-mounted into the container (e.g.,
  `~/.hermes/.env` → `/opt/data/.env`) may show "Device or resource busy" when
  using `sed -i`. Use a write-to-temp-then-mv pattern, or use the `write_file`
  / `patch` tools which handle atomic writes through the skill_manage API.
  Direct append (`>>`) works but partial writes can corrupt. For bulk changes,
  read the file content, modify in memory, then overwrite atomically.
- **Twilio credentials are the only blocker**: The SMS adapter code is already
  in the image. aiohttp is included in recent images. The entire platform
  auto-enables when the three required env vars are present — no code changes,
  no config.yaml edits, no dependency installation needed for current images.

## Platform: Slack

Slack auto-enables when `SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN` are set.
Socket Mode is used (no inbound webhook URL needed).

### Env vars
```
SLACK_BOT_TOKEN=***       # OAuth & Permissions page
SLACK_APP_TOKEN=***       # App-Level Tokens page (must have connections:write scope)
SLACK_ALLOWED_USERS=U0B0...    # comma-separated Slack user IDs (optional)
```

**⚠️ Do NOT set `SLACK_CLIENT_ID` or `SLACK_CLIENT_SECRET` in `.env` unless
using HTTP-based OAuth.** When both env vars are present, slack_bolt's
`AsyncApp.__init__` auto-creates `AsyncOAuthSettings` which discards the bot
token (`self._token = None`) and forces OAuth authorization — causing
`AsyncMultiTeamsAuthorization: AuthorizeResult not found` errors. Socket Mode
only needs Bot Token + App Token. See `references/slack-diagnostics.md` for
the full diagnostic matrix including this pitfall.

### Troubleshooting
See `references/slack-diagnostics.md` for the full diagnostic matrix — token
validation commands, Socket Mode failure patterns, the OAuth-env-var conflict,
and the HTTP 200 vs 401 flowchart.
