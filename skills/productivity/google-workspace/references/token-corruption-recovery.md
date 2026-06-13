# Token Corruption Recovery

Sometimes the Google OAuth token file (`~/.hermes/google_token.json`) exists but is missing critical fields like `client_id`, `client_secret`, or `refresh_token`. This causes the `setup.py --check` command to report `TOKEN_CORRUPT`.

## Symptoms

Running `setup.py --check` outputs:
```
TOKEN_CORRUPT: Authorized user info was not in the expected format, missing fields client_id, client_secret, refresh_token.
```

## Recovery Steps

1. **Delete the corrupt token file** (optional but recommended):
   ```bash
   rm ~/.hermes/google_token.json
   ```

2. **Re-run the OAuth flow** using the standard Google Workspace setup:
   ```bash
   cd ~/.hermes/skills/productivity/google-workspace
   python3 scripts/setup.py --client-secret ~/.hermes/google_client_secret.json
   python3 scripts/setup.py --auth-url
   ```
   Visit the printed URL, authorize the app, and copy the redirect URL or auth code.

3. **Exchange the auth code**:
   ```bash
   python3 scripts/setup.py --auth-code <CODE_FROM_URL>
   ```

4. **Verify** the token is now valid:
   ```bash
   python3 scripts/setup.py --check
   ```
   Should output `AUTHENTICATED: Token valid at ...`

## Prevention

- Ensure the token file always contains a `refresh_token`. If you manually edit the token file, preserve all fields from the original OAuth response.
- The token file is shared across all Hermes profiles; avoid deleting it unless you intend to re-authenticate for all profiles.
