# rclone Headless OAuth on VPS

## The Problem

When setting up rclone with Google Drive on a headless VPS, the user may provide an OAuth authorization code they retrieved from a browser on their laptop. **This code is almost always expired** — OAuth codes last only a few minutes, and the copy-paste delay across contexts kills them.

Common failure mode: trying `rclone config create` interactively, trying to exchange the code via Python with different redirect URIs, or waiting on `rclone authorize drive --auth-no-open-browser` (which still requires a browser to complete — it just doesn't auto-open it). All of these waste time.

## The Correct Approaches

### Option A — Ask for the `rclone authorize` token blob

Have the user run this on their **laptop** (which has a browser):

```bash
rclone authorize drive
```

This produces a JSON blob like:
```json
{"access_token":"ya29....","token_type":"Bearer","refresh_token":"1//...","expiry":"2026-06-03T14:00:00Z"}
```

Write it straight into the rclone config:

```bash
cat > /root/.config/rclone/rclone.conf << 'EOF'
[gdrive_personal]
type = drive
scope = drive
client_id = <from existing token>
client_secret = <from existing token>
token = <paste the blob from rclone authorize>
EOF
```

The `rclone authorize` output contains the `refresh_token` — this is what makes it persistent. OAuth codes (the `4/0AeoWuM8...` format from the browser URL) do NOT contain a refresh token and cannot be used for persistent auth.

### Option B — Copy the user's existing rclone.conf

If rclone already works on the user's laptop, just ask for their `~/.config/rclone/rclone.conf` contents. Write it directly to the VPS — no auth flow needed.

### Option C — Extract credentials from Hermes' Google token

If `/root/.hermes/google_token.json` exists, it contains `client_id` and `client_secret` that can be reused for rclone. But the token's `scope` field determines what APIs it works with — a Gmail-only token won't work for Drive.

## Anti-Patterns (DO NOT DO)

- ❌ `rclone config create gdrive_personal drive scope drive` — interactive, opens browser, will timeout headless
- ❌ Trying multiple redirect URIs to exchange an OAuth code — if the first one fails, the code is dead
- ❌ Using the OAuth code as an `access_token` directly — it's an authorization code, not a token
- ❌ `rclone config token '{"access_token":"4/0AeoWuM8..."}'` — OAuth codes are not access tokens
- ❌ Waiting on `rclone authorize drive --auth-no-open-browser` — it still needs a browser to complete the flow, it just won't auto-open it

## Quick Verification

After writing the config, verify immediately:

```bash
rclone lsf gdrive_personal:  # List root
rclone about gdrive_personal:  # Check quota/health
```

If listing works but about fails, the scope is too narrow (e.g., `drive.file` vs `drive`).
