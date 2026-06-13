---
name: google-workspace
description: Gmail, Calendar, Drive, Contacts, Sheets, and Docs integration for Hermes. Uses Hermes-managed OAuth2 setup, prefers the Google Workspace CLI (`gws`) when available for broader API coverage, and falls back to the Python client libraries otherwise.
version: 1.0.0
author: Nous Research
license: MIT
metadata:
  hermes:
    tags: [Google, Gmail, Calendar, Drive, Sheets, Docs, Contacts, Email, OAuth]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [himalaya]
---

# Google Workspace

Gmail, Calendar, Drive, Contacts, Sheets, and Docs — through Hermes-managed OAuth and a thin CLI wrapper. When `gws` is installed, the skill uses it as the execution backend for broader Google Workspace coverage; otherwise it falls back to the bundled Python client implementation.

## Token Location (CRITICAL)

The OAuth token is **always** at `/root/.hermes/google_token.json` — NOT at `$HERMES_HOME/google_token.json`. This is because profiles share a single OAuth token. The profile-aware `HERMES_HOME` (e.g., `/root/.hermes/profiles/detoxxx`) will NOT contain the token. Always hardcode `/root/.hermes/google_token.json` in scripts or use `os.path.expanduser("~/.hermes/google_token.json")` if running outside a profile context.

## References

- `references/gmail-search-syntax.md` — Gmail search operators (is:unread, from:, newer_than:, etc.)
- `references/drive-download-workaround.py` — Download text files from Drive (google_api.py only has search)
- `references/recursive-workspace-pull.md` — Full recursive folder download with content-type routing (Google Docs export, binary vs text handling)
- `references/drive-upload.md` — Upload files to Drive using stored OAuth token `references/recursive-workspace-pull.md` — Full recursive folder download with content-type routing (Google Docs export, binary vs text handling)
- `references/drive-upload.md` — Upload files to Drive using stored OAuth token
- `references/service-account-pattern.md` — Service account bootstrap: auth, list, download, modify, pitfalls
- `references/check-token-freshness.md` — Diagnostic procedure for distinguishing auth states (see Scripts section below)
- `references/drive-recursive-download.md` — Recursive folder download with mime-type routing, export vs download, and pitfall notes
- `references/token-corruption-recovery.md` — Recovery steps when token file is missing critical fields (client_id, client_secret, refresh_token)

## Drive — Recursive Download

`google_api.py drive search` only finds files — it cannot list folders or download content. For bulk workspace mirroring, use the recursive download pattern in `references/drive-recursive-download.md`.

Key pitfalls:
- **Google Docs/Slides/Sheets must be EXPORTED** (`files().export()`), not downloaded (`files().get_media()`). Downloading a Docs file returns HTTP 403.
- **`~/` path trap**: When `HERMES_HOME` is set to a profile dir, `~` expands to the profile, not `/root`. Always use absolute `/root/.hermes/google_token.json` for the token path.
- **Filter temp files**: Skip `~WRL*.tmp`, `~$*` files — they're Word lock artifacts.

## Scripts

- `scripts/setup.py` — OAuth2 setup (run once to authorize)
- `scripts/google_api.py` — compatibility wrapper CLI. It prefers `gws` for operations when available, while preserving Hermes' existing JSON output contract.
- `scripts/check_token_freshness.py` — Token freshness diagnostic with expiry tracking. Use instead of `setup.py --check` when `REFRESH_FAILED` occurs and you need to distinguish "expired" vs "revoked" errors.

### Scripts — check_token_freshness.py

This diagnostic script goes beyond `setup.py --check` to provide granular error reporting:

- Reports token expiry time and remaining validity
- Distinguishes between "NOT_AUTHENTICATED", "TOKEN_CORRUPT", "REFRESH_FAILED", "UNKNOWN_ERROR"
- Warns about path migration after VPS/container changes

**Use it when:**

```bash
$GSETUP --check  # Reports REFRESH_FAILED — need more detail?
python3 ~/.hermes/skills/productivity/google-workspace/scripts/check_token_freshness.py
```

**Output interpretation:**

| Status | Meaning | Action |
|--------|---------|--------|
| `AUTHENTICATED` | Token valid, Drive access confirmed | Ready to use |
| `NOT_AUTHENTICATED` | No token file found | Run setup Steps 2-5 |
| `TOKEN_CORRUPT` | Invalid JSON or missing fields | `rm ~/.hermes/google_token.json` then redo Steps 3-5 |
| `REFRESH_FAILED` | Token expired or revoked | Re-run `--auth-url` and complete new exchange |
| `UNKNOWN_ERROR` | Other error | Include error message in troubleshooting |

## Bulk Downloads — Prefer WebUI

For large folder downloads (50+ files, multi-GB), programmatic recursive download via the Drive API is slow and gets interrupted easily. **Prefer the WebUI Files panel** for bulk Drive → workspace transfers. Navigate to the workspace in WebUI, use the Drive integration to select and download folders directly.

Only use programmatic download (via `scripts/google_api.py` or the `drive-download-workaround.py` reference) for single files or small batches where WebUI isn't practical.