# Google Drive File Download — Inline Python with OAuth

Reliable pattern for downloading files from Google Drive using the stored OAuth
Desktop token. Use this when `google_api.py drive search` finds your files but
there's no built-in download command (the GAPI CLI only supports `drive search`).

## Prerequisites

- OAuth token at `/root/.hermes/google_token.json` (key: `token`, not `access_token`)
- OAuth client secret at `/root/client_secret_339939932247-mfmdg4cupg62nuectocd9g7tcq9g715h.apps.googleusercontent.com.json`
- `google-api-python-client` and `google-auth-oauthlib` installed

## Pattern — Download by File ID

```python
import json, os, io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Load OAuth token
with open('/root/.hermes/google_token.json') as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data['token'],
    refresh_token=token_data.get('refresh_token'),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=token_data.get('client_id',
        '339939932247-mfmdg4cupg62nuectocd9g7tcq9g715h.apps.googleusercontent.com'),
    client_secret=token_data.get('client_secret', '')
)

service = build('drive', 'v3', credentials=creds)

# Download one or more files
files = {
    'FILE_ID_HERE': '/opt/hermes/detoxxx_v2/output_filename.md',
    # add more as needed
}

for file_id, dest_path in files.items():
    # Optional: get metadata first
    meta = service.files().get(fileId=file_id, fields='name,size,mimeType').execute()

    # Download media
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    content = fh.getvalue().decode('utf-8')
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'w') as f:
        f.write(content)

    print(f"{meta['name']}: {len(content)} chars, {content.count(chr(10))} lines → {dest_path}")
```

## Pattern — Search then Download

Combine with the GAPI CLI for search:

```bash
# 1. Search for the file
cd /opt/data/skills/productivity/google-workspace
python3 scripts/google_api.py drive search "filename keywords" --max 5

# 2. Copy the file ID from the JSON output, then use the download pattern above
```

## Pitfalls

- **Token key name:** The stored token uses key `'token'`, NOT `'access_token'`.
  Using the wrong key name produces opaque 401 errors.
- **Service account fallback:** The service account CAN download files (it has
  read access), but CANNOT create new files (storageQuotaExceeded). Always use
  OAuth for create/delete operations.
- **Large files:** For files >10MB, `get_media()` may need chunked download with
  progress tracking. The pattern above uses `MediaIoBaseDownload` which handles
  chunking automatically.
- **OAuth token expired — fallback to local cache:** When the token produces `RefreshError: invalid_grant`, do not retry — fall back to the local file cache at `/opt/hermes/detoxxx_v2/`. The master handbook and most section files are kept there. For files that exist ONLY on Drive, the service account at `/root/.hermes/google_service_account.json` can download from folders explicitly shared with it (read-only — cannot create). For files not shared with the SA and with no local cache, the user must re-authenticate OAuth manually.
